from qdrant_client.models import (
    Distance,
    VectorParams,
)
from common.logger import logger
from configuration.config import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
)
from configuration.constants import (
    COLLECTION_ALREADY_EXISTS_LOG,
    COLLECTION_CREATED_LOG,
    COLLECTION_SETUP_FAILED_LOG,
)
from database.qdrant_client_manager import client
from exceptions.qdrant_exception import (QdrantConnectionException,)

def create_collection_if_missing() -> None:
    """
    Create the Qdrant collection if it does not already exist.
    """
    try:
        collections = client.get_collections()
        existing = [
            collection.name
            for collection in collections.collections
        ]

        if COLLECTION_NAME not in existing:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

            logger.info(COLLECTION_CREATED_LOG,)
        
        else:
            logger.info(COLLECTION_ALREADY_EXISTS_LOG,)

    except Exception as ex:
        logger.exception(COLLECTION_SETUP_FAILED_LOG,)
        raise QdrantConnectionException() from ex