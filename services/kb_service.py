from common.logger import logger
from configuration.constants import FETCH_RECORDS_FAILED_LOG
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.knowledge_base_exception import KnowledgeBaseException
from repositories.kb_repository import getAllRecords


def get_knowledge_base_records(business_id: str, course_ids: list[str] | None):
    """Retrieve Knowledge Base records for a specific business and optionally specific courses."""
    logger.info("Knowledge Base record retrieval started. Business ID=%s | Course IDs=%s", business_id, course_ids)

    try:
        records = getAllRecords(businessId=business_id, courseIds=course_ids)
        logger.info("Knowledge Base record retrieval completed. Business ID=%s | Records=%d", business_id, len(records))
        return records

    except ContentKoshException as ex:
        logger.exception("%s: %s", FETCH_RECORDS_FAILED_LOG, ex)
        raise KnowledgeBaseException() from ex