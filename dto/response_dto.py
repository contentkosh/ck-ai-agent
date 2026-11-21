from typing import Any, Optional
from pydantic import BaseModel


class QueryResponse(BaseModel):
    answer: str
    document_id: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None

    @classmethod
    def from_payload(cls, *, answer: str, payload: dict):
        return cls(
            answer=answer,
            document_id=payload.get("document_id"),
            source=payload.get("source"),
            page=payload.get("page"),
        )


class CacheResponse(BaseModel):
    answer: str
    document_id: Optional[str] = None
    source: Optional[str] = None
    page: Optional[int] = None
    similarity_score: Optional[float] = None


class KnowledgeBaseResponse(BaseModel):
    request_id: str
    total_records: int
    records: list[Any]
    similarity_score: Optional[float] = None

class QueryJobResponse(BaseModel):
    job_id: str
    status: str
    result: QueryResponse | None = None
    error: str | None = None