import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from configuration.config import (
    LOG_BACKUP_COUNT,
    LOG_FILE_PATH,
    LOG_MAX_BYTES,
)
from configuration.constants import LOGGER_FORMAT

os.makedirs(
    os.path.dirname(LOG_FILE_PATH) or ".",
    exist_ok=True,
)

logger = logging.getLogger("ck_ai_agent")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    formatter = logging.Formatter(LOGGER_FORMAT)

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
