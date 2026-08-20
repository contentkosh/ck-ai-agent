import re
from configuration.config import (
    KB_COLLECTION_PREFIX,
    CACHE_COLLECTION_PREFIX,
)

def normalize_business_id(
    business_id: str,
) -> str:
    """
    Normalize a business ID so it can safely be used
    as part of a Qdrant collection name.
    """
    normalizedBusinessId = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        business_id.strip().lower(),
    )
    normalizedBusinessId = normalizedBusinessId.strip("_")
    if not normalizedBusinessId:
        raise ValueError(
            "Business ID must contain at least one valid character."
        )
    return normalizedBusinessId


def get_kb_collection_name(
    business_id: str,
) -> str:
    """
    Return the Knowledge Base collection name
    for a business.
    """
    normalizedBusinessId = normalize_business_id(
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
    normalizedBusinessId = normalize_business_id(
        business_id,
    )
    return (
        f"{CACHE_COLLECTION_PREFIX}"
        f"{normalizedBusinessId}"
    )