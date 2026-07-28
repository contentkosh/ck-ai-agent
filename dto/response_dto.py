from typing import Optional
from pydantic import BaseModel
from configuration.constants import (
    METADATA_DOCUMENT_ID,
    METADATA_DOCUMENT_TYPE,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_SUMMARY,
    METADATA_TAG,
    METADATA_TITLE,
)
from dto.knowledge_base_record_dto import KnowledgeBaseRecordDto

# ==========================================================
# Query Response
# ==========================================================

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

    @classmethod
    def from_payload(
        cls,
        answer: str,
        payload: dict,
    ) -> "QueryResponse":
        """
        Build a QueryResponse from an LLM answer
        and the retrieved document payload.
        """
        return cls(
            answer=answer,
            document_id=payload.get(METADATA_DOCUMENT_ID,),
            title=payload.get(METADATA_TITLE,),
            document_type=payload.get(METADATA_DOCUMENT_TYPE,),
            tag=payload.get(METADATA_TAG,),
            summary=payload.get(METADATA_SUMMARY,),
            source=payload.get(METADATA_SOURCE,),
            page=payload.get(METADATA_PAGE,),
        )

# ==========================================================
# Get Knowledge Base Response
# ==========================================================

class KnowledgeBaseResponse(BaseModel):
    """
    Response returned when retrieving Knowledge Base records.
    """
    request_id: str
    total_records: int
    records: list[KnowledgeBaseRecordDto]
