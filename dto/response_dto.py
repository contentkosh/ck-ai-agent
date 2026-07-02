from typing import Optional

from pydantic import BaseModel


class QueryResponse(BaseModel):
    answer: str

    document_id: Optional[str] = None

    title: Optional[str] = None

    document_type: Optional[str] = None

    tag: Optional[str] = None

    summary: Optional[str] = None

    source: Optional[str] = None

    page: Optional[int] = None

    similarity_score: Optional[float] = None