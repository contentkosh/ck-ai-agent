from fastapi import APIRouter
from common.logger import logger
from configuration.constants import (
    API_TITLE,
    API_VERSION,
)
from dto.health_response_dto import HealthResponse
router = APIRouter()

# ==========================================================
# Health Check
# ==========================================================

@router.get(
    "/",
    response_model=HealthResponse,
)
def health():
    """
    Health API.
    """
    logger.info("[%s] Health API called.", API_TITLE)
    return HealthResponse(
        status="Running",
        service=API_TITLE,
        version=API_VERSION,
    )