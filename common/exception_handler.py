from fastapi import (
    FastAPI,
    Request,
    logger,
)
from fastapi.responses import JSONResponse
from httpcore import request

from common.custom_exceptions import (
    ValidationException,
    DatabaseException,
    PDFProcessingException,
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
        return JSONResponse(
            status_code=400,
            content={
                "message": str(exc),
            },
        )

    @app.exception_handler(PDFProcessingException)
    async def pdf_exception_handler(
        request: Request,
        exc: PDFProcessingException,
    ):
        return JSONResponse(
            status_code=422,
            content={
                "message": str(exc),
            },
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(
        request: Request,
        exc: DatabaseException,
    ):
        return JSONResponse(
            status_code=503,
            content={
                "message": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def handle_exception(
            request: Request,
            exc: Exception,
    ):
        logger.exception("Unhandled Exception: %s", exc)

        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error",
                "request_id": getattr(
                    request.state,
                    "request_id",
                    None,
                ),
            },
        )