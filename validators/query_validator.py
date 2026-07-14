from fastapi import (HTTPException,status,)
from configuration.config import MAX_QUERY_LENGTH
from configuration.constants import (EMPTY_QUERY_ERROR,QUERY_LENGTH_ERROR,)
def validate_query(query: str) -> None:
    """
    Validate user query.
    """
    if query is None or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=EMPTY_QUERY_ERROR,
        )

    if len(query.strip()) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=QUERY_LENGTH_ERROR.format(
                MAX_QUERY_LENGTH
            ),
        )