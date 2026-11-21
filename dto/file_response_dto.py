from pydantic import BaseModel


class UploadedDocumentDto(BaseModel):
    """Basic information returned for an uploaded document."""
    document_id: str | None = None
    source: str | None = None


class UploadedDocumentErrorDto(BaseModel):
    """Error returned for a document that failed during upload."""
    source: str
    error: str


class UploadedDocumentsListResponse(BaseModel):
    """Response returned when fetching uploaded documents."""
    request_id: str
    total_documents: int
    documents: list[UploadedDocumentDto]


class UploadedDocumentsResponse(BaseModel):
    """Response returned after uploading documents."""
    status: str
    message: str
    documents_processed: int
    documents_failed: int
    chunks_inserted: int
    documents: list[UploadedDocumentDto]
    errors: list[UploadedDocumentErrorDto]


class DeleteDocumentResponse(BaseModel):
    request_id: str
    status: str
    message: str
    document_id: str


class ClearKnowledgeBaseResponse(BaseModel):
    request_id: str
    status: str
    message: str