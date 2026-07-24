import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from common.logger import logger
from configuration.config import UPLOAD_FOLDER
from configuration.constants import (
    DELETE_TEMP_FILE_FAILED_LOG,
    DELETE_TEMP_FILE_SUCCESS_LOG,
)

def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded file to the uploads folder under a unique
    name so two uploads with the same filename never collide.
    The original filename is preserved as a suffix for
    readability; ingestion payloads still record the
    original filename as the document's source.
    """
    uploadDirectory = Path(UPLOAD_FOLDER)
    uploadDirectory.mkdir(parents=True, exist_ok=True)

    originalName = Path(file.filename).name
    uniqueName = f"{uuid.uuid4().hex}_{originalName}"
    destination = uploadDirectory / uniqueName

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(destination)

def delete_saved_file(filePath: str) -> None:
    """
    Remove a previously saved upload from disk once its
    content has been extracted and no longer needs to be
    kept around. Failures are logged instead of raised.
    """
    try:
        path = Path(filePath)
        if path.exists():
            path.unlink()
            logger.info(DELETE_TEMP_FILE_SUCCESS_LOG, filePath)
    except Exception as exception:
        logger.warning(
            DELETE_TEMP_FILE_FAILED_LOG,
            filePath,
            exception,
        )