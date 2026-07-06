import os
import shutil

from fastapi import UploadFile

from configuration.app_settings import UPLOAD_FOLDER


def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded file to the uploads folder.
    """

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    destination = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(destination, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return destination