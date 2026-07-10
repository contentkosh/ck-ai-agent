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