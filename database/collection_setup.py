from qdrant_client.models import Distance, VectorParams

from common.logger import logger
from configuration.config import EMBEDDING_DIMENSION
from configuration.constants import (
    COLLECTION_ALREADY_EXISTS_LOG,
    COLLECTION_CREATED_LOG,
    COLLECTION_SETUP_FAILED_LOG,
)
from configuration.error_constants import QDRANT_CONNECTION_ERROR_MESSAGE
from database.qdrant_client_manager import client
from exceptions.contentkosh_exception import ContentKoshException


def create_collection_if_missing(
    collection_name: str,
) -> None:
    """
    Create the specified Qdrant collection if it does not
    already exist.
    """
    logger.info(
        "Checking Qdrant collection: %s",
        collection_name,
    )

    try:
        collections = client.get_collections()

        existingCollections = [
            collection.name for collection in collections.collections
        ]

        if collection_name not in existingCollections:
            logger.info(
                "Qdrant collection does not exist. Creation started: %s",
                collection_name,
            )

            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(
                "%s: %s",
                COLLECTION_CREATED_LOG,
                collection_name,
            )
        else:
            logger.info(
                "%s: %s",
                COLLECTION_ALREADY_EXISTS_LOG,
                collection_name,
            )

    except Exception as exception:
        logger.exception(
            "%s: %s",
            COLLECTION_SETUP_FAILED_LOG,
            collection_name,
        )
        raise ContentKoshException(
            QDRANT_CONNECTION_ERROR_MESSAGE,
        ) from exception
