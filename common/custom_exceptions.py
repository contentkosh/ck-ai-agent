from http import HTTPStatus
from common.error_codes import ErrorCode
from configuration.constants import (
    DATABASE_ERROR_MESSAGE,
    PDF_PROCESSING_ERROR_MESSAGE,
    EMBEDDING_ERROR_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
    RESOURCE_NOT_FOUND_MESSAGE,
    AUTHENTICATION_FAILED_MESSAGE,
)

# ==========================================================
# Base Exception
# ==========================================================

class ApplicationException(Exception):
    """
    Base application exception.
    """
    def __init__(selferror_code: ErrorCode,message: str,status_code: HTTPStatus,
    ) -> None:

        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# ==========================================================
# Database Exception
# ==========================================================

class DatabaseException(ApplicationException):
    """
    Raised when a database operation fails.
    """

    def __init__(self,message: str = DATABASE_ERROR_MESSAGE,
    ) -> None:

        super().__init__(
            error_code=ErrorCode.QDRANT_INSERT_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

# ==========================================================
# PDF Processing Exception
# ==========================================================

class PDFProcessingException(ApplicationException):
    """
    Raised when a PDF cannot be processed.
    """
    def __init__(self,message: str = PDF_PROCESSING_ERROR_MESSAGE,
    ) -> None:

        super().__init__(
            error_code=ErrorCode.DOCUMENT_PROCESSING_FAILED,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

# ==========================================================
# Embedding Exception
# ==========================================================

class EmbeddingException(ApplicationException):
    """
    Raised when embedding generation fails.
    """
    def __init__(self,message: str = EMBEDDING_ERROR_MESSAGE,
    ) -> None:

        super().__init__(
            error_code=ErrorCode.EMBEDDING_GENERATION_FAILED,
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

# ==========================================================
# Validation Exception
# ==========================================================

class ValidationException(ApplicationException):
    """
    Raised when validation fails.
    """
    def __init__(self,message: str = VALIDATION_ERROR_MESSAGE,
    ) -> None:
        
        super().__init__(
            error_code=ErrorCode.INVALID_REQUEST,
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
        )

# ==========================================================
# Not Found Exception
# ==========================================================

class NotFoundException(ApplicationException):
    """
    Raised when a requested resource is not found.
    """
    def __init__(self,message: str = RESOURCE_NOT_FOUND_MESSAGE,
    ) -> None:
        
        super().__init__(
            error_code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
        )

# ==========================================================
# Authentication Exception
# ==========================================================

class AuthenticationException(ApplicationException):
    """
    Raised when authentication fails.
    """
    def __init__(self,message: str = AUTHENTICATION_FAILED_MESSAGE,
    ) -> None:

        super().__init__(
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
        )