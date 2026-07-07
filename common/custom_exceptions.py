class DatabaseException(Exception):
    """
    Raised when database operation fails.
    """
    pass


class PDFProcessingException(Exception):
    """
    Raised when PDF cannot be processed.
    """
    pass


class EmbeddingException(Exception):
    """
    Raised when embedding generation fails.
    """
    pass


class ValidationException(Exception):
    """
    Raised when validation fails.
    """
    pass