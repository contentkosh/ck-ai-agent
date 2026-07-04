"""
Base exception for the Knowledge Base application.

All custom exceptions should inherit from this class.
"""


class KBBaseException(Exception):
    """
    Base exception class for all application-specific exceptions.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
    ):
        """
        Initialize the base exception.

        Args:
            message: Human-readable error message.
            error_code: Unique application error code.
        """
        self.message = message
        self.error_code = error_code

        super().__init__(message)

    def to_dict(self) -> dict:
        """
        Convert exception to a serializable dictionary.

        Returns:
            Dictionary containing exception details.
        """
        return {
            "success": False,
            "message": self.message,
            "errorCode": self.error_code,
        }

    def __str__(self) -> str:
        """
        String representation of the exception.
        """
        return (
            f"{self.error_code}: "
            f"{self.message}"
        )