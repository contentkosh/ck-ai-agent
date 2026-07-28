from pydantic import BaseModel

class DocumentPayloadDto(BaseModel):
    document_id: str | None = None
    title: str | None = None
    document_type: str | None = None
    tag: str | None = None
    summary: str | None = None
    source: str | None = None
    page: int | None = None
    text: str | None = None