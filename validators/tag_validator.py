# ==========================================================
# Tag Validation Utilities
# Validates optional metadata tags by ensuring they are
# non-empty and within the allowed length before use in
# Knowledge Base operations.
# ==========================================================

from exceptions.validation_exception import InvalidTagException

def validate_tag(tag: str | None) -> None:
    # Tag is optional for GET /llm/kb
    if tag is None:
        return
    if not tag.strip():
        raise InvalidTagException("Tag cannot be empty.")
    if len(tag) > 100:
        raise InvalidTagException("Tag exceeds maximum length.")