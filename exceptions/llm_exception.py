from common.error_codes import ErrorCode
from configuration.constants import (LLM_RESPONSE_ERROR_MESSAGE,LLM_TIMEOUT_ERROR_MESSAGE,)
from exceptions.base_exception import KBBaseException

class LLMResponseException(KBBaseException):
    """
    Raised when the LLM fails to generate a response.
    """
    def __init__(self,message: str = LLM_RESPONSE_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.LLM_RESPONSE_FAILED,)

class LLMTimeoutException(KBBaseException):
    """
    Raised when the LLM request times out.
    """
    def __init__(self,message: str = LLM_TIMEOUT_ERROR_MESSAGE,
    ):
        super().__init__(message=message,error_code=ErrorCode.LLM_TIMEOUT,)