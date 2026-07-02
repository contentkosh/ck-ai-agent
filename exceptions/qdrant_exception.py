"""
Custom exceptions related to Qdrant operations.
"""

from common.error_codes import ErrorCodes
from exceptions.base_exception import KBBaseException


class QdrantConnectionException(KBBaseException):
    """
    Raised when Qdrant connection fails.
    """

    def __init__(
        self,
        message: str = "Unable to connect to Qdrant.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.QDRANT_CONNECTION_FAILED,
        )


class QdrantInsertException(KBBaseException):
    """
    Raised when inserting vectors into Qdrant fails.
    """

    def __init__(
        self,
        message: str = "Failed to insert vectors into Qdrant.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.QDRANT_INSERT_FAILED,
        )


class QdrantSearchException(KBBaseException):
    """
    Raised when Qdrant search fails.
    """

    def __init__(
        self,
        message: str = "Failed to search Qdrant.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.QDRANT_SEARCH_FAILED,
        )