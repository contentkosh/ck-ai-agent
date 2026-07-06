from fastapi import FastAPI

from configuration.constants import (
    API_TITLE,
    API_VERSION,
)

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


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
)

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
