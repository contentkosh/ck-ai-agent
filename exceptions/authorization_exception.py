from http import HTTPStatus
from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from configuration.error_constants import (AUTHORIZATION_FAILED_MESSAGE,)

class AuthorizationException(ApplicationException):
    """
    Raised when an authenticated user does not have permission
    to access a resource.
    """

    def __init__(
        self,
        message: str = AUTHORIZATION_FAILED_MESSAGE,
    ) -> None:

        super().__init__(
            error_code=ErrorCode.AUTHORIZATION_FAILED,
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
        )