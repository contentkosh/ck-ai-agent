from fastapi import (
    FastAPI,
    Request,
    status,
)

from fastapi.responses import JSONResponse

from common.logger import logger

from common.custom_exceptions import (
    DatabaseException,
    PDFProcessingException,
    ValidationException,
)

from common.error_codes import ErrorCodes


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


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers.
    """

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request,
        exc: ValidationException,
    ):
        return build_error_response(
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCodes.BAD_REQUEST,
            message=str(exc),
        )

    @app.exception_handler(PDFProcessingException)
    async def pdf_exception_handler(
        request: Request,
        exc: PDFProcessingException,
    ):
        return build_error_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCodes.DOCUMENT_PROCESSING_FAILED,
            message=str(exc),
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(
        request: Request,
        exc: DatabaseException,
    ):
        return build_error_response(
            request=request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code=ErrorCodes.QDRANT_CONNECTION_FAILED,
            message=str(exc),
        )

    @app.exception_handler(Exception)
    async def handle_exception(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "Unhandled Exception: %s",
            exc,
        )

        return build_error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCodes.INTERNAL_SERVER_ERROR,
            message="Internal Server Error",
        )