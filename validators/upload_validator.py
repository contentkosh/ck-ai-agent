# ==========================================================
# Upload Validation Utilities
# Validates uploaded document requests by ensuring files are
# provided and that each uploaded file satisfies the required
# PDF validation rules before processing.
# ==========================================================

from fastapi import UploadFile
from configuration.error_constants import NO_FILES_UPLOADED_ERROR
from exceptions.validation_exception import EmptyFileException
from validators.file_validator import validate_pdf_file


def validate_upload(files: list[UploadFile], subject_ids: list[str]) -> None:
    if not files:
        raise EmptyFileException(NO_FILES_UPLOADED_ERROR)

    if len(subject_ids) != len(files):
        raise ValueError(
            "The number of subject IDs must match the number of uploaded files."
        )

    for subject_id in subject_ids:
        if not subject_id or not subject_id.strip():
            raise ValueError("Subject ID cannot be empty.")

    for file in files:
        validate_pdf_file(file)
