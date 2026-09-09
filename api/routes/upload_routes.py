import re
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


def normalize_course_ids(
    course_ids: List[str],
) -> List[str]:
    """
    Normalize course IDs received from the upload request.
    Supports repeated, comma-separated, and space-separated IDs.
    """
    normalized_course_ids = []

    for course_id in course_ids:
        normalized_course_ids.extend(
            value
            for value in re.split(
                r"[,\s]+",
                course_id.strip(),
            )
            if value
        )

    return list(
        dict.fromkeys(
            normalized_course_ids,
        )
    )


@router.post(
    UPLOAD_DOCUMENTS_ROUTE,
    dependencies=[Depends(verify_api_key)],
)
def upload_documents(
    business_id: Annotated[str, Form(...)],
    course_ids: Annotated[List[str], Form(...)],
    files: Annotated[List[UploadFile], File(...)],
    context: RequestContext = Depends(
        get_request_context,
    ),
):
    """
    Upload one or more PDF documents into the
    Knowledge Base for one or more courses.
    """
    logger.info(
        UPLOAD_REQUEST_LOG,
        context.request_id,
    )

    validate_upload(files)

    normalized_course_ids = normalize_course_ids(
        course_ids,
    )

    result = ingest_documents(
        files=files,
        business_id=business_id,
        course_ids=normalized_course_ids,
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