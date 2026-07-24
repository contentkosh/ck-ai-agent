# ==========================================================
# Upload Validation Utilities
# Validates uploaded document requests by ensuring files are
# provided and that each uploaded file satisfies the required
# PDF validation rules before processing.
# ==========================================================

from fastapi import UploadFile

from configuration.constants import NO_FILES_UPLOADED_ERROR
from exceptions.validation_exception import EmptyFileException
from validators.file_validator import validate_pdf_file

def validate_upload(files: list[UploadFile]) -> None:
    if not files:
        raise EmptyFileException(NO_FILES_UPLOADED_ERROR)
    for file in files:
        validate_pdf_file(file)