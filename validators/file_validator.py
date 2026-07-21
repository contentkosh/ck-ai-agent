# ==========================================================
# File Validation Utilities
# Validates uploaded and saved PDF files by checking their
# type, size, existence, and basic file integrity before
# document processing begins.
# ==========================================================

from pathlib import Path
from configuration.config import MAX_FILE_SIZE
from configuration.constants import (
    PDF_EXTENSION,
    SUPPORTED_CONTENT_TYPE,
    PDF_MAGIC_BYTES,
)
from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
)

def validate_pdf_file(file) -> None:
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
    validate_pdf_signature(file)


def validate_pdf_signature(file) -> None:
    header = file.file.read(len(PDF_MAGIC_BYTES))
    file.file.seek(0)

    if header != PDF_MAGIC_BYTES:
        raise InvalidFileException(
            "File content does not match a valid PDF."
        )

def validate_file_size(
    file_size: int,
) -> None:
    if file_size > MAX_FILE_SIZE:
        raise InvalidFileException(
            f"File size exceeds the maximum allowed "
            f"limit of {MAX_FILE_SIZE // (1024 * 1024)} MB."
        )


def validate_saved_file(
    file_path: str,
) -> None:
    path = Path(file_path)

    if not path.exists():
        raise InvalidFileException(
            "Uploaded file could not be found."
        )
    validate_file_size(
        path.stat().st_size
    )