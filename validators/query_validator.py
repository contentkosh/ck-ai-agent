# ==========================================================
# Query Validation Utilities
# Validates user queries by ensuring they are not empty and
# do not exceed the maximum allowed length before processing.
# ==========================================================

from configuration.config import MAX_QUERY_LENGTH
from configuration.error_constants import (
    EMPTY_QUERY_ERROR,
    QUERY_LENGTH_ERROR,
)
from exceptions.validation_exception import (
    EmptyQueryException,
    QueryTooLongException,
)
def validate_query(query: str) -> None:
    """
    Validate user query.

    Raises:
        EmptyQueryException
        QueryTooLongException
    """
    if query is None or not query.strip():
        raise EmptyQueryException(
            EMPTY_QUERY_ERROR,
        )

    if len(query.strip()) > MAX_QUERY_LENGTH:
        raise QueryTooLongException(
            QUERY_LENGTH_ERROR.format(
                MAX_QUERY_LENGTH,
            )
        )