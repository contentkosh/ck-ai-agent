from fastapi import APIRouter

from common.logger import logger

from configuration.constants import (
    API_TITLE,
    API_VERSION,
)

router = APIRouter()


# ==========================================================
# Health Check
# ==========================================================

@router.get("/")
def health_check():
    """
    Health Check API.
    """

    logger.info("Health Check API called.")

    return {
        "status": "Running",
        "service": API_TITLE,
        "version": API_VERSION,
    }