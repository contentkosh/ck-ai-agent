from common.logger import logger

from database.qdrant_client_manager import client
from configuration.app_settings import (
    COLLECTION_NAME,
    SCROLL_LIMIT,
)
records, _ = client.scroll(collection_name=COLLECTION_NAME,limit=SCROLL_LIMIT,with_payload=True)

logger.info("Documents in Knowledge Base:")

for point in records:
    payload = point.payload
    logger.info("Title : %s", payload.get("title"))
    logger.info("Type : %s", payload.get("document_type"))
    logger.info("Tag : %s", payload.get("tag"))
    logger.info("Source : %s", payload.get("source"))
    logger.info("Page : %s", payload.get("page"))
    logger.info("-" * 40)