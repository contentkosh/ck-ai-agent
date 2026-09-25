import uvicorn
from dotenv import load_dotenv

load_dotenv()

from api.app import app
from common.logger import logger
from configuration.config import (
    API_HOST,
    API_PORT,
    API_RELOAD,
)

if __name__ == "__main__":
    logger.info("Starting CK AI Agent application")
    logger.info(
        "Server configuration: host=%s, port=%s, reload=%s",
        API_HOST,
        API_PORT,
        API_RELOAD,
    )

    try:
        uvicorn.run(
            "api.app:app",
            host=API_HOST,
            port=API_PORT,
            reload=API_RELOAD,
        )
    except Exception:
        logger.exception("Application terminated due to an unexpected error")
        raise
    finally:
        logger.info("CK AI Agent application stopped")
