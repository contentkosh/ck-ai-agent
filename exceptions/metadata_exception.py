from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.error_constants import (
    METADATA_EXTRACTION_ERROR_MESSAGE,
    INVALID_METADATA_ERROR_MESSAGE,
)

class MetadataExtractionException(ApplicationException):
    """
    Raised when metadata extraction fails.
    """
    def __init__(self, message: str = METADATA_EXTRACTION_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.METADATA_EXTRACTION_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

class InvalidMetadataException(ApplicationException):
    """
    Raised when extracted metadata is invalid.
    """
    def __init__(self, message: str = INVALID_METADATA_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.INVALID_METADATA,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )