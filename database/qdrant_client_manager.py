from qdrant_client import QdrantClient

from common.logger import logger

from configuration.config import (
    QDRANT_HOST,
    QDRANT_PORT,
)
from configuration.constants import (
    QDRANT_CLIENT_INITIALIZED_LOG,
    QDRANT_CLIENT_INITIALIZING_LOG,
)
logger.info(
    QDRANT_CLIENT_INITIALIZING_LOG,
    QDRANT_HOST,
    QDRANT_PORT,
)
client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
)
logger.info(QDRANT_CLIENT_INITIALIZED_LOG)