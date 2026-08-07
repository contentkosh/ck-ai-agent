from pydantic import BaseModel
class DocumentMetadataDto(BaseModel):
    title: str
    document_type: str
    tag: str
    summary: str