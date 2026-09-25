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
    Save an uploaded file to the configured upload folder
    using a unique filename.
    """
    uploadDirectory = Path(UPLOAD_FOLDER)
    uploadDirectory.mkdir(
        parents=True,
        exist_ok=True,
    )

    originalName = Path(file.filename).name
    uniqueName = f"{uuid.uuid4().hex}_{originalName}"
    destination = uploadDirectory / uniqueName

    logger.info(
        "File save started. Filename=%s | Destination=%s",
        originalName,
        destination,
    )

    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        logger.info(
            "File save completed successfully. Filename=%s | Destination=%s",
            originalName,
            destination,
        )

        return str(destination)

    except Exception:
        logger.exception(
            "File save failed. Filename=%s | Destination=%s",
            originalName,
            destination,
        )
        raise


def delete_saved_file(filePath: str) -> None:
    """
    Remove a previously saved upload from disk once it is
    no longer needed. Deletion failures are logged and ignored.
    """
    logger.info(
        "Temporary file cleanup started: %s",
        filePath,
    )

    try:
        path = Path(filePath)

        if path.exists():
            path.unlink()

            logger.info(
                DELETE_TEMP_FILE_SUCCESS_LOG,
                filePath,
            )
        else:
            logger.info(
                "Temporary file already absent: %s",
                filePath,
            )

    except Exception as exception:
        logger.warning(
            DELETE_TEMP_FILE_FAILED_LOG,
            filePath,
            exception,
        )
