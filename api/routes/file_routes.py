from fastapi import APIRouter, Depends, Query

from api.dependencies import get_request_context, verify_api_key
from common.logger import logger
from configuration.constants import (
    CLEAR_KB_REQUEST_LOG,
    CLEAR_KB_ROUTE,
    CLEAR_KB_SUCCESS_LOG,
    DELETE_DOCUMENT_REQUEST_LOG,
    DELETE_DOCUMENT_ROUTE,
    DELETE_DOCUMENT_SUCCESS_LOG,
    DOCUMENTS_ROUTE,
    DOCUMENT_DELETED_SUCCESS,
    FETCH_UPLOADED_DOCUMENTS_LOG,
    FETCH_UPLOADED_DOCUMENTS_SUCCESS_LOG,
    KNOWLEDGE_BASE_CLEARED_SUCCESS,
    SUCCESS_STATUS,
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


@router.get(
    DOCUMENTS_ROUTE,
    response_model=UploadedDocumentsListResponse,
)
def get_uploaded_documents(
    business_id: str,
    course_ids: list[str] = Query(...),
    context: RequestContext = Depends(get_request_context),
):
    """
    Retrieve all uploaded documents for a specific
    business and any of the specified courses.
    """
    logger.info(
        FETCH_UPLOADED_DOCUMENTS_LOG,
        context.request_id,
    )

    try:
        logger.info(
            "[%s] Uploaded document retrieval started. Business ID=%s | Course IDs=%s",
            context.request_id,
            business_id,
            course_ids,
        )

        uploaded_documents = get_uploaded_documents_service(
            business_id=business_id,
            course_ids=course_ids,
        )

        logger.info(
            "[%s] Uploaded document retrieval completed. Documents=%d",
            context.request_id,
            len(uploaded_documents),
        )

        logger.info(
            FETCH_UPLOADED_DOCUMENTS_SUCCESS_LOG,
            context.request_id,
            len(uploaded_documents),
        )

        return UploadedDocumentsListResponse(
            request_id=context.request_id,
            total_documents=len(uploaded_documents),
            documents=uploaded_documents,
        )

    except Exception:
        logger.exception(
            "[%s] Uploaded document retrieval request failed.",
            context.request_id,
        )
        raise


@router.delete(
    DELETE_DOCUMENT_ROUTE,
    response_model=DeleteDocumentResponse,
    dependencies=[
        Depends(verify_api_key),
    ],
)
def delete_uploaded_document(
    document_id: str,
    business_id: str,
    context: RequestContext = Depends(get_request_context),
):
    """
    Delete a document and all its associated chunks
    from a specific business Knowledge Base.
    """
    logger.info(
        DELETE_DOCUMENT_REQUEST_LOG,
        context.request_id,
        document_id,
    )

    try:
        logger.info(
            "[%s] Document deletion request started. Business ID=%s | Document ID=%s",
            context.request_id,
            business_id,
            document_id,
        )

        delete_document_service(
            documentId=document_id,
            business_id=business_id,
        )

        logger.info(
            "[%s] Document deletion service completed. Document ID=%s",
            context.request_id,
            document_id,
        )

        logger.info(
            DELETE_DOCUMENT_SUCCESS_LOG,
            context.request_id,
        )

        return DeleteDocumentResponse(
            request_id=context.request_id,
            status=SUCCESS_STATUS,
            message=DOCUMENT_DELETED_SUCCESS,
            document_id=document_id,
        )

    except Exception:
        logger.exception(
            "[%s] Document deletion request failed. Document ID=%s",
            context.request_id,
            document_id,
        )
        raise


@router.delete(
    CLEAR_KB_ROUTE,
    response_model=ClearKnowledgeBaseResponse,
    dependencies=[
        Depends(verify_api_key),
    ],
)
def clear_knowledge_base(
    business_id: str,
    context: RequestContext = Depends(get_request_context),
):
    """
    Delete all documents from a specific business
    Knowledge Base.
    """
    logger.info(
        CLEAR_KB_REQUEST_LOG,
        context.request_id,
    )

    try:
        logger.info(
            "[%s] Knowledge Base clearing request started. Business ID=%s",
            context.request_id,
            business_id,
        )

        clear_kb_service(
            business_id=business_id,
        )

        logger.info(
            "[%s] Knowledge Base clearing service completed. Business ID=%s",
            context.request_id,
            business_id,
        )

        logger.info(
            CLEAR_KB_SUCCESS_LOG,
            context.request_id,
        )

        return ClearKnowledgeBaseResponse(
            request_id=context.request_id,
            status=SUCCESS_STATUS,
            message=KNOWLEDGE_BASE_CLEARED_SUCCESS,
        )

    except Exception:
        logger.exception(
            "[%s] Knowledge Base clearing request failed. Business ID=%s",
            context.request_id,
            business_id,
        )
        raise
