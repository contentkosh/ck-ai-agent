from typing import List
import time

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

    Timing for each major stage is logged to the terminal.
    """

    total_start = time.perf_counter()

    try:
        logger.info(
            QUERY_RECEIVED_LOG,
            query,
        )

        # --------------------------------------------------
        # 1. Generate query embedding
        # --------------------------------------------------

        start = time.perf_counter()

        queryEmbedding = get_embedding_model().encode(query).tolist()

        logger.info(
            "[TIMING] Embedding generation: %.4f seconds",
            time.perf_counter() - start,
        )

        # --------------------------------------------------
        # 2. Cache lookup
        # --------------------------------------------------

        start = time.perf_counter()

        cached = get_cached_answer(
            query_embedding=queryEmbedding,
            business_id=business_id,
            course_ids=course_ids,
        )

        logger.info(
            "[TIMING] Cache lookup: %.4f seconds",
            time.perf_counter() - start,
        )

        if cached:
            logger.info(
                "Returning cached answer.",
            )

            logger.info(
                "[TIMING] KB service total (cache hit): %.4f seconds",
                time.perf_counter() - total_start,
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

        # --------------------------------------------------
        # 3. Qdrant retrieval
        # --------------------------------------------------

        start = time.perf_counter()

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

        logger.info(
            "[TIMING] Qdrant retrieval: %.4f seconds",
            time.perf_counter() - start,
        )

        if not searchResults:
            logger.warning(
                NO_RELEVANT_CHUNKS_LOG,
            )

            logger.info(
                "[TIMING] KB service total (no relevant chunks): %.4f seconds",
                time.perf_counter() - total_start,
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

        # --------------------------------------------------
        # 4. Build context
        # --------------------------------------------------

        start = time.perf_counter()

        contextText = build_context(
            searchResults,
        )

        logger.info(
            "[TIMING] Context building: %.4f seconds",
            time.perf_counter() - start,
        )

        # --------------------------------------------------
        # 5. Build prompt
        # --------------------------------------------------

        start = time.perf_counter()

        prompt = build_prompt(
            context=contextText,
            query=query,
        )

        logger.info(
            "[TIMING] Prompt building: %.4f seconds",
            time.perf_counter() - start,
        )

        # --------------------------------------------------
        # 6. LLM generation
        # --------------------------------------------------

        start = time.perf_counter()

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

        logger.info(
            "[TIMING] LLM generation: %.4f seconds",
            time.perf_counter() - start,
        )

        answer = llmResponse.content.strip()

        if ANSWER_NOT_FOUND_MESSAGE.lower() in answer.lower():
            logger.info(
                "[TIMING] KB service total (LLM returned no-answer): %.4f seconds",
                time.perf_counter() - total_start,
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

        # --------------------------------------------------
        # 7. Cache write
        # --------------------------------------------------

        start = time.perf_counter()

        cache_answer(
            question=query,
            embedding=queryEmbedding,
            context=contextText,
            answer=answer,
            documentPayload=documentPayload,
            business_id=business_id,
            course_ids=course_ids,
        )

        logger.info(
            "[TIMING] Cache write: %.4f seconds",
            time.perf_counter() - start,
        )

        # --------------------------------------------------
        # Total service time
        # --------------------------------------------------

        logger.info(
            "[TIMING] KB service TOTAL: %.4f seconds",
            time.perf_counter() - total_start,
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

        logger.info(
            "[TIMING] KB service TOTAL (failed): %.4f seconds",
            time.perf_counter() - total_start,
        )

        raise KnowledgeBaseException(
            CHAT_SERVICE_ERROR_MESSAGE,
        ) from exception
