from qdrant_client.models import Distance, VectorParams

from database.qdrant_client_manager import client
from configuration.app_settings import (
    COLLECTION_NAME
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

                distance=Distance.COSINE

            )

        )

        print("Collection created successfully.")

    else:

        print("Collection already exists.")

except Exception as e:

    print(e)