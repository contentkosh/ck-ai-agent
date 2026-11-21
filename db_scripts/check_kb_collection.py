
from dto.knowledge_base_record_dto import KnowledgeBaseRecordDto
from common.logger import logger
from configuration.config import SCROLL_LIMIT
from configuration.constants import (
    DOCUMENTS_HEADER_LOG,
    DOCUMENT_SEPARATOR_LOG,
    METADATA_DOCUMENT_ID,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_TEXT,
)
from database.qdrant_client_manager import client
from common.collection_utils import get_kb_collection_name


def print_all_documents(business_id: str) -> None:
    """Print every stored chunk for a specific business Knowledge Base."""
    collection_name = get_kb_collection_name(business_id)
    logger.info(DOCUMENTS_HEADER_LOG)
    nextOffset = None

    while True:
        records, nextOffset = client.scroll(
            collection_name=collection_name,
            limit=SCROLL_LIMIT,
            offset=nextOffset,
            with_payload=True,
        )

        for point in records:
            documentPayload = point.payload
            record = KnowledgeBaseRecordDto(
                document_id=documentPayload.get(METADATA_DOCUMENT_ID),
                source=documentPayload.get(METADATA_SOURCE),
                page=documentPayload.get(METADATA_PAGE),
                text=documentPayload.get(METADATA_TEXT),
            )
            logger.info("Document ID=%s | Source=%s | Page=%s", record.document_id, record.source, record.page)
            logger.info("Text: %s", record.text)
            logger.info(DOCUMENT_SEPARATOR_LOG)

        if nextOffset is None:
            break


if __name__ == "__main__":
    logger.info("Business ID is required to inspect a Knowledge Base.")
