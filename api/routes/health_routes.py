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
def health_check():
    """
    Health Check API.
    """
    logger.info("[%s] Health Check API called.", API_TITLE)

    return HealthResponse(
        status="Running",
        service=API_TITLE,
        version=API_VERSION,
    )