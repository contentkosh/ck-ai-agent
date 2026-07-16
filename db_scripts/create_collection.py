from qdrant_client.models import (
    Distance,
    VectorParams,
)
from common.logger import logger
from database.qdrant_client_manager import client
from configuration.app_settings import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
)

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
        logger.info("Collection '%s' created successfully.", COLLECTION_NAME)
    else:
        logger.info("Collection '%s' already exists.",COLLECTION_NAME)

except Exception as ex:
    logger.exception("Failed to create collection '%s': %s",COLLECTION_NAME,ex)