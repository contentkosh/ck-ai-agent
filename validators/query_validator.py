from fastapi import HTTPException

from configuration.app_settings import MAX_QUERY_LENGTH
from configuration.constants import (
    EMPTY_QUERY_ERROR,
    QUERY_LENGTH_ERROR,
)
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