from typing import List

from common.embedding_client import get_embedding_model
from common.llm_client import get_llm
from common.logger import logger
from configuration.config import SEARCH_LIMIT
from configuration.constants import (
    CHAT_SERVICE_FAILED_LOG,
    LLM_INVOCATION_FAILED_LOG,
    METADATA_TEXT,
    NO_RELEVANT_CHUNKS_LOG,
    QUERY_RECEIVED_LOG,
    RETRIEVED_CHUNKS_LOG,
    TOP_MATCHING_SOURCE_LOG,
)
from configuration.context import KNOWLEDGE_BASE_QA_PROMPT
from configuration.error_constants import (
    ANSWER_NOT_FOUND_MESSAGE,
    CHAT_SERVICE_ERROR_MESSAGE,
)
from dto.response_dto import QueryResponse
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.llm_exception import LLMResponseException
from exceptions.qdrant_exception import QdrantConnectionException
from repositories.kb_repository import searchChunks
from services.cache_service import (
    cache_answer,
    get_cached_answer,
)


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


def ask_question(
    query: str,
    business_id: str,
    course_ids: list[str],
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

        cached = get_cached_answer(
            query_embedding=queryEmbedding,
            business_id=business_id,
            course_ids=course_ids,
        )

        if cached:
            logger.info(
                "Returning cached answer.",
            )

            return QueryResponse(
                answer=cached.answer,
                document_id=cached.document_id,
                title=cached.title,
                document_type=cached.document_type,
                tag=cached.tag,
                summary=cached.summary,
                source=cached.source,
                page=cached.page,
            )

        try:
            searchResults = searchChunks(
                queryEmbedding=queryEmbedding,
                businessId=business_id,
                courseIds=course_ids,
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

        logger.info(
            RETRIEVED_CHUNKS_LOG,
            len(searchResults),
        )

        documentPayload = searchResults[0].payload

        logger.info(
            TOP_MATCHING_SOURCE_LOG,
            documentPayload.get("source"),
        )

        contextText = build_context(
            searchResults,
        )

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

        cache_answer(
            question=query,
            embedding=queryEmbedding,
            context=contextText,
            answer=answer,
            documentPayload=documentPayload,
            business_id=business_id,
            course_ids=course_ids,
        )

        return QueryResponse.from_payload(
            answer=answer,
            payload=documentPayload,
        )

    except LLMResponseException:
        raise

    except KnowledgeBaseException:
        raise

    except Exception as exception:
        logger.exception(
            CHAT_SERVICE_FAILED_LOG,
            exception,
        )

        raise KnowledgeBaseException(
            CHAT_SERVICE_ERROR_MESSAGE,
        ) from exception