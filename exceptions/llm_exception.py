"""
Custom exceptions related to LLM operations.
"""

from common.error_codes import ErrorCodes
from exceptions.base_exception import KBBaseException


class LLMResponseException(KBBaseException):
    """
    Raised when the LLM fails to generate a response.
    """

    def __init__(
        self,
        message: str = "LLM response generation failed.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.LLM_RESPONSE_FAILED,
        )


class LLMTimeoutException(KBBaseException):
    """
    Raised when the LLM request times out.
    """

    def __init__(
        self,
        message: str = "LLM request timed out.",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.LLM_TIMEOUT,
        )