from dto.response_dto import CacheResponse
from repositories.cache_repository import (
    search_cache,
    save_cache,
)

from configuration.config import (
    CACHE_ENABLED,
    CACHE_SIMILARITY_THRESHOLD,
)

from configuration.constants import (
    INVALID_CACHE_RESPONSES,
)

from common.logger import logger


# ==========================================================
# Search Semantic Cache
# ==========================================================

def get_cached_answer(
    query_embedding: list[float],
    business_id: str,
    course_id: str,
):
    """
    Return a cached answer if a similar question exists
    for the specified business and course.
    """

    if not CACHE_ENABLED:
        return None

    results = search_cache(
        query_embedding=query_embedding,
        business_id=business_id,
        course_id=course_id,
    )

    if not results:
        logger.info(
            "Cache Miss - No similar question found."
        )
        return None

    result = results[0]

    if result is None:
        logger.info(
            "Cache Miss - Invalid result from cache search."
        )
        return None

    score = result.score

    logger.info(
        "Cache similarity score: %.3f",
        score,
    )

    if score >= CACHE_SIMILARITY_THRESHOLD:
        logger.info(
            "Cache Hit",
        )

        return CacheResponse(
            answer=result.payload.get("answer"),
            document_id=result.payload.get("document_id"),
            title=result.payload.get("title"),
            document_type=result.payload.get("document_type"),
            tag=result.payload.get("tag"),
            summary=result.payload.get("summary"),
            source=result.payload.get("source"),
            page=result.payload.get("page"),
            similarity_score=score,
        )

    logger.info(
        "Cache Miss",
    )

    return None


# ==========================================================
# Validate Cache Entry
# ==========================================================

def should_cache(
    answer: str,
) -> bool:
    """
    Decide whether an answer should be cached.
    """

    if not answer:
        return False

    answer = answer.strip()

    if not answer:
        return False

    for text in INVALID_CACHE_RESPONSES:
        if text.lower() in answer.lower():
            return False

    return True


# ==========================================================
# Save Cache
# ==========================================================

def cache_answer(
    *,
    question: str,
    embedding: list[float],
    context: str,
    answer: str,
    documentPayload: dict,
    business_id: str,
    course_id: str,
):
    """
    Store a successful answer in the business-specific
    and course-specific semantic cache.
    """

    if not CACHE_ENABLED:
        return

    if not should_cache(answer):
        logger.info(
            "Answer not cached.",
        )
        return

    save_cache(
        question=question,
        embedding=embedding,
        context=context,
        answer=answer,
        documentPayload=documentPayload,
        business_id=business_id,
        course_id=course_id,
    )