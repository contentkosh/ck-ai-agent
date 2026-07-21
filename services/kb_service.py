# ==========================================================
# Get Knowledge Base Records
# Retrieve stored Knowledge Base records with optional
# filtering based on the provided document tag.
# ==========================================================

from repositories.kb_repository import (
    get_all_records,
)
# ==========================================================
# Get Knowledge Base
# ==========================================================
def get_knowledge_base_records(
    tag: str | None,
):
    """
    Retrieve Knowledge Base records.
    """
    return get_all_records(tag)