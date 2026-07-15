from common.error_codes import ErrorCode
from configuration.constants import (METADATA_EXTRACTION_ERROR_MESSAGE,INVALID_METADATA_ERROR_MESSAGE,)
from exceptions.base_exception import KBBaseException

class MetadataExtractionException(KBBaseException):
    """
    Raised when metadata extraction fails.
    """
    def __init__(self,message: str = METADATA_EXTRACTION_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.METADATA_EXTRACTION_FAILED,)

class InvalidMetadataException(KBBaseException):
    """
    Raised when extracted metadata is invalid.
    """
    def __init__(self,message: str = INVALID_METADATA_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.INVALID_METADATA,)