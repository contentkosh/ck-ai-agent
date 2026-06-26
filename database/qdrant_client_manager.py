from qdrant_client import QdrantClient

from configuration.app_settings import (
    QDRANT_HOST,
    QDRANT_PORT
)

client = QdrantClient(

    host=QDRANT_HOST,

    port=QDRANT_PORT
)