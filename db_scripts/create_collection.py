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
    COLLECTION_ALREADY_EXISTS_SCRIPT_LOG,
    COLLECTION_CREATED_SUCCESS_LOG,
    COLLECTION_CREATION_FAILED_LOG,
)
from database.qdrant_client_manager import client

def create_collection_if_missing() -> None:
    """
    Create the Qdrant collection if it does not already exist.
    """
    collections = client.get_collections()
    existingCollections = [
        collection.name
        for collection in collections.collections
    ]
    if COLLECTION_NAME not in existingCollections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
        )
        logger.info(COLLECTION_CREATED_SUCCESS_LOG)
    else:
        logger.info(COLLECTION_ALREADY_EXISTS_SCRIPT_LOG)
if __name__ == "__main__":
    try:
        create_collection_if_missing()

    except Exception as exception:
        logger.exception(COLLECTION_CREATION_FAILED_LOG)