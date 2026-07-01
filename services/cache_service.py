from repositories.cache_repository import (
    search_cache,
    save_cache,
)

from configuration.app_settings import (
    CACHE_ENABLED,
    CACHE_SIMILARITY_THRESHOLD,
)

from common.logger import logger


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

    results = search_cache(query_embedding)

    print("\n========== CACHE DEBUG ==========")
    print("Results Found:", len(results))

    if not results:

        logger.info("Cache Miss")

        return None

    result = results[0]

    score = result.score

    print("Similarity Score:", score)

    logger.info(
        "Cache similarity score: %.3f",
        score,
    )

    if score >= CACHE_SIMILARITY_THRESHOLD:

        logger.info("Cache Hit")

        print("CACHE HIT")

        return{
            "answer": result.payload.get("answer"),
            "score": score,
        }

    logger.info("Cache Miss")

    print("CACHE MISS")
    print("================================\n")

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

    invalid_answers = [

        "I don't know",

        "Answer not found",

        "No relevant context found",

    ]

    for text in invalid_answers:

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

):
    """
    Store a successful answer in the cache.
    """

    if not CACHE_ENABLED:

        return

    if not should_cache(answer):

        logger.info(
            "Answer not cached."
        )

        return

    save_cache(

        question=question,

        embedding=embedding,

        context=context,

        answer=answer,

    )