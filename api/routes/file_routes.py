from fastapi import (APIRouter,Depends,)
from api.dependencies import get_request_context, verify_api_key
from common.logger import logger
from configuration.constants import (
    DOCUMENTS_ROUTE,
    DELETE_DOCUMENT_ROUTE,
    CLEAR_KB_ROUTE,
    FETCH_UPLOADED_DOCUMENTS_LOG,
    FETCH_UPLOADED_DOCUMENTS_SUCCESS_LOG,
    DELETE_DOCUMENT_REQUEST_LOG,
    DELETE_DOCUMENT_SUCCESS_LOG,
    CLEAR_KB_REQUEST_LOG,
    CLEAR_KB_SUCCESS_LOG,
    SUCCESS_STATUS,
    DOCUMENT_DELETED_SUCCESS,
    KNOWLEDGE_BASE_CLEARED_SUCCESS,
)

from configuration.context import RequestContext
from dto.file_response_dto import (
    ClearKnowledgeBaseResponse,
    DeleteDocumentResponse,
    UploadedDocumentsListResponse,
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
    DOCUMENTS_ROUTE,
    response_model=UploadedDocumentsListResponse,
)
def get_uploaded_documents(
    context: RequestContext = Depends(get_request_context),
):
    """
    Retrieve all uploaded documents.
    """
    logger.info(FETCH_UPLOADED_DOCUMENTS_LOG,context.request_id,)
    uploaded_documents = get_uploaded_documents_service()
    logger.info(FETCH_UPLOADED_DOCUMENTS_SUCCESS_LOG,context.request_id,len(uploaded_documents),)
    return UploadedDocumentsListResponse(
        request_id=context.request_id,
        total_documents=len(uploaded_documents),
        documents=uploaded_documents,
    )

# ==========================================================
# Delete Uploaded Document
# ==========================================================

@router.delete(DELETE_DOCUMENT_ROUTE,response_model=DeleteDocumentResponse,dependencies=[Depends(verify_api_key)],)
def delete_uploaded_document(
    document_id: str,
    context: RequestContext = Depends(get_request_context),
):
    """
    Delete a document and all its associated chunks.
    """
    logger.info(DELETE_DOCUMENT_REQUEST_LOG,context.request_id,document_id,)
    delete_document_service(document_id)
    logger.info(DELETE_DOCUMENT_SUCCESS_LOG,context.request_id,)
    return DeleteDocumentResponse(
        request_id=context.request_id,
        status=SUCCESS_STATUS,
        message=DOCUMENT_DELETED_SUCCESS,
        document_id=document_id,
    )

# ==========================================================
# Clear Knowledge Base
# ==========================================================

@router.delete(CLEAR_KB_ROUTE,response_model=ClearKnowledgeBaseResponse,dependencies=[Depends(verify_api_key)],)
def clear_knowledge_base(
    context: RequestContext = Depends(get_request_context),
):
    """
    Delete all documents from the Knowledge Base.
    """
    logger.info(CLEAR_KB_REQUEST_LOG,context.request_id,)
    clear_kb_service()
    logger.info(CLEAR_KB_SUCCESS_LOG,context.request_id,)
    return ClearKnowledgeBaseResponse(
        request_id=context.request_id,
        status=SUCCESS_STATUS,
        message=KNOWLEDGE_BASE_CLEARED_SUCCESS,
    )