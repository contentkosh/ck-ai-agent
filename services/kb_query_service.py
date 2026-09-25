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
) -> QueryResponse:
    total_start = time.perf_counter()

    try:
        logger.info(
            QUERY_RECEIVED_LOG,
            query,
        )
        logger.info(
            "Query processing started. Business ID=%s | Course IDs=%s",
            business_id,
            course_ids,
        )

        embedding_start = time.perf_counter()

        logger.info(
            "Query embedding generation started.",
        )

        queryEmbedding = get_embedding_model().encode(query).tolist()

        logger.info(
            "Query embedding generation completed. Dimensions=%d | duration=%.4fs",
            len(queryEmbedding),
            time.perf_counter() - embedding_start,
        )

        cache_start = time.perf_counter()

        logger.info(
            "Cache lookup started.",
        )

        cached = get_cached_answer(
            query_embedding=queryEmbedding,
            business_id=business_id,
            course_ids=course_ids,
        )

        cache_duration = time.perf_counter() - cache_start

        if cached:
            logger.info(
                "Cache hit. Returning cached answer.",
            )
            logger.info(
                "Cache lookup completed. duration=%.4fs",
                cache_duration,
            )
            logger.info(
                "Query completed successfully from cache. total=%.4fs",
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
            "Cache miss. Continuing with Knowledge Base retrieval.",
        )
        logger.info(
            "Cache lookup completed. duration=%.4fs",
            cache_duration,
        )

        retrieval_start = time.perf_counter()

        logger.info(
            "Qdrant retrieval started. Limit=%d",
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
            "Qdrant retrieval completed. duration=%.4fs",
            retrieval_duration,
        )

        if not searchResults:
            logger.warning(
                NO_RELEVANT_CHUNKS_LOG,
            )
            logger.info(
                "Query completed without relevant chunks. total=%.4fs",
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
                "[RETRIEVAL] Chunk %d | score=%.4f | source=%s | page=%s",
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
            "Context building started. Chunks=%d",
            len(searchResults),
        )

        contextText = build_context(searchResults)

        logger.info(
            "Context building completed. Characters=%d | duration=%.4fs",
            len(contextText),
            time.perf_counter() - context_start,
        )

        prompt_start = time.perf_counter()

        logger.info(
            "Prompt building started.",
        )

        prompt = build_prompt(
            context=contextText,
            query=query,
        )

        logger.info(
            "Prompt building completed. Characters=%d | duration=%.4fs",
            len(prompt),
            time.perf_counter() - prompt_start,
        )

        llm_start = time.perf_counter()

        logger.info(
            "Knowledge Base LLM generation started.",
        )

        try:
            llmResponse = get_llm().invoke(prompt)
        except Exception as exception:
            logger.exception(
                "%s: %s",
                LLM_INVOCATION_FAILED_LOG,
                exception,
            )
            raise LLMResponseException() from exception

        logger.info(
            "Knowledge Base LLM generation completed. Response characters=%d | duration=%.4fs",
            len(llmResponse.content),
            time.perf_counter() - llm_start,
        )

        answer = llmResponse.content.strip()

        if ANSWER_NOT_FOUND_MESSAGE.lower() in answer.lower():
            logger.info(
                "LLM returned the configured no-answer response.",
            )
            logger.info(
                "Query completed without an answer. total=%.4fs",
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
            "Answer generated successfully. Characters=%d",
            len(answer),
        )

        cache_start = time.perf_counter()

        logger.info(
            "Cache write started.",
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
            "Cache write completed. duration=%.4fs",
            time.perf_counter() - cache_start,
        )

        logger.info(
            "Query completed successfully. total=%.4fs",
            time.perf_counter() - total_start,
        )

        return QueryResponse.from_payload(
            answer=answer,
            payload=documentPayload,
        )

    except LLMResponseException:
        logger.info(
            "Query failed during LLM processing. total=%.4fs",
            time.perf_counter() - total_start,
        )
        raise
    except KnowledgeBaseException:
        logger.info(
            "Query failed during Knowledge Base processing. total=%.4fs",
            time.perf_counter() - total_start,
        )
        raise
    except Exception as exception:
        logger.exception(
            CHAT_SERVICE_FAILED_LOG,
            exception,
        )
        logger.info(
            "Query failed unexpectedly. total=%.4fs",
            time.perf_counter() - total_start,
        )
        raise KnowledgeBaseException(
            CHAT_SERVICE_ERROR_MESSAGE,
        ) from exception
