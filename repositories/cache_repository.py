import uuid

from common.collection_utils import get_cache_collection_name
from common.custom_exceptions import DatabaseException
from common.logger import logger
from configuration.config import CACHE_TOP_K
from configuration.constants import (
    METADATA_BUSINESS_ID,
    METADATA_COURSE_ID,
    METADATA_DOCUMENT_ID,
)
from configuration.error_constants import (
    DATABASE_CACHE_CLEAR_ERROR_MESSAGE,
    DATABASE_CACHE_DELETE_ERROR_MESSAGE,
)
from database.collection_setup import create_collection_if_missing
from database.qdrant_client_manager import client
from qdrant_client.models import FieldCondition, Filter, MatchAny, PointStruct


def ensure_cache_collection(
    business_id: str,
) -> str:
    collection_name = get_cache_collection_name(
        business_id,
    )

    logger.info(
        "Ensuring cache collection exists: %s",
        collection_name,
    )

    create_collection_if_missing(
        collection_name,
    )

    logger.info(
        "Cache collection ready: %s",
        collection_name,
    )

    return collection_name


def search_cache(
    *,
    query_embedding: list[float],
    business_id: str,
    course_ids: list[str],
    limit: int = CACHE_TOP_K,
):
    collection_name = ensure_cache_collection(
        business_id,
    )

    try:
        logger.info(
            "Cache Qdrant search started. Collection=%s | limit=%d",
            collection_name,
            limit,
        )

        query_filter = Filter(
            must=[
                FieldCondition(
                    key=METADATA_COURSE_ID,
                    match=MatchAny(
                        any=course_ids,
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
            "Cache Qdrant search completed. Collection=%s | results=%d",
            collection_name,
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


def save_cache(
    *,
    question: str,
    embedding: list[float],
    context: str,
    answer: str,
    documentPayload: dict,
    business_id: str,
    course_ids: list[str],
):
    collection_name = ensure_cache_collection(
        business_id,
    )

    try:
        logger.info(
            "Cache Qdrant write started. Collection=%s",
            collection_name,
        )

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "question": question,
                "context": context,
                "answer": answer,
                METADATA_BUSINESS_ID: business_id,
                METADATA_COURSE_ID: course_ids,
                METADATA_DOCUMENT_ID: documentPayload.get(
                    METADATA_DOCUMENT_ID,
                ),
                "title": documentPayload.get("title"),
                "document_type": documentPayload.get("document_type"),
                "tag": documentPayload.get("tag"),
                "summary": documentPayload.get("summary"),
                "source": documentPayload.get("source"),
                "page": documentPayload.get("page"),
            },
        )

        client.upsert(
            collection_name=collection_name,
            points=[point],
        )

        logger.info(
            "Cache Qdrant write completed successfully. Collection=%s",
            collection_name,
        )

    except Exception as ex:
        logger.exception(
            "Failed to save cache: %s",
            ex,
        )
        raise DatabaseException(
            "Unable to save cache.",
        ) from ex


def delete_cache_for_document(
    *,
    business_id: str,
    course_ids: list[str],
    document_id: str,
) -> bool:
    collection_name = ensure_cache_collection(
        business_id,
    )

    try:
        logger.info(
            "Cache deletion started. Collection=%s | document_id=%s",
            collection_name,
            document_id,
        )

        cache_filter = Filter(
            must=[
                FieldCondition(
                    key=METADATA_COURSE_ID,
                    match=MatchAny(
                        any=course_ids,
                    ),
                ),
                FieldCondition(
                    key=METADATA_DOCUMENT_ID,
                    match=MatchAny(
                        any=[document_id],
                    ),
                ),
            ],
        )

        client.delete(
            collection_name=collection_name,
            points_selector=cache_filter,
        )

        logger.info(
            "Cache entries deleted successfully. Document ID=%s",
            document_id,
        )

        return True

    except Exception as ex:
        logger.exception(
            DATABASE_CACHE_DELETE_ERROR_MESSAGE,
            document_id,
            ex,
        )
        raise DatabaseException(
            DATABASE_CACHE_DELETE_ERROR_MESSAGE,
        ) from ex


def delete_all_cache(
    *,
    business_id: str,
) -> bool:
    collection_name = ensure_cache_collection(
        business_id,
    )

    try:
        logger.info(
            "Full cache deletion started. Collection=%s",
            collection_name,
        )

        client.delete(
            collection_name=collection_name,
            points_selector=Filter(),
        )

        logger.info(
            "All cache entries deleted successfully. Business ID=%s",
            business_id,
        )

        return True

    except Exception as ex:
        logger.exception(
            DATABASE_CACHE_CLEAR_ERROR_MESSAGE,
            business_id,
            ex,
        )
        raise DatabaseException(
            DATABASE_CACHE_CLEAR_ERROR_MESSAGE,
        ) from ex
