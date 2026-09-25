from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.file_routes import router as file_router
from api.routes.health_routes import router as health_router
from api.routes.kb_routes import router as kb_router
from api.routes.upload_routes import router as upload_router
from common.exception_handler import register_exception_handlers
from common.logger import logger
from configuration.constants import API_TITLE, API_VERSION
from configuration.middleware import RequestContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application startup initiated")
    try:
        yield
    except Exception:
        logger.exception("Application encountered an error during runtime")
        raise
    finally:
        logger.info("FastAPI application shutdown completed")


def create_app() -> FastAPI:
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(kb_router)
    app.include_router(upload_router)
    app.include_router(file_router)
    logger.info("FastAPI application configured successfully")
    return app


app = create_app()
