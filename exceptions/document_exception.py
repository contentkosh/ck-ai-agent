from common.error_codes import ErrorCode
from configuration.constants import (
    DOCUMENT_PROCESSING_ERROR_MESSAGE,
    DOCUMENT_NOT_FOUND_MESSAGE,
    INVALID_DOCUMENT_MESSAGE,
    EMPTY_DOCUMENT_MESSAGE,
)
from exceptions.base_exception import KBBaseException

class DocumentProcessingException(KBBaseException):
    """
    Raised when document processing fails.
    """
    def __init__(self,message: str = DOCUMENT_PROCESSING_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCodes.DOCUMENT_PROCESSING_FAILED,)

class DocumentNotFoundException(KBBaseException):
    """
    Raised when the requested document is not found.
    """
    def __init__(self,message: str = DOCUMENT_NOT_FOUND_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCodes.DOCUMENT_NOT_FOUND,)

class InvalidDocumentException(KBBaseException):
    """
    Raised when an invalid document is uploaded.
    """
    def __init__(self,message: str = INVALID_DOCUMENT_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCodes.INVALID_DOCUMENT,)

class EmptyDocumentException(KBBaseException):
    """
    Raised when an uploaded document is empty.
    """
    def __init__(self,message: str = EMPTY_DOCUMENT_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCodes.EMPTY_DOCUMENT,)