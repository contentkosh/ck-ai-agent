from common.error_codes import ErrorCode
from configuration.constants import (
    EMPTY_FILE_ERROR_MESSAGE,
    INVALID_FILE_ERROR_MESSAGE,
    INVALID_REQUEST_ERROR_MESSAGE,
    INVALID_TAG_ERROR_MESSAGE,
)
from exceptions.base_exception import KBBaseException

class InvalidFileException(KBBaseException):
    """
    Raised when an uploaded file is invalid.
    """
    def __init__(self,message: str = INVALID_FILE_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.INVALID_FILE_TYPE,)

class InvalidTagException(KBBaseException):
    """
    Raised when a tag is invalid.
    """
    def __init__(self,message: str = INVALID_TAG_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.INVALID_TAG,)

class EmptyFileException(KBBaseException):
    """
    Raised when an uploaded file is empty.
    """
    def __init__(self,message: str = EMPTY_FILE_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.EMPTY_FILE,)

class InvalidRequestException(KBBaseException):
    """
    Raised when a request is invalid.
    """
    def __init__(self,message: str = INVALID_REQUEST_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.INVALID_REQUEST,)