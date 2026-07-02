import uuid
from typing import Optional

from qdrant_client.models import PointStruct

from database.qdrant_client_manager import client

from configuration.app_settings import (
    CACHE_COLLECTION_NAME,
)

from common.logger import logger
from common.custom_exceptions import DatabaseException


# ==========================================================
# Search Cache
# ==========================================================

def search_cache(
    query_embedding: list[float],
    limit: int = 1,
):
    """
    Search the semantic answer cache.
    """

    try:

        result = client.query_points(

            collection_name=CACHE_COLLECTION_NAME,

            query=query_embedding,

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
            "Unable to search cache."
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

):

    """
    Store an answer in the semantic cache.
    """

    print("CACHE SAVED:", question),

    try:

        point = PointStruct(

            id=str(uuid.uuid4()),

            vector=embedding,

            payload={

                "question": question,

                "context": context,

                "answer": answer,

            },

        )

        client.upsert(

            collection_name=CACHE_COLLECTION_NAME,

            points=[point],

        )

        logger.info(
            "Answer cached successfully."
        )

    except Exception as ex:

        logger.exception(
            "Failed to save cache: %s",
            ex,
        )

        raise DatabaseException(
            "Unable to save cache."
        ) from ex