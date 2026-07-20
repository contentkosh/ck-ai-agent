from typing import (
    Annotated,
    List,
)
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)
from api.dependencies import get_request_context, verify_api_key
from common.logger import logger
from configuration.constants import UPLOAD_DOCUMENTS_ROUTE
from configuration.context import RequestContext
from services.kb_ingestion_service import ingest_documents
from validators.upload_validator import validate_upload
router = APIRouter()

# ==========================================================
# Upload Documents
# ==========================================================

@router.post(UPLOAD_DOCUMENTS_ROUTE, dependencies=[Depends(verify_api_key)])
def upload_documents(
    files: Annotated[List[UploadFile], File(...)],
    context: RequestContext = Depends(get_request_context),
):
    """
    Upload one or more PDF documents into the Knowledge Base.
    """
    logger.info("[%s] Upload request received.", context.request_id)
    validate_upload(files)
    result = ingest_documents(files)
    logger.info("[%s] Uploaded %d document(s) successfully.",context.request_id, len(files),)
    return {
        "request_id": context.request_id,
        "message": result,
    }