"""
Tag validation utilities.
"""

from exceptions.validation_exception import InvalidTagException


def validate_tag(tag: str) -> None:
    """
    Validate metadata tag.

    Args:
        tag: User supplied tag.

    Raises:
        InvalidTagException
    """

    if tag is None:
        raise InvalidTagException()

    if not tag.strip():
        raise InvalidTagException(
            "Tag cannot be empty."
        )

    if len(tag) > 100:
        raise InvalidTagException(
            "Tag exceeds maximum length."
        )