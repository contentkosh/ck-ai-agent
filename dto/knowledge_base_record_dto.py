from typing import Optional
from pydantic import BaseModel

class KnowledgeBaseRecordDto(BaseModel):
    """
    Represents a single Knowledge Base record.
    """
    document_id: Optional[str] = None
    title: Optional[str] = None
    document_type: Optional[str] = None
    tag: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None
    text: Optional[str] = None