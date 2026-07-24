# ==========================================================
# Knowledge Base Chat Service
# Handles question answering by generating embeddings,
# retrieving relevant document chunks, and using the LLM
# to produce context-aware responses.
# ==========================================================

from typing import List
from dotenv import load_dotenv
from common.custom_exceptions import DatabaseException
from common.embedding_client import get_embedding_model
from common.llm_client import get_llm
from common.logger import logger
from configuration.config import SEARCH_LIMIT
from configuration.constants import (
    ANSWER_NOT_FOUND_MESSAGE,
    CHAT_SERVICE_ERROR_MESSAGE,
    CHAT_SERVICE_FAILED_LOG,
    LLM_INVOCATION_FAILED_LOG,
    METADATA_SOURCE,
    METADATA_TEXT,
    NO_RELEVANT_CHUNKS_LOG,
    QUERY_RECEIVED_LOG,
    RETRIEVED_CHUNKS_LOG,
    TOP_MATCHING_SOURCE_LOG,
)
from configuration.context import KNOWLEDGE_BASE_QA_PROMPT
from dto.response_dto import QueryResponse
from exceptions.llm_exception import LLMResponseException
from repositories.kb_repository import searchChunks

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
    return "\n\n".join(
        searchResult.payload.get(
            METADATA_TEXT,
            "",
        )
        for searchResult in searchResults
    )

# ==========================================================
# Build Prompt
# ==========================================================

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
) -> QueryResponse:
    """
    Search the Knowledge Base and generate an answer.
    """
    try:
        logger.info(QUERY_RECEIVED_LOG, query)

        # --------------------------------------------------
        # Generate Query Embedding
        # --------------------------------------------------

        queryEmbedding = (
            get_embedding_model()
            .encode(query)
            .tolist()
        )

        # --------------------------------------------------
        # Search Knowledge Base
        # --------------------------------------------------

        searchResults = searchChunks(
            queryEmbedding=queryEmbedding,
            limit=SEARCH_LIMIT,
        )

        if not searchResults:
            logger.warning(NO_RELEVANT_CHUNKS_LOG)

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

        contextText = build_context(searchResults)
        documentPayload = searchResults[0].payload
        logger.info(TOP_MATCHING_SOURCE_LOG,documentPayload.get(
                METADATA_SOURCE,
            ),
        )

        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        prompt = build_prompt(
            context=contextText,
            query=query,
        )

        try:
            llmResponse = get_llm().invoke(
                prompt,
            )
        except Exception as exception:
            logger.exception(
                LLM_INVOCATION_FAILED_LOG,
            )
            raise LLMResponseException() from exception

        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return QueryResponse.from_payload(
            answer=llmResponse.content.strip(),
            payload=documentPayload,
        )

    except LLMResponseException:
        raise

    except Exception as exception:
        logger.exception(CHAT_SERVICE_FAILED_LOG,exception,)
        raise DatabaseException(CHAT_SERVICE_ERROR_MESSAGE,) from exception