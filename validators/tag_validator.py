"""
Tag validation utilities.
"""

from exceptions.validation_exception import InvalidTagException


def validate_tag(tag: str | None) -> None:
    """
    Validate optional metadata tag.

    Args:
        tag: Optional tag supplied by the user.

    Raises:
        InvalidTagException
    """

    # Tag is optional for GET /llm/kb
    if tag is None:
        return

    if not tag.strip():
        raise InvalidTagException(
            "Tag cannot be empty."
        )

    if len(tag) > 100:
        raise InvalidTagException(
            "Tag exceeds maximum length."
        )