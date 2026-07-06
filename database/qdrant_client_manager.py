from qdrant_client import QdrantClient

from common.logger import logger

from configuration.app_settings import (
    QDRANT_HOST,
    QDRANT_PORT,
)

logger.info(
    "Initializing Qdrant client. host=%s port=%s",
    QDRANT_HOST,
    QDRANT_PORT,
)

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
)

logger.info("Qdrant client initialized successfully.")