"""
File validation utilities.

This module contains reusable validation functions
for uploaded PDF documents.
"""

from pathlib import Path

from configuration.constants import (
    MAX_FILE_SIZE,
    PDF_EXTENSION,
    SUPPORTED_CONTENT_TYPE,
)

from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
)


def validate_pdf_file(file) -> None:
    """
    Validate an uploaded PDF file.

    Args:
        file:
            Uploaded file object.

    Raises:
        EmptyFileException
        InvalidFileException
    """

    if file is None:
        raise EmptyFileException()

    filename = (
        getattr(file, "filename", None)
        or getattr(file, "name", None)
    )

    if not filename:
        raise InvalidFileException(
            "Uploaded file has no filename."
        )

    extension = Path(filename).suffix.lower()

    if extension != PDF_EXTENSION:
        raise InvalidFileException(
            "Only PDF files are allowed."
        )

    content_type = getattr(
        file,
        "content_type",
        None,
    )

    if (
        content_type
        and content_type != SUPPORTED_CONTENT_TYPE
    ):
        raise InvalidFileException(
            "Invalid file type. Only PDF files are allowed."
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size == 0:
        raise EmptyFileException(
            "Uploaded file is empty."
        )

    validate_file_size(file_size)


def validate_file_size(
    file_size: int,
) -> None:
    """
    Validate uploaded file size.

    Args:
        file_size:
            File size in bytes.

    Raises:
        InvalidFileException
    """

    if file_size > MAX_FILE_SIZE:
        raise InvalidFileException(
            f"File size exceeds the maximum allowed "
            f"limit of {MAX_FILE_SIZE // (1024 * 1024)} MB."
        )


def validate_saved_file(
    file_path: str,
) -> None:
    """
    Validate a saved file on disk.

    Args:
        file_path:
            Path to the saved file.

    Raises:
        InvalidFileException
    """

    path = Path(file_path)

    if not path.exists():
        raise InvalidFileException(
            "Uploaded file could not be found."
        )

    validate_file_size(
        path.stat().st_size
    )