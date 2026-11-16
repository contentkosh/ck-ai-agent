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


def create_collection_if_missing(collection_name: str) -> None:
    """Create the specified Qdrant collection if missing and validate its vector dimension."""
    logger.info("Checking Qdrant collection: %s", collection_name)

    try:
        collections = client.get_collections()
        existing_collections = [
            collection.name for collection in collections.collections
        ]

        if collection_name not in existing_collections:
            logger.info(
                "Qdrant collection does not exist. Creation started: %s",
                collection_name,
            )
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION, distance=Distance.COSINE
                ),
            )
            logger.info("%s: %s", COLLECTION_CREATED_LOG, collection_name)
            return

        collection_info = client.get_collection(collection_name)
        vectors_config = collection_info.config.params.vectors

        if isinstance(vectors_config, dict):
            raise ValueError(
                f"Collection '{collection_name}' uses named vectors. Expected a single unnamed vector of dimension {EMBEDDING_DIMENSION}."
            )

        existing_dimension = vectors_config.size

        if existing_dimension != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Collection '{collection_name}' has vector dimension {existing_dimension}, "
                f"but the configured embedding model requires {EMBEDDING_DIMENSION}. "
                "Recreate the collection and re-ingest its documents."
            )

        logger.info(
            "%s: %s | Vector dimension: %d",
            COLLECTION_ALREADY_EXISTS_LOG,
            collection_name,
            existing_dimension,
        )

    except Exception as exception:
        logger.exception("%s: %s", COLLECTION_SETUP_FAILED_LOG, collection_name)
        raise ContentKoshException(QDRANT_CONNECTION_ERROR_MESSAGE) from exception
