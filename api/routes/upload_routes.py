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


def normalize_course_ids(course_ids: List[str]) -> List[str]:
    normalized_course_ids = []

    for course_id in course_ids:
        normalized_course_ids.extend(
            value for value in re.split(r"[,\s]+", course_id.strip()) if value
        )

    return list(dict.fromkeys(normalized_course_ids))


@router.post(
    UPLOAD_DOCUMENTS_ROUTE,
    dependencies=[Depends(verify_api_key)],
)
def upload_documents(
    business_id: Annotated[str, Form(...)],
    course_ids: Annotated[List[str], Form(...)],
    files: Annotated[List[UploadFile], File(...)],
    context: RequestContext = Depends(get_request_context),
):
    logger.info(
        UPLOAD_REQUEST_LOG,
        context.request_id,
    )

    try:
        logger.info(
            "[%s] Upload validation started. Files=%d",
            context.request_id,
            len(files),
        )
        validate_upload(files)
        logger.info(
            "[%s] Upload validation completed successfully.",
            context.request_id,
        )

        normalized_course_ids = normalize_course_ids(course_ids)
        logger.info(
            "[%s] Course IDs normalized. Count=%d",
            context.request_id,
            len(normalized_course_ids),
        )

        logger.info(
            "[%s] Document ingestion started. Files=%d",
            context.request_id,
            len(files),
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
    except Exception:
        logger.exception(
            "[%s] Upload request failed.",
            context.request_id,
        )
        raise
