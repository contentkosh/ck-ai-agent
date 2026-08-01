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
    PDF_EXTENSION,
    PDF_MAGIC_BYTES,
    SUPPORTED_CONTENT_TYPE,
)
from configuration.error_constants import (
    EMPTY_UPLOADED_FILE_ERROR,
    FILE_SIZE_EXCEEDED_ERROR,
    INVALID_FILE_TYPE_ERROR,
    INVALID_PDF_SIGNATURE_ERROR,
    NO_FILENAME_ERROR,
    UPLOADED_FILE_NOT_FOUND_ERROR,
)
from exceptions.validation_exception import (
    EmptyFileException,
    InvalidFileException,
)

def validate_pdf_file(file) -> None:
    """
    Validate an uploaded PDF file.
    """
    if file is None:
        raise EmptyFileException()

    filename = getattr(file, "filename", None) or getattr(file, "name", None)

    if not filename:
        raise InvalidFileException(NO_FILENAME_ERROR)

    if Path(filename).suffix.lower() != PDF_EXTENSION:
        raise InvalidFileException(INVALID_FILE_TYPE_ERROR)

    contentType = getattr(file, "content_type", None)

    if contentType and contentType != SUPPORTED_CONTENT_TYPE:
        raise InvalidFileException(INVALID_FILE_TYPE_ERROR)

    file.file.seek(0, 2)
    fileSize = file.file.tell()
    file.file.seek(0)

    if fileSize == 0:
        raise EmptyFileException(EMPTY_UPLOADED_FILE_ERROR)

    validate_file_size(fileSize)
    validate_pdf_signature(file)

def validate_pdf_signature(file) -> None:
    """
    Validate the PDF magic bytes.
    """
    header = file.file.read(len(PDF_MAGIC_BYTES))
    file.file.seek(0)

    if header != PDF_MAGIC_BYTES:
        raise InvalidFileException(INVALID_PDF_SIGNATURE_ERROR)

def validate_file_size(fileSize: int) -> None:
    """
    Validate the uploaded file size.
    """
    if fileSize > MAX_FILE_SIZE:
        raise InvalidFileException(
            FILE_SIZE_EXCEEDED_ERROR.format(
                MAX_FILE_SIZE // BYTES_PER_MB,
            )
        )

def validate_saved_file(filePath: str) -> None:
    """
    Validate a saved file on disk.
    """
    path = Path(filePath)

    if not path.exists():
        raise InvalidFileException(UPLOADED_FILE_NOT_FOUND_ERROR)

    validate_file_size(path.stat().st_size)