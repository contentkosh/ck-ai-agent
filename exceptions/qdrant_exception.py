from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.error_constants import (
    QDRANT_CONNECTION_ERROR_MESSAGE,
    QDRANT_INSERT_ERROR_MESSAGE,
    QDRANT_SEARCH_ERROR_MESSAGE,
    QDRANT_FETCH_ERROR_MESSAGE,
    QDRANT_DELETE_ERROR_MESSAGE,
)

class QdrantConnectionException(ApplicationException):
    """
    Raised when Qdrant connection fails.
    """
    def __init__(self, message: str = QDRANT_CONNECTION_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.QDRANT_CONNECTION_FAILED,
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )

class QdrantInsertException(ApplicationException):
    """
    Raised when inserting vectors into Qdrant fails.
    """
    def __init__(self, message: str = QDRANT_INSERT_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.QDRANT_INSERT_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

class QdrantSearchException(ApplicationException):
    """
    Raised when Qdrant search fails.
    """
    def __init__(self, message: str = QDRANT_SEARCH_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.QDRANT_SEARCH_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

class QdrantFetchException(ApplicationException):
    """
    Raised when fetching records from Qdrant fails.
    """
    def __init__(self, message: str = QDRANT_FETCH_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.QDRANT_FETCH_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


class QdrantDeleteException(ApplicationException):
    """
    Raised when deleting records from Qdrant fails.
    """
    def __init__(self, message: str = QDRANT_DELETE_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.QDRANT_DELETE_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )