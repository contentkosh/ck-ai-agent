import os

from fastapi import HTTPException

# ==========================================================
# Constants
# ==========================================================

MAX_QUERY_LENGTH = 1000
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ==========================================================
# Validate Query
# ==========================================================

def validate_query(query: str) -> None:
    """
    Validate user query.
    """

    if query is None or not query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    if len(query.strip()) > MAX_QUERY_LENGTH:

        raise HTTPException(
            status_code=400,
            detail=f"Query cannot exceed {MAX_QUERY_LENGTH} characters."
        )


# ==========================================================
# Validate Uploaded PDF
# ==========================================================

def validate_pdf(file) -> None:
    """
    Validate uploaded PDF.
    """

    if file is None:

        raise HTTPException(
            status_code=400,
            detail="No file uploaded."
        )

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


# ==========================================================
# Validate Filename
# ==========================================================

def validate_filename(filename: str) -> None:
    """
    Validate filename.
    """

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Filename cannot be empty."
        )

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


# ==========================================================
# Validate File Size
# ==========================================================

def validate_file_size(file_path: str) -> None:
    """
    Validate uploaded file size.
    """

    size = os.path.getsize(file_path)

    if size > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="File size exceeds 20 MB."
        )


# ==========================================================
# Validate Tag
# ==========================================================

def validate_tag(tag: str | None) -> None:
    """
    Validate optional tag parameter.
    """

    if tag is None:
        return

    if not tag.strip():

        raise HTTPException(
            status_code=400,
            detail="Tag cannot be empty."
        )

    if len(tag) > 100:

        raise HTTPException(
            status_code=400,
            detail="Tag is too long."
        )