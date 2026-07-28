from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.error_constants import (KNOWLEDGE_BASE_ERROR_MESSAGE,)

class KnowledgeBaseException(ApplicationException):
    """
    Raised when a Knowledge Base operation fails.
    """
    def __init__(
        self,
        message: str = KNOWLEDGE_BASE_ERROR_MESSAGE,
    ):
        super().__init__(
            error_code=ErrorCode.KNOWLEDGE_BASE_OPERATION_FAILED,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )