from common.logger import logger
from configuration.constants import (
    FETCH_RECORDS_FAILED_LOG,
)
from exceptions.knowledge_base_exception import (
    KnowledgeBaseException,
)
from exceptions.contentkosh_exception import (
    ContentKoshException,
)
from repositories.kb_repository import (
    getAllRecords,
)

def get_knowledge_base_records(
    business_id: str,
    course_id: str | None,
    tag: str | None,
):
    """
    Retrieve Knowledge Base records for a specific business
    and optionally a specific course and tag.
    """
    try:
        return getAllRecords(
            businessId=business_id,
            courseId=course_id,
            tag=tag,
        )
    except ContentKoshException as ex:
        logger.exception(
            "%s: %s",
            FETCH_RECORDS_FAILED_LOG,
            ex,
        )
        raise KnowledgeBaseException() from ex