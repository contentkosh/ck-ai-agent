from fastapi import (
    APIRouter,
    Depends,
)

from api.dependencies import get_request_context
from common.logger import logger
from configuration.context import RequestContext

from dto.file_response_dto import (
    ClearKnowledgeBaseResponse,
    DeleteDocumentResponse,
    UploadedDocumentsResponse,
)

from services.file_service import (
    clear_knowledge_base as clear_kb_service,
    delete_uploaded_document as delete_document_service,
    get_uploaded_documents as get_uploaded_documents_service,
)

router = APIRouter()

# ==========================================================
# Get Uploaded Documents
# ==========================================================

@router.get(
    "/llm/files",
    response_model=UploadedDocumentsResponse,
)
def get_uploaded_documents(
    context: RequestContext = Depends(get_request_context),
):
    """
    Retrieve all uploaded documents.
    """
    logger.info("[%s] Fetching uploaded documents.", context.request_id)

    documents = get_uploaded_documents_service()

    logger.info("[%s] Retrieved %d uploaded document(s).",context.request_id, len(documents),)

    return UploadedDocumentsResponse(
        request_id=context.request_id,
        total_documents=len(documents),
        documents=documents,
    )

# ==========================================================
# Delete Uploaded Document
# ==========================================================

@router.delete(
    "/llm/files/{document_id}",
    response_model=DeleteDocumentResponse,
)
def delete_uploaded_document(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
):
    """
    Delete a document and all its associated chunks.
    """
    logger.info("[%s] Delete request received. Document ID=%s",context.request_id,document_id,)

    delete_document_service(document_id)

    logger.info("[%s] Document deleted successfully.",context.request_id,)

    return DeleteDocumentResponse(
        request_id=context.request_id,
        status="success",
        message="Document deleted successfully.",
        document_id=document_id,
    )

# ==========================================================
# Clear Knowledge Base
# ==========================================================

@router.delete(
    "/llm/files",
    response_model=ClearKnowledgeBaseResponse,
)
def clear_knowledge_base(
    context: RequestContext = Depends(get_request_context),
):
    """
    Delete all documents from the Knowledge Base.
    """
    logger.info("[%s] Clearing Knowledge Base.",context.request_id,)

    clear_kb_service()

    logger.info("[%s] Knowledge Base cleared successfully.",context.request_id,)

    return ClearKnowledgeBaseResponse(
        request_id=context.request_id,
        status="success",
        message="Knowledge Base cleared successfully.",
    )