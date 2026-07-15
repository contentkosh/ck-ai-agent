from fastapi import (FastAPI,Request,status,)
from fastapi.responses import JSONResponse
from common.logger import logger
from common.custom_exceptions import (ApplicationException,)
from common.error_codes import (ErrorCode,)
from configuration.constants import (
    INTERNAL_SERVER_ERROR_MESSAGE,
    UNHANDLED_EXCEPTION_LOG,
)

# ==========================================================
# Error Response Builder
# ==========================================================

def build_error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    """
    Build a standard error response.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "request_id": getattr(
                    request.state,
                    "request_id",
                    None,
                ),
            },
        },
    )

# ==========================================================
# Register Exception Handlers
# ==========================================================

def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register global exception handlers.
    """
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request,
        exc: ApplicationException,
    ):
        """
        Handle all application-specific exceptions.
        """
        return build_error_response(
            request=request,
            status_code=exc.status_code,
            code=exc.error_code.value,
            message=exc.message,
        )

    @app.exception_handler(Exception)
    async def handle_exception(
        request: Request,
        exc: Exception,
    ):
        """
        Handle unexpected exceptions.
        """
        logger.exception(UNHANDLED_EXCEPTION_LOG,exc,)
        return build_error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.INTERNAL_SERVER_ERROR.value,
            message=INTERNAL_SERVER_ERROR_MESSAGE,
        )