from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.error_constants import (
    EMPTY_FILE_ERROR_MESSAGE,
    INVALID_FILE_ERROR_MESSAGE,
    INVALID_REQUEST_ERROR_MESSAGE,
    INVALID_TAG_ERROR_MESSAGE,
    EMPTY_QUERY_ERROR,
    QUERY_LENGTH_ERROR,
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

class EmptyQueryException(ApplicationException):
    """
    Raised when a user query is empty or missing.
    """
    def __init__(self, message: str = EMPTY_QUERY_ERROR):
        super().__init__(
            error_code=ErrorCode.EMPTY_QUERY,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

class QueryTooLongException(ApplicationException):
    """
    Raised when a user query exceeds the maximum allowed length.
    """
    def __init__(self, message: str = QUERY_LENGTH_ERROR):
        super().__init__(
            error_code=ErrorCode.INVALID_QUERY,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )