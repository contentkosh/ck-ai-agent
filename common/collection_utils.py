import re

from configuration.config import (
    KB_COLLECTION_PREFIX,
    CACHE_COLLECTION_PREFIX,
)

from configuration.constants import (
    BUSINESS_ID_NORMALIZATION_PATTERN,
)


def normalize_id(
    value: str,
) -> str:
    """
    Normalize an ID so it can safely be used
    in collection names and metadata.
    """
    normalizedValue = re.sub(
        BUSINESS_ID_NORMALIZATION_PATTERN,
        "_",
        value.strip().lower(),
    )

    normalizedValue = normalizedValue.strip("_")

    if not normalizedValue:
        raise ValueError(
            "ID must contain at least one valid character."
        )

    return normalizedValue


def get_kb_collection_name(
    business_id: str,
) -> str:
    """
    Return the Knowledge Base collection name
    for a business.
    """
    normalizedBusinessId = normalize_id(
        business_id,
    )

    return (
        f"{KB_COLLECTION_PREFIX}"
        f"{normalizedBusinessId}"
    )


def get_cache_collection_name(
    business_id: str,
) -> str:
    """
    Return the semantic cache collection name
    for a business.
    """
    normalizedBusinessId = normalize_id(
        business_id,
    )

    return (
        f"{CACHE_COLLECTION_PREFIX}"
        f"{normalizedBusinessId}"
    )