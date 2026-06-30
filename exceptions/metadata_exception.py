"""
Custom exceptions related to metadata extraction.
"""

from common.error_codes import ErrorCodes
from exceptions.base_exception import KBBaseException


class MetadataExtractionException(KBBaseException):
    """
    Raised when metadata extraction fails.
    """

    def __init__(
        self,
        message: str = "Metadata extraction failed.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.METADATA_EXTRACTION_FAILED,
        )


class InvalidMetadataException(KBBaseException):
    """
    Raised when extracted metadata is invalid.
    """

    def __init__(
        self,
        message: str = "Invalid metadata.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_METADATA,
        )