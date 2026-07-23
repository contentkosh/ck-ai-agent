from dto.knowledge_base_record_dto import KnowledgeBaseRecordDto
from configuration.config import (COLLECTION_NAME,SCROLL_LIMIT,)
from database.qdrant_client_manager import client
from configuration.constants import (
    METADATA_DOCUMENT_ID,
    METADATA_DOCUMENT_TYPE,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_SUMMARY,
    METADATA_TAG,
    METADATA_TEXT,
    METADATA_TITLE,
)

def print_all_documents() -> None:
    """
    Print every stored chunk's metadata, paginating through
    the full collection.
    """
    print("\nDOCUMENTS\n")

    nextOffset = None

    while True:
        records, nextOffset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=SCROLL_LIMIT,
            offset=nextOffset,
            with_payload=True,
        )

        for point in records:
            documentPayload = point.payload

            record = KnowledgeBaseRecordDto(
                document_id=documentPayload.get(METADATA_DOCUMENT_ID,),
                title=documentPayload.get(METADATA_TITLE,),
                document_type=documentPayload.get(METADATA_DOCUMENT_TYPE,),
                tag=documentPayload.get(METADATA_TAG,),
                summary=documentPayload.get(METADATA_SUMMARY,),
                source=documentPayload.get(METADATA_SOURCE,),
                page=documentPayload.get(METADATA_PAGE,),
                text=documentPayload.get(METADATA_TEXT,),
            )

            print(f"Title : {record.title}")
            print(f"Type : {record.document_type}")
            print(f"Tag : {record.tag}")
            print(f"Source : {record.source}")
            print(f"Page : {record.page}")
            print("-" * 40)

        if nextOffset is None:
            break

if __name__ == "__main__":
    print_all_documents()