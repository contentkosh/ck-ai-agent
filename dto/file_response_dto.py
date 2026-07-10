from typing import Any
from pydantic import BaseModel

class UploadedDocumentsResponse(BaseModel):
    request_id: str
    total_documents: int
    documents: list[Any]

class DeleteDocumentResponse(BaseModel):
    request_id: str
    status: str
    message: str
    document_id: str

class ClearKnowledgeBaseResponse(BaseModel):
    request_id: str
    status: str
    message: str