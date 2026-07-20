import uuid
from pathlib import Path
import shutil
from fastapi import UploadFile
from common.logger import logger
from configuration.config import UPLOAD_FOLDER

def save_uploaded_file(
    file: UploadFile,
) -> str:
    """
    Save uploaded file to the uploads folder under a unique
    name so two uploads with the same filename never collide.
    The original filename is preserved as a suffix for
    readability; ingestion payloads still record the
    *original* filename as the document's "source".
    """
    upload_directory = Path(UPLOAD_FOLDER)
    upload_directory.mkdir(parents=True, exist_ok=True)

    original_name = Path(file.filename).name
    unique_name = f"{uuid.uuid4().hex}_{original_name}"
    destination = upload_directory / unique_name

    with destination.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )
    return str(destination)

def delete_saved_file(file_path: str) -> None:
    """
    Remove a previously saved upload from disk once its
    content has been extracted and no longer needs to be
    kept around. Failures are logged, not raised, since a
    stray temp file should never fail the ingestion request
    that already succeeded.
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info("Deleted temporary upload file: %s", file_path)
    except Exception as ex:
        logger.warning(
            "Failed to delete temporary upload file '%s': %s",
            file_path,
            ex,
        )