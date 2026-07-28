from pydantic import BaseModel

# ==========================================================
# Uploaded Document
# ==========================================================

class UploadedDocumentDto(BaseModel):
    """
    Metadata returned for an uploaded document.
    """
    title: str | None = None
    document_type: str | None = None
    tag: str | None = None
    summary: str | None = None
    source: str | None = None

# ==========================================================
# Get Uploaded Documents Response
# ==========================================================

class UploadedDocumentsListResponse(BaseModel):
    """
    Response returned when fetching uploaded documents.
    """
    request_id: str
    total_documents: int
    documents: list[UploadedDocumentDto]
    
# ==========================================================
# Upload Documents Response
# ==========================================================

class UploadedDocumentsResponse(BaseModel):
    """
    Response returned after uploading documents.
    """
    status: str
    documents_processed: int
    chunks_inserted: int
    documents: list[UploadedDocumentDto]

# ==========================================================
# Delete Document Response
# ==========================================================

class DeleteDocumentResponse(BaseModel):
    request_id: str
    status: str
    message: str
    document_id: str

# ==========================================================
# Clear Knowledge Base Response
# ==========================================================

class ClearKnowledgeBaseResponse(BaseModel):
    request_id: str
    status: str
    message: str