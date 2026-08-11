from fastapi import APIRouter, Depends
from api.dependencies import require_permission
from common.logger import logger
from configuration.config import (
    API_TITLE,
    API_VERSION,
)
from configuration.constants import (
    HEALTH_API_LOG,
    HEALTH_ROUTE,
    QUERY_KB_PERMISSION,
    SERVICE_RUNNING_STATUS,
)
from dto.health_response_dto import HealthResponse

router = APIRouter()

# ==========================================================
# Health Check
# ==========================================================

@router.get(
    HEALTH_ROUTE,
    response_model=HealthResponse,
)
def health() -> HealthResponse:
    """
    Health API.
    """
    logger.info(HEALTH_API_LOG, API_TITLE)
    return HealthResponse(
        status=SERVICE_RUNNING_STATUS,
        service=API_TITLE,
        version=API_VERSION,
    )

# ==========================================================
# Authentication & Authorization Test
# ==========================================================

@router.get(
    "/health/auth",
    dependencies=[
        Depends(
            require_permission(QUERY_KB_PERMISSION)
        )
    ],
)
def authenticated_health_check() -> dict[str, str]:
    """
    Verify authentication and authorization.
    """
    return {
        "status": "authorized",
    }