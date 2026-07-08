from repositories.cache_repository import (
    search_cache,
    save_cache,
)

from configuration.app_settings import (
    CACHE_ENABLED,
    CACHE_SIMILARITY_THRESHOLD,
)

from configuration.constants import (
    INVALID_CACHE_RESPONSES,
)

from common.logger import logger
from common.custom_exceptions import DatabaseException

from dto.response_dto import CacheResponse


# ==========================================================
# Search Semantic Cache
# ==========================================================

def get_cached_answer(
    query_embedding: list[float],
):
    """
    Return a cached answer if a similar question exists.
    """
    if not CACHE_ENABLED:
        return None
    try:
        cache_results = search_cache(query_embedding)
    except DatabaseException:
        logger.exception("Cache lookup failed.")
        return None
    if not cache_results:
        logger.info("Cache Miss")
        return None
    cached_result = cache_results[0]
    similarity_score = cached_result.score
    logger.info("Cache similarity score: %.3f", similarity_score)
    if similarity_score >= CACHE_SIMILARITY_THRESHOLD:
        logger.info("Cache Hit")
        return CacheResponse(
            answer=cached_result.payload.get("answer"),
            document_id=cached_result.payload.get("document_id"),
            title=cached_result.payload.get("title"),
            document_type=cached_result.payload.get("document_type"),
            tag=cached_result.payload.get("tag"),
            summary=cached_result.payload.get("summary"),
            source=cached_result.payload.get("source"),
            page=cached_result.payload.get("page"),
            similarity_score=similarity_score,
        )
    logger.info("Cache Miss")
    return None


def should_cache(
    answer: str,
) -> bool:
    """
    Decide whether an answer should be cached.
    """
    if not answer:
        return False
    normalized_answer = answer.strip().lower()
    if not normalized_answer:
        return False
    for invalid_response in INVALID_CACHE_RESPONSES:
        if invalid_response.lower() in normalized_answer:
            return False
    return True


# ==========================================================
# Save Cache

# ==========================================================
# Save Cache
# ==========================================================

def cache_answer(
    *,
    question: str,
    embedding: list[float],
    context: str,
    answer: str,
    metadata: dict,
):
    """
    Store a successful answer in the cache.
    """
    if not CACHE_ENABLED:
        return
    if not should_cache(answer):
        logger.info("Answer not cached.")
        return
    try:
        existing_cache = search_cache(embedding)
        if existing_cache:
            similarity_score = existing_cache[0].score
            if similarity_score >= CACHE_SIMILARITY_THRESHOLD:
                logger.info("Duplicate cache entry found. Skipping cache save.")
                return
        save_cache(
            question=question,
            embedding=embedding,
            context=context,
            answer=answer,
            metadata=metadata
        )
    except DatabaseException:
        logger.exception("Failed to save answer in cache.")