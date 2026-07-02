from qdrant_client.models import Distance, VectorParams

from database.qdrant_client_manager import client
from configuration.app_settings import (
    CACHE_COLLECTION_NAME,
)

EMBEDDING_DIMENSION = 384

try:

    collections = client.get_collections()

    existing = [
        collection.name
        for collection in collections.collections
    ]

    if CACHE_COLLECTION_NAME not in existing:

        client.create_collection(
            collection_name=CACHE_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
        )

        print(f"Collection '{CACHE_COLLECTION_NAME}' created successfully.")

    else:

        print(f"Collection '{CACHE_COLLECTION_NAME}' already exists.")

except Exception as ex:

    print(ex)