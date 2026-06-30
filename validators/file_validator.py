"""
File validation utilities.
"""

from pathlib import Path

from common.constants import PDF_EXTENSION
from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
)


def validate_pdf_file(file) -> None:
    """
    Validate an uploaded PDF file.

    Args:
        file: Uploaded file object.

    Raises:
        EmptyFileException
        InvalidFileException
    """

    if file is None:
        raise EmptyFileException()

    filename = getattr(
            file,
            "filename",
            None,
        ) or getattr(
            file,
            "name",
            None,
        )

    if not filename:
        raise InvalidFileException(
            "Uploaded file has no filename."
        )

    extension = Path(filename).suffix.lower()

    if extension != PDF_EXTENSION:
        raise InvalidFileException(
            "Only PDF files are supported."
        )