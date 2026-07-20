import logging
import os
from logging.handlers import RotatingFileHandler
from configuration.config import (
    LOG_FILE_PATH,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
)

os.makedirs(os.path.dirname(LOG_FILE_PATH) or ".", exist_ok=True)

logger = logging.getLogger("ck_ai_agent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )
    logger.addHandler(handler)