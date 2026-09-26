import time
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
    QUERY_EMBEDDING_STARTED_LOG,
    QUERY_EMBEDDING_COMPLETED_LOG,
    CACHE_LOOKUP_STARTED_LOG,
    CACHE_HIT_LOG,
    CACHE_MISS_LOG,
    QDRANT_SEARCH_STARTED_LOG,
    QDRANT_SEARCH_COMPLETED_LOG,
    CONTEXT_BUILD_STARTED_LOG,
    CONTEXT_BUILD_COMPLETED_LOG,
    LLM_GENERATION_STARTED_LOG,
    LLM_GENERATION_COMPLETED_LOG,
    CACHE_WRITE_STARTED_LOG,
    CACHE_WRITE_COMPLETED_LOG,
    CACHE_WRITE_SKIPPED_LOG,
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
from services.cache_service import cache_answer, get_cached_answer


def build_context(searchResults: List) -> str:
    contextParts = []

    for index, searchResult in enumerate(searchResults, start=1):
        payload = searchResult.payload
        source = payload.get("source", "Unknown")
        page = payload.get("page", "Unknown")
        text = payload.get(METADATA_TEXT, "")

        contextParts.append(
            f"--- Retrieved Chunk {index} ---\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{text}"
        )

    return "\n\n".join(contextParts)


def build_prompt(
    *,
    context: str,
    query: str,
) -> str:
    return KNOWLEDGE_BASE_QA_PROMPT.format(
        context=context,
        query=query,
    )


def ask_question(
    query: str,
    business_id: str,
    course_ids: list[str],
    job_id: str,
) -> QueryResponse:
    total_start = time.perf_counter()

    try:
        logger.info(
            QUERY_RECEIVED_LOG,
            query,
        )

        logger.info(
            "Query processing started. job_id=%s Business ID=%s | Course IDs=%s",
            job_id,
            business_id,
            course_ids,
        )

        embedding_start = time.perf_counter()

        logger.info(
            QUERY_EMBEDDING_STARTED_LOG,
            job_id,
        )

        queryEmbedding = get_embedding_model().encode(query).tolist()

        logger.info(
            QUERY_EMBEDDING_COMPLETED_LOG,
            job_id,
        )

        logger.info(
            "Query embedding generation completed. job_id=%s Dimensions=%d | duration=%.4fs",
            job_id,
            len(queryEmbedding),
            time.perf_counter() - embedding_start,
        )

        cache_start = time.perf_counter()

        logger.info(
            CACHE_LOOKUP_STARTED_LOG,
            job_id,
        )

        cached = get_cached_answer(
            query_embedding=queryEmbedding,
            business_id=business_id,
            course_ids=course_ids,
        )

        cache_duration = time.perf_counter() - cache_start

        if cached:
            logger.info(
                CACHE_HIT_LOG,
                job_id,
            )

            logger.info(
                "Cache lookup completed. job_id=%s duration=%.4fs",
                job_id,
                cache_duration,
            )

            logger.info(
                "Query completed successfully from cache. job_id=%s total=%.4fs",
                job_id,
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

        logger.info(
            CACHE_MISS_LOG,
            job_id,
        )

        logger.info(
            "Cache lookup completed. job_id=%s duration=%.4fs",
            job_id,
            cache_duration,
        )

        retrieval_start = time.perf_counter()

        logger.info(
            QDRANT_SEARCH_STARTED_LOG,
            job_id,
        )

        logger.info(
            "Qdrant retrieval started. job_id=%s Limit=%d",
            job_id,
            SEARCH_LIMIT,
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

        retrieval_duration = time.perf_counter() - retrieval_start

        logger.info(
            QDRANT_SEARCH_COMPLETED_LOG,
            job_id,
            len(searchResults),
        )

        logger.info(
            "Qdrant retrieval completed. job_id=%s duration=%.4fs",
            job_id,
            retrieval_duration,
        )

        if not searchResults:
            logger.warning(
                NO_RELEVANT_CHUNKS_LOG,
            )

            logger.info(
                "Query completed without relevant chunks. job_id=%s total=%.4fs",
                job_id,
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

        for index, searchResult in enumerate(searchResults, start=1):
            logger.info(
                "[%s] [RETRIEVAL] Chunk %d | score=%.4f | source=%s | page=%s",
                job_id,
                index,
                searchResult.score,
                searchResult.payload.get("source"),
                searchResult.payload.get("page"),
            )

        documentPayload = searchResults[0].payload

        logger.info(
            TOP_MATCHING_SOURCE_LOG,
            documentPayload.get("source"),
        )

        context_start = time.perf_counter()

        logger.info(
            CONTEXT_BUILD_STARTED_LOG,
            job_id,
        )

        logger.info(
            "Context building started. job_id=%s Chunks=%d",
            job_id,
            len(searchResults),
        )

        contextText = build_context(searchResults)

        logger.info(
            CONTEXT_BUILD_COMPLETED_LOG,
            job_id,
        )

        logger.info(
            "Context building completed. job_id=%s Characters=%d | duration=%.4fs",
            job_id,
            len(contextText),
            time.perf_counter() - context_start,
        )

        prompt_start = time.perf_counter()

        logger.info(
            "[%s] Prompt building started.",
            job_id,
        )

        prompt = build_prompt(
            context=contextText,
            query=query,
        )

        logger.info(
            "[%s] Prompt building completed. Characters=%d | duration=%.4fs",
            job_id,
            len(prompt),
            time.perf_counter() - prompt_start,
        )

        llm_start = time.perf_counter()

        logger.info(
            LLM_GENERATION_STARTED_LOG,
            job_id,
        )

        logger.info(
            "Knowledge Base LLM generation started. job_id=%s",
            job_id,
        )

        try:
            llmResponse = get_llm().invoke(prompt)

        except Exception as exception:
            logger.exception(
                LLM_INVOCATION_FAILED_LOG,
                exception,
            )

            raise LLMResponseException() from exception

        logger.info(
            LLM_GENERATION_COMPLETED_LOG,
            job_id,
        )

        logger.info(
            "Knowledge Base LLM generation completed. job_id=%s Response characters=%d | duration=%.4fs",
            job_id,
            len(llmResponse.content),
            time.perf_counter() - llm_start,
        )

        answer = llmResponse.content.strip()

        if ANSWER_NOT_FOUND_MESSAGE.lower() in answer.lower():
            logger.info(
                "[%s] LLM returned the configured no-answer response.",
                job_id,
            )

            logger.info(
                "Query completed without an answer. job_id=%s total=%.4fs",
                job_id,
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
            "[%s] Answer generated successfully. Characters=%d",
            job_id,
            len(answer),
        )

        cache_start = time.perf_counter()

        logger.info(
            CACHE_WRITE_STARTED_LOG,
            job_id,
        )

        logger.info(
            "Cache write started. job_id=%s",
            job_id,
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

        logger.info(
            CACHE_WRITE_COMPLETED_LOG,
            job_id,
        )

        logger.info(
            "Cache write completed. job_id=%s duration=%.4fs",
            job_id,
            time.perf_counter() - cache_start,
        )

        logger.info(
            "Query completed successfully. job_id=%s total=%.4fs",
            job_id,
            time.perf_counter() - total_start,
        )

        return QueryResponse.from_payload(
            answer=answer,
            payload=documentPayload,
        )

    except LLMResponseException:
        logger.info(
            "Query failed during LLM processing. job_id=%s total=%.4fs",
            job_id,
            time.perf_counter() - total_start,
        )
        raise

    except KnowledgeBaseException:
        logger.info(
            "Query failed during Knowledge Base processing. job_id=%s total=%.4fs",
            job_id,
            time.perf_counter() - total_start,
        )
        raise

    except Exception as exception:
        logger.exception(
            CHAT_SERVICE_FAILED_LOG,
            exception,
        )

        logger.info(
            "Query failed unexpectedly. job_id=%s total=%.4fs",
            job_id,
            time.perf_counter() - total_start,
        )

        raise KnowledgeBaseException(
            CHAT_SERVICE_ERROR_MESSAGE,
        ) from exception
