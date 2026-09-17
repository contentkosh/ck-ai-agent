from contextlib import asynccontextmanager

from fastapi import FastAPI

from configuration.constants import (
    API_TITLE,
    API_VERSION,
)
from common.exception_handler import register_exception_handlers
from api.routes.health_routes import (
    router as health_router,
)
from api.routes.kb_routes import (
    router as kb_router,
)
from api.routes.upload_routes import (
    router as upload_router,
)
from api.routes.file_routes import (
    router as file_router,
)

from configuration.middleware import (
    RequestContextMiddleware,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Business-specific Qdrant collections are created
    when they are first used.
    """
    yield

# ==========================================================
# Create FastAPI Application
# ==========================================================

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(
        RequestContextMiddleware,
    )
    register_exception_handlers(app)
    app.include_router(
        health_router,
    )
    app.include_router(
        kb_router,
    )
    app.include_router(
        upload_router,
    )
    app.include_router(
        file_router,
    )
    return app

# ==========================================================
# Application Instance
# ==========================================================

app = create_app()