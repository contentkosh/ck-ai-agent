# ==========================================================
# Tag Validation Utilities
# Validates optional metadata tags by ensuring they are
# non-empty and within the allowed length before use in
# Knowledge Base operations.
# ==========================================================

from configuration.config import MAX_TAG_LENGTH
from configuration.error_constants import (
    EMPTY_TAG_ERROR,
    TAG_LENGTH_ERROR,
)
from exceptions.validation_exception import InvalidTagException

def validate_tag(tag: str | None) -> None:
    if tag is None:
        return
    if not tag.strip():
        raise InvalidTagException(EMPTY_TAG_ERROR)
    if len(tag) > MAX_TAG_LENGTH:
        raise InvalidTagException(TAG_LENGTH_ERROR.format(MAX_TAG_LENGTH))