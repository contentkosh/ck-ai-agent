from common.logger import logger
from configuration.constants import FETCH_RECORDS_FAILED_LOG
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.contentkosh_exception import ContentKoshException
from repositories.kb_repository import getAllRecords

def get_knowledge_base_records(
    tag: str | None,
):
    """
    Retrieve Knowledge Base records.
    """
    try:
        return getAllRecords(tag)

    except ContentKoshException as ex:
        logger.exception(FETCH_RECORDS_FAILED_LOG,ex,)
        raise KnowledgeBaseException() from ex