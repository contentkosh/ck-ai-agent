from common.logger import logger
from configuration.config import CACHE_ENABLED, CACHE_SIMILARITY_THRESHOLD
from configuration.constants import INVALID_CACHE_RESPONSES
from dto.response_dto import CacheResponse
from repositories.cache_repository import save_cache, search_cache


def get_cached_answer(
    query_embedding: list[float],
    business_id: str,
    course_ids: list[str],
):
    if not CACHE_ENABLED:
        logger.info("Cache lookup skipped because cache is disabled.")
        return None

    logger.info(
        "Cache search started. Business ID=%s | Course IDs=%s",
        business_id,
        course_ids,
    )

    results = search_cache(
        query_embedding=query_embedding,
        business_id=business_id,
        course_ids=course_ids,
    )

    if not results:
        logger.info("Cache miss. No similar question found.")
        return None

    result = results[0]

    if result is None:
        logger.info("Cache miss. Invalid result from cache search.")
        return None

    score = result.score

    logger.info(
        "Cache similarity score: %.3f | threshold=%.3f",
        score,
        CACHE_SIMILARITY_THRESHOLD,
    )

    if score >= CACHE_SIMILARITY_THRESHOLD:
        logger.info(
            "Cache hit. Similarity=%.3f",
            score,
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
        "Cache miss. Similarity %.3f is below threshold %.3f.",
        score,
        CACHE_SIMILARITY_THRESHOLD,
    )
    return None


def should_cache(answer: str) -> bool:
    if not answer or not answer.strip():
        logger.info("Answer not cached because it is empty.")
        return False

    answer = answer.strip()

    for text in INVALID_CACHE_RESPONSES:
        if text.lower() in answer.lower():
            logger.info(
                "Answer not cached because it matches an invalid cache response."
            )
            return False

    return True


def cache_answer(
    *,
    question: str,
    embedding: list[float],
    context: str,
    answer: str,
    documentPayload: dict,
    business_id: str,
    course_ids: list[str],
):
    if not CACHE_ENABLED:
        logger.info("Cache write skipped because cache is disabled.")
        return

    if not should_cache(answer):
        return

    logger.info(
        "Cache write started. Business ID=%s | Course IDs=%s",
        business_id,
        course_ids,
    )

    try:
        save_cache(
            question=question,
            embedding=embedding,
            context=context,
            answer=answer,
            documentPayload=documentPayload,
            business_id=business_id,
            course_ids=course_ids,
        )
        logger.info("Cache write completed successfully.")
    except Exception:
        logger.exception("Cache write failed.")
        raise
