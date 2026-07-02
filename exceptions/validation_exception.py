"""
Custom exceptions related to validation.
"""

from common.error_codes import ErrorCodes
from exceptions.base_exception import KBBaseException


class InvalidFileException(KBBaseException):
    """
    Raised when an uploaded file is invalid.
    """

    def __init__(
        self,
        message: str = "Invalid file uploaded.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_FILE_TYPE,
        )


class InvalidTagException(KBBaseException):
    """
    Raised when a tag is invalid.
    """

    def __init__(
        self,
        message: str = "Invalid tag.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_TAG,
        )


class EmptyFileException(KBBaseException):
    """
    Raised when an uploaded file is empty.
    """

    def __init__(
        self,
        message: str = "Uploaded file is empty.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.EMPTY_FILE,
        )


class InvalidRequestException(KBBaseException):
    """
    Raised when a request is invalid.
    """

    def __init__(
        self,
        message: str = "Invalid request.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_REQUEST,
        )