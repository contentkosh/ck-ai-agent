from typing import (
    Any,
    Optional,
)
from pydantic import BaseModel

class QueryResponse(BaseModel):
    """
    Response returned by the Knowledge Base.
    """
    answer: str

    document_id: Optional[str] = None

    title: Optional[str] = None

    document_type: Optional[str] = None

    tag: Optional[str] = None

    summary: Optional[str] = None

    source: Optional[str] = None

    page: Optional[int] = None

# ==========================================================
# Get Knowledge Base Response
# ==========================================================

class KnowledgeBaseResponse(BaseModel):
    """
    Response returned when retrieving Knowledge Base records.
    """
    request_id: str

    total_records: int

    records: list[Any]