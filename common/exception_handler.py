from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from common.custom_exceptions import ApplicationException
from common.error_codes import ErrorCode
from common.logger import logger
from configuration.constants import UNHANDLED_EXCEPTION_LOG
from configuration.error_constants import INTERNAL_SERVER_ERROR_MESSAGE


def build_error_response(
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status": status_code,
            "status_text": HTTPStatus(status_code).phrase,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request,
        exc: ApplicationException,
    ):
        logger.warning(
            "Application exception: %s %s | code=%s | message=%s",
            request.method,
            request.url.path,
            exc.error_code.value,
            exc.message,
        )

        return build_error_response(
            status_code=exc.status_code,
            code=exc.error_code.value,
            message=exc.message,
        )

    @app.exception_handler(Exception)
    async def handle_exception(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "%s | %s %s",
            UNHANDLED_EXCEPTION_LOG,
            request.method,
            request.url.path,
        )

        return build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.INTERNAL_SERVER_ERROR.value,
            message=INTERNAL_SERVER_ERROR_MESSAGE,
        )
