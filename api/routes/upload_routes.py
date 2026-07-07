from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from common.logger import logger
from api.dependencies import get_request_context

from services.kb_ingestion_service import ingest_documents

from validators.upload_validator import validate_upload


router = APIRouter()



# ==========================================================
# Upload Documents
# ==========================================================

@router.post("/llm/upload")
def upload_documents(
    files: list[UploadFile] = File(...),
):
    """
    Upload one or more PDF documents into the Knowledge Base.
    """

    context = get_request_context()

    logger.info(
        "[%s] Upload request received.",
        context.request_id,
    )

    try:

        validate_upload(files)

        result = ingest_documents(files)

        logger.info(
            "[%s] Uploaded %d document(s) successfully.",
            context.request_id,
            len(files),
        )

        return {
            "request_id": context.request_id,
            "message": result,
        }

    except HTTPException:
        raise

    except Exception as ex:

        logger.exception(
            "[%s] Upload failed: %s",
            context.request_id,
            ex,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )