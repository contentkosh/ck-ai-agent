# ==========================================================
# File Validation Utilities
# Validates uploaded and saved PDF files by checking their
# type, size, existence, and basic file integrity before
# document processing begins.
# ==========================================================

from pathlib import Path

from configuration.config import MAX_FILE_SIZE
from configuration.constants import (
    BYTES_PER_MB,
    EMPTY_UPLOADED_FILE_ERROR,
    FILE_SIZE_EXCEEDED_ERROR,
    INVALID_FILE_TYPE_ERROR,
    INVALID_PDF_SIGNATURE_ERROR,
    NO_FILENAME_ERROR,
    ONLY_PDF_ALLOWED_ERROR,
    PDF_EXTENSION,
    PDF_MAGIC_BYTES,
    SUPPORTED_CONTENT_TYPE,
    UPLOADED_FILE_NOT_FOUND_ERROR,
)
from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
)


def validate_pdf_file(file) -> None:
    if file is None:
        raise EmptyFileException()

    filename = getattr(file, "filename", None) or getattr(file, "name", None)
    if not filename:
        raise InvalidFileException(NO_FILENAME_ERROR)

    if Path(filename).suffix.lower() != PDF_EXTENSION:
        raise InvalidFileException(ONLY_PDF_ALLOWED_ERROR)

    content_type = getattr(file, "content_type", None)
    if content_type and content_type != SUPPORTED_CONTENT_TYPE:
        raise InvalidFileException(INVALID_FILE_TYPE_ERROR)

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size == 0:
        raise EmptyFileException(EMPTY_UPLOADED_FILE_ERROR)

    validate_file_size(file_size)
    validate_pdf_signature(file)


def validate_pdf_signature(file) -> None:
    header = file.file.read(len(PDF_MAGIC_BYTES))
    file.file.seek(0)

    if header != PDF_MAGIC_BYTES:
        raise InvalidFileException(INVALID_PDF_SIGNATURE_ERROR)


def validate_file_size(file_size: int) -> None:
    if file_size > MAX_FILE_SIZE:
        raise InvalidFileException(FILE_SIZE_EXCEEDED_ERROR.format(MAX_FILE_SIZE // BYTES_PER_MB))


def validate_saved_file(file_path: str) -> None:
    path = Path(file_path)

    if not path.exists():
        raise InvalidFileException(UPLOADED_FILE_NOT_FOUND_ERROR)

    validate_file_size(path.stat().st_size)