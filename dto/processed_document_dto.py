from pydantic import BaseModel
from dto.document_metadata_dto import DocumentMetadataDto

class ProcessedDocumentDto(BaseModel):
    document_id: str
    metadata: DocumentMetadataDto
    chunks: int