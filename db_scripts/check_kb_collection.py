from database.qdrant_client_manager import client
from configuration.app_settings import COLLECTION_NAME

records, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=20,
    with_payload=True
)

print("\nDOCUMENTS\n")

for point in records:

    payload = point.payload

    print(

        f"Title : {payload.get('title')}"

    )

    print(

        f"Type : {payload.get('document_type')}"

    )

    print(

        f"Tag : {payload.get('tag')}"

    )

    print(

        f"Source : {payload.get('source')}"

    )

    print(

        f"Page : {payload.get('page')}"

    )

    print("-" * 40)