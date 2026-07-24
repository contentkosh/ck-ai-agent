import logging
import os
from logging.handlers import RotatingFileHandler

from configuration.config import (
    LOG_BACKUP_COUNT,
    LOG_FILE_PATH,
    LOG_MAX_BYTES,
)
from configuration.constants import LOGGER_FORMAT

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
        logging.Formatter(LOGGER_FORMAT)
    )
    logger.addHandler(handler)