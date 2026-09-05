from common.logger import logger
from configuration.constants import FETCH_RECORDS_FAILED_LOG
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.contentkosh_exception import ContentKoshException
from repositories.kb_repository import getAllRecords

def get_knowledge_base_records(
    business_id: str,
    course_ids: list[str] | None,
    tag: str | None,
):
    """
    Retrieve Knowledge Base records for a specific business
    and optionally specific courses and tag.
    """
    try:
        return getAllRecords(
            businessId=business_id,
            courseIds=course_ids,
            tag=tag,
        )
    except ContentKoshException as ex:
        logger.exception(
            "%s: %s",
            FETCH_RECORDS_FAILED_LOG,
            ex,
        )
        raise KnowledgeBaseException() from ex