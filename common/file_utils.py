from pathlib import Path
import shutil
from fastapi import UploadFile
from configuration.config import (UPLOAD_FOLDER,)

def save_uploaded_file(
    file: UploadFile,
) -> str:
    """
    Save uploaded file to the uploads folder.
    """
    upload_directory = Path(UPLOAD_FOLDER)
    upload_directory.mkdir(parents=True,exist_ok=True,)
    filename = Path(file.filename).name
    destination = upload_directory / filename
    with destination.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer,
        )
    return str(destination)