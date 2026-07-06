from fastapi import HTTPException

MAX_QUERY_LENGTH = 1000


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