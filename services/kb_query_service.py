# ==========================================================
# Knowledge Base Chat Service
# Handles question answering by generating embeddings,
# retrieving relevant document chunks, and using the LLM
# to produce context-aware responses.
# ==========================================================

from typing import List

from dotenv import load_dotenv
from services.cache_service import (
    get_cached_answer,
    cache_answer,
)
from configuration.context import KNOWLEDGE_BASE_QA_PROMPT
from common.logger import logger
from services.llmlingua_service import compress_context
from common.embedding_client import get_embedding_model
from exceptions.knowledge_base_exception import (KnowledgeBaseException,)
from common.llm_client import get_llm
from configuration.config import SEARCH_LIMIT
from configuration.constants import (
    CHAT_SERVICE_FAILED_LOG,
    LLM_INVOCATION_FAILED_LOG,
    METADATA_SOURCE,
    METADATA_TEXT,
    NO_RELEVANT_CHUNKS_LOG,
    QUERY_RECEIVED_LOG,
    RETRIEVED_CHUNKS_LOG,
    TOP_MATCHING_SOURCE_LOG,
)
from configuration.error_constants import(
    ANSWER_NOT_FOUND_MESSAGE,
    CHAT_SERVICE_ERROR_MESSAGE,
)
from dto.response_dto import QueryResponse
from exceptions.llm_exception import LLMResponseException
from repositories.kb_repository import searchChunks
from exceptions.contentkosh_exception import (ContentKoshException,)
from exceptions.qdrant_exception import (QdrantConnectionException,)

load_dotenv()

# ==========================================================
# Build Context
# ==========================================================

def build_context(
    searchResults: List,
) -> str:
    """
    Combine retrieved chunks into a single context string.
    """
    return "\n".join(
        searchResult.payload.get(
            METADATA_TEXT,
            "",
        )
        for searchResult in searchResults
    )

# ==========================================================
# Build Prompt
# ==========================================================
from configuration.context import KNOWLEDGE_BASE_QA_PROMPT

def build_prompt(
    *,
    context: str,
    query: str,
) -> str:
    """
    Build the LLM prompt.
    """
    return KNOWLEDGE_BASE_QA_PROMPT.format(
        context=context,
        query=query,
    )

# ==========================================================
# Ask Question
# ==========================================================

def ask_question(
    query: str,
    business_id: str,
    course_id: str,
) -> QueryResponse:
    """
    Search the Knowledge Base and generate an answer.
    """
    try:
        logger.info(
            QUERY_RECEIVED_LOG,
            query,
        )

        queryEmbedding = (
            get_embedding_model()
            .encode(query)
            .tolist()
        )

        # --------------------------------------------------
        # Check Semantic Cache
        # --------------------------------------------------

        cached = get_cached_answer(
            query_embedding=queryEmbedding,
            business_id=business_id,
            course_id=course_id,
        )

        if cached:
            logger.info(
                "Returning cached answer.",
            )

            return QueryResponse(
                answer=cached.get("answer"),
                document_id=cached.get("document_id"),
                title=cached.get("title"),
                document_type=cached.get("document_type"),
                tag=cached.get("tag"),
                summary=cached.get("summary"),
                source=cached.get("source"),
                page=cached.get("page"),
            )

        # --------------------------------------------------
        # Search Knowledge Base
        # --------------------------------------------------

        try:
            searchResults = searchChunks(
                queryEmbedding=queryEmbedding,
                businessId=business_id,
                courseId=course_id,
                limit=SEARCH_LIMIT,
            )

        except ContentKoshException as exception:
            logger.exception(
                CHAT_SERVICE_FAILED_LOG,
                exception,
            )

            if isinstance(
                exception.cause,
                QdrantConnectionException,
            ):
                raise exception.cause

            raise KnowledgeBaseException() from exception

        # --------------------------------------------------
        # No Relevant Chunks
        # --------------------------------------------------

        if not searchResults:
            logger.warning(
                NO_RELEVANT_CHUNKS_LOG,
            )

            return QueryResponse(
                answer=ANSWER_NOT_FOUND_MESSAGE,
                document_id=None,
                title=None,
                document_type=None,
                tag=None,
                summary=None,
                source=None,
                page=None,
            )

        logger.info(RETRIEVED_CHUNKS_LOG,len(searchResults))

        # --------------------------------------------------
        # Build Context
        # --------------------------------------------------

        contextText = build_context(
            searchResults,
        )

        # --------------------------------------------------
        # Compress Context using LLMLingua
        # --------------------------------------------------

        compressedContext = compress_context(
            context=contextText,
            query=query,
        )

        documentPayload = (
            searchResults[0].payload or {}
        )

        logger.info(
            TOP_MATCHING_SOURCE_LOG,
            documentPayload.get(
                METADATA_SOURCE,
            ),
        )

        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        prompt = build_prompt(
            context=compressedContext,
            query=query,
        )

        try:
            llmResponse = get_llm().invoke(
                prompt,
            )

        except Exception as exception:
            logger.exception(
                "%s: %s",
                LLM_INVOCATION_FAILED_LOG,
                exception,
            )
            raise LLMResponseException() from exception

        answer = llmResponse.content.strip()

        if ANSWER_NOT_FOUND_MESSAGE.lower() in answer.lower():
            return QueryResponse(
                answer=ANSWER_NOT_FOUND_MESSAGE,
                document_id=None,
                title=None,
                document_type=None,
                tag=None,
                summary=None,
                source=None,
                page=None,
            )

        # --------------------------------------------------
        # Save to Semantic Cache
        # --------------------------------------------------

        cache_answer(
            question=query,
            embedding=queryEmbedding,
            context=contextText,
            answer=answer,
            documentPayload=documentPayload,
            business_id=business_id,
            course_id=course_id,
        )

        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return QueryResponse.from_payload(
            answer=answer,
            payload=documentPayload,
        )

    except LLMResponseException:
        raise

    except KnowledgeBaseException:
        raise

    except Exception as exception:
        logger.exception(CHAT_SERVICE_FAILED_LOG,exception)
        raise KnowledgeBaseException(
            CHAT_SERVICE_ERROR_MESSAGE,
        ) from exception