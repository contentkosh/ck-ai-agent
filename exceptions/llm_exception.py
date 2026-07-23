from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.constants import (
    LLM_RESPONSE_ERROR_MESSAGE,
)

class LLMResponseException(ApplicationException):
    """
    Raised when the LLM fails to generate a response.
    """
    def __init__(self, message: str = LLM_RESPONSE_ERROR_MESSAGE):
        super().__init__(
            error_code=ErrorCode.LLM_RESPONSE_FAILED,
            message=message,
            status_code=HTTPStatus.BAD_GATEWAY,
        )
