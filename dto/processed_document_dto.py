from pydantic import BaseModel


class ProcessedDocumentDto(BaseModel):
    document_id: str
    chunks: int
