from typing import Optional
from pydantic import BaseModel


class KnowledgeBaseRecordDto(BaseModel):
    document_id: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None
    text: Optional[str] = None
