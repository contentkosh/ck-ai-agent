import re

from configuration.config import (
    KB_COLLECTION_PREFIX,
    CACHE_COLLECTION_PREFIX,
)
from configuration.constants import BUSINESS_ID_NORMALIZATION_PATTERN


def normalize_id(value: str) -> str:
    """
    Normalize an ID so it can safely be used
    in collection names and metadata.
    """
    normalized_value = re.sub(
        BUSINESS_ID_NORMALIZATION_PATTERN,
        "_",
        value.strip().lower(),
    )
    normalized_value = normalized_value.strip("_")

    if not normalized_value:
        raise ValueError("ID must contain at least one valid character.")

    return normalized_value


def get_kb_collection_name(business_id: str) -> str:
    """
    Return the versioned Knowledge Base collection name.
    """
    normalized_business_id = normalize_id(business_id)
    return f"{KB_COLLECTION_PREFIX}{normalized_business_id}_bge"


def get_cache_collection_name(business_id: str) -> str:
    """
    Return the versioned semantic cache collection name.
    """
    normalized_business_id = normalize_id(business_id)
    return f"{CACHE_COLLECTION_PREFIX}{normalized_business_id}_bge"
