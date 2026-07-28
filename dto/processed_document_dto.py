from pydantic import BaseModel
from qdrant_client.models import PointStruct
from dto.document_metadata_dto import DocumentMetadataDto

class ProcessedDocumentDto(BaseModel):
    document_id: str
    metadata: DocumentMetadataDto
    points: list[PointStruct]
    chunks: int
    model_config = {
        "arbitrary_types_allowed": True,
    }