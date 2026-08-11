from typing import Annotated, List
from fastapi import APIRouter, Depends, File, UploadFile
from api.dependencies import get_request_context, require_permission
from common.logger import logger
from configuration.constants import (
    UPLOAD_DOCUMENTS_ROUTE,
    UPLOAD_REQUEST_LOG,
    UPLOAD_SUCCESS_LOG,
    UPLOAD_DOCUMENTS_PERMISSION,
)
from configuration.context import RequestContext
from services.kb_ingestion_service import ingest_documents
from validators.upload_validator import validate_upload

router = APIRouter()

# ==========================================================
# Upload Documents
# ==========================================================

@router.post(
    UPLOAD_DOCUMENTS_ROUTE,
    dependencies=[
        Depends(
            require_permission(UPLOAD_DOCUMENTS_PERMISSION)
        )
    ],
)

def upload_documents(
    files: Annotated[List[UploadFile], File(...)],
    context: RequestContext = Depends(get_request_context),
):
    """
    Upload one or more PDF documents into the Knowledge Base.
    """
    logger.info(UPLOAD_REQUEST_LOG, context.request_id)
    validate_upload(files)
    result = ingest_documents(files)
    logger.info(UPLOAD_SUCCESS_LOG, context.request_id, len(files))
    return {
        "request_id": context.request_id,
        "message": result,
    }