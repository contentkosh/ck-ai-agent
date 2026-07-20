from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.constants import (
    EMPTY_FILE_ERROR_MESSAGE,
    INVALID_FILE_ERROR_MESSAGE,
    INVALID_REQUEST_ERROR_MESSAGE,
    INVALID_TAG_ERROR_MESSAGE,
)

class InvalidFileException(ApplicationException):
    """
    Raised when an uploaded file is invalid.
    """
    def __init__(self, message: str = INVALID_FILE_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.INVALID_FILE_TYPE,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

class InvalidTagException(ApplicationException):
    """
    Raised when a tag is invalid.
    """
    def __init__(self, message: str = INVALID_TAG_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.INVALID_TAG,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

class EmptyFileException(ApplicationException):
    """
    Raised when an uploaded file is empty.
    """
    def __init__(self, message: str = EMPTY_FILE_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.EMPTY_FILE,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

class InvalidRequestException(ApplicationException):
    """
    Raised when a request is invalid.
    """
    def __init__(self, message: str = INVALID_REQUEST_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.INVALID_REQUEST,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )