from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, UploadFile

from api.dependencies import get_request_context, verify_api_key
from common.logger import logger
from configuration.constants import (
    UPLOAD_DOCUMENTS_ROUTE,
    UPLOAD_REQUEST_LOG,
    UPLOAD_SUCCESS_LOG,
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
    dependencies=[Depends(verify_api_key)],
)
def upload_documents(
    business_id: Annotated[str, Form(...)],
    course_id: Annotated[str, Form(...)],
    files: Annotated[List[UploadFile], File(...)],
    context: RequestContext = Depends(get_request_context),
):
    """Upload one or more PDF documents into the Knowledge Base."""

    logger.info(
        UPLOAD_REQUEST_LOG,
        context.request_id,
    )

    validate_upload(files)

    result = ingest_documents(
        files=files,
        business_id=business_id,
        course_id=course_id,
    )

    logger.info(
        UPLOAD_SUCCESS_LOG,
        context.request_id,
        len(files),
    )

    return {
        "request_id": context.request_id,
        "message": result,
    }