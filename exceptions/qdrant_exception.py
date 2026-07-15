from common.error_codes import ErrorCode
from configuration.constants import (
    QDRANT_CONNECTION_ERROR_MESSAGE,
    QDRANT_INSERT_ERROR_MESSAGE,
    QDRANT_SEARCH_ERROR_MESSAGE,
)
from exceptions.base_exception import KBBaseException

class QdrantConnectionException(KBBaseException):
    """
    Raised when Qdrant connection fails.
    """
    def __init__(self,message: str = QDRANT_CONNECTION_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.QDRANT_CONNECTION_FAILED,)

class QdrantInsertException(KBBaseException):
    """
    Raised when inserting vectors into Qdrant fails.
    """
    def __init__(self,message: str = QDRANT_INSERT_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.QDRANT_INSERT_FAILED,)

class QdrantSearchException(KBBaseException):
    """
    Raised when Qdrant search fails.
    """
    def __init__(self,message: str = QDRANT_SEARCH_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.QDRANT_SEARCH_FAILED,)