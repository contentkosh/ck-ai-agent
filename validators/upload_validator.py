"""
Upload validation utilities.

Validates uploaded documents before
processing begins.
"""

from fastapi import UploadFile

from exceptions.validation_exception import (
    EmptyFileException,
)

from validators.file_validator import (
    validate_pdf_file,
)


def validate_upload(
    files: list[UploadFile],
) -> None:
    """
    Validate uploaded PDF files.

    Args:
        files:
            Uploaded documents.

    Raises:
        EmptyFileException
        InvalidFileException
    """

    if not files:
        raise EmptyFileException(
            "No files were uploaded."
        )

    for file in files:
        validate_pdf_file(file)