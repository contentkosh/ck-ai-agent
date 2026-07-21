from qdrant_client.models import Distance, VectorParams
from database.qdrant_client_manager import client
from configuration.config import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
)

def create_collection_if_missing() -> None:
    """
    Create the Qdrant collection if it does not already exist.
    """
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
        print("Collection created successfully.")
    else:
        print("Collection already exists.")

if __name__ == "__main__":
    try:
        create_collection_if_missing()
    except Exception as e:
        print(e)