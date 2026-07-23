from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.constants import (
    DOCUMENT_PROCESSING_ERROR_MESSAGE,
    EMPTY_DOCUMENT_MESSAGE,
)

class DocumentProcessingException(ApplicationException):
    """
    Raised when document processing fails.
    """
    def __init__(self, message: str = DOCUMENT_PROCESSING_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.DOCUMENT_PROCESSING_FAILED,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

class EmptyDocumentException(ApplicationException):
    """
    Raised when an uploaded document is empty.
    """
    def __init__(self, message: str = EMPTY_DOCUMENT_MESSAGE):
        super().__init__(
            error_code=ErrorCode.EMPTY_DOCUMENT,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )