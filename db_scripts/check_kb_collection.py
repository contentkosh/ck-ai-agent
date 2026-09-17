from dto.knowledge_base_record_dto import (
    KnowledgeBaseRecordDto,
)
from common.logger import logger
from configuration.config import (
    SCROLL_LIMIT,
    MAX_SCROLL_ITERATIONS,
)
from configuration.constants import (
    DOCUMENTS_HEADER_LOG,
    DOCUMENT_DETAILS_LOG,
    DOCUMENT_SEPARATOR_LOG,
    MAX_SCROLL_ITERATIONS_REACHED_LOG,
    METADATA_DOCUMENT_ID,
    METADATA_DOCUMENT_TYPE,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_SUMMARY,
    METADATA_TAG,
    METADATA_TEXT,
    METADATA_TITLE,
)
from database.qdrant_client_manager import client
from common.collection_utils import (
    get_kb_collection_name,
)

def print_all_documents(
    business_id: str,
) -> None:
    """
    Print every stored chunk's metadata for a specific
    business, paginating through its Knowledge Base
    collection.
    """

    collection_name = get_kb_collection_name(
        business_id,
    )

    logger.info(
        DOCUMENTS_HEADER_LOG,
    )

    nextOffset = None
    iteration = 0

    while iteration < MAX_SCROLL_ITERATIONS:
        records, nextOffset = client.scroll(
            collection_name=collection_name,
            limit=SCROLL_LIMIT,
            offset=nextOffset,
            with_payload=True,
        )

        for point in records:
            documentPayload = point.payload

            record = KnowledgeBaseRecordDto(
                document_id=documentPayload.get(
                    METADATA_DOCUMENT_ID,
                ),
                title=documentPayload.get(
                    METADATA_TITLE,
                ),
                document_type=documentPayload.get(
                    METADATA_DOCUMENT_TYPE,
                ),
                tag=documentPayload.get(
                    METADATA_TAG,
                ),
                summary=documentPayload.get(
                    METADATA_SUMMARY,
                ),
                source=documentPayload.get(
                    METADATA_SOURCE,
                ),
                page=documentPayload.get(
                    METADATA_PAGE,
                ),
                text=documentPayload.get(
                    METADATA_TEXT,
                ),
            )
            logger.info(
                DOCUMENT_DETAILS_LOG,
                record.title,
                record.document_type,
                record.tag,
                record.source,
                record.page,
            )
            logger.info(DOCUMENT_SEPARATOR_LOG)
        if nextOffset is None:
            break
        iteration += 1
    else:
        logger.warning(MAX_SCROLL_ITERATIONS_REACHED_LOG)
if __name__ == "__main__":
    logger.info("Business ID is required to inspect a Knowledge Base.")