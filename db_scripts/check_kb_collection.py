from database.qdrant_client_manager import client
from configuration.config import (
    COLLECTION_NAME,
    SCROLL_LIMIT,
)

def print_all_documents() -> None:
    """
    Print every stored chunk's metadata, paginating through
    the full collection.
    """
    print("\nDOCUMENTS\n")
    next_offset = None

    while True:
        records, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=SCROLL_LIMIT,
            offset=next_offset,
            with_payload=True,
        )
        for point in records:
            payload = point.payload
            print(f"Title : {payload.get('title')}")
            print(f"Type : {payload.get('document_type')}")
            print(f"Tag : {payload.get('tag')}")
            print(f"Source : {payload.get('source')}")
            print(f"Page : {payload.get('page')}")
            print("-" * 40)
        if next_offset is None:
            break

if __name__ == "__main__":
    print_all_documents()