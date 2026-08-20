import uuid

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
)
from database.qdrant_client_manager import client
from database.collection_setup import create_collection_if_missing
from common.collection_utils import (
    get_cache_collection_name,
)
from configuration.constants import (
    METADATA_BUSINESS_ID,
    METADATA_COURSE_ID,
)
from common.logger import logger
from common.custom_exceptions import DatabaseException

# ==========================================================
# Ensure Cache Collection
# ==========================================================

def ensure_cache_collection(
    business_id: str,
) -> str:
    """
    Return the cache collection for a business and create it
    if it does not already exist.
    """

    collection_name = get_cache_collection_name(
        business_id,
    )

    create_collection_if_missing(
        collection_name,
    )

    return collection_name


# ==========================================================
# Search Cache
# ==========================================================

def search_cache(
    *,
    query_embedding: list[float],
    business_id: str,
    course_id: str,
    limit: int = 1,
):
    """
    Search the semantic answer cache for a specific
    business and course.
    """

    collection_name = ensure_cache_collection(
        business_id,
    )

    try:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key=METADATA_COURSE_ID,
                    match=MatchValue(
                        value=course_id,
                    ),
                ),
            ],
        )

        result = client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=limit,
        )

        logger.info(
            "Cache search returned %d result(s).",
            len(result.points),
        )

        return result.points

    except Exception as ex:
        logger.exception(
            "Cache search failed: %s",
            ex,
        )

        raise DatabaseException(
            "Unable to search cache.",
        ) from ex


# ==========================================================
# Save Cache
# ==========================================================

def save_cache(
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
    Store an answer in the business-specific semantic cache.
    """

    collection_name = ensure_cache_collection(
        business_id,
    )

    logger.info(
        "Cache saved for question: %s",
        question,
    )

    try:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "question": question,
                "context": context,
                "answer": answer,

                METADATA_BUSINESS_ID: business_id,
                METADATA_COURSE_ID: course_id,

                "document_id": documentPayload.get(
                    "document_id",
                ),
                "title": documentPayload.get(
                    "title",
                ),
                "document_type": documentPayload.get(
                    "document_type",
                ),
                "tag": documentPayload.get(
                    "tag",
                ),
                "summary": documentPayload.get(
                    "summary",
                ),
                "source": documentPayload.get(
                    "source",
                ),
                "page": documentPayload.get(
                    "page",
                ),
            },
        )

        client.upsert(
            collection_name=collection_name,
            points=[point],
        )

        logger.info(
            "Answer cached successfully.",
        )

    except Exception as ex:
        logger.exception("Failed to save cache: %s", ex)
        raise DatabaseException("Unable to save cache.") from ex