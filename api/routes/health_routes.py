from fastapi import APIRouter
from common.logger import logger
from configuration.constants import (
    API_TITLE,
    API_VERSION,
    HEALTH_API_LOG,
    HEALTH_ROUTE,
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
    logger.info(HEALTH_API_LOG,API_TITLE,)
    return HealthResponse(
        status=SERVICE_RUNNING_STATUS,
        service=API_TITLE,
        version=API_VERSION,
    )