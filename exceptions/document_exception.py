"""
Custom exceptions related to document processing.
"""

from common.error_codes import ErrorCodes
from exceptions.base_exception import KBBaseException


class DocumentProcessingException(KBBaseException):
    """
    Raised when document processing fails.
    """

    def __init__(
        self,
        message: str = "Document processing failed.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.DOCUMENT_PROCESSING_FAILED,
        )


class DocumentNotFoundException(KBBaseException):
    """
    Raised when the requested document is not found.
    """

    def __init__(
        self,
        message: str = "Document not found.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.DOCUMENT_NOT_FOUND,
        )


class InvalidDocumentException(KBBaseException):
    """
    Raised when an invalid document is uploaded.
    """

    def __init__(
        self,
        message: str = "Invalid document.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_DOCUMENT,
        )


class EmptyDocumentException(KBBaseException):
    """
    Raised when an uploaded document is empty.
    """

    def __init__(
        self,
        message: str = "Document is empty.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.EMPTY_DOCUMENT,
        )