from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from api.dependencies import get_request_context, verify_api_key
from common.logger import logger
from configuration.constants import UPLOAD_DOCUMENTS_ROUTE, UPLOAD_REQUEST_LOG
from configuration.context import RequestContext
from services.kb_ingestion_service import ingest_documents
from validators.upload_validator import validate_upload

router = APIRouter()


@router.post(UPLOAD_DOCUMENTS_ROUTE, dependencies=[Depends(verify_api_key)])
def upload_documents(
    business_id: Annotated[str, Form(...)],
    course_ids: Annotated[List[str], Form(...)],
    files: Annotated[List[UploadFile], File(...)],
    context: RequestContext = Depends(get_request_context),
):
    logger.info(UPLOAD_REQUEST_LOG, context.request_id)
    try:
        logger.info(
            "[%s] Upload validation started. Files=%d", context.request_id, len(files)
        )
        validate_upload(files)
        logger.info(
            "[%s] Upload validation completed successfully.", context.request_id
        )

        raw_course_ids = [
            course_id for value in course_ids for course_id in value.split(",")
        ]
        normalized_course_ids = list(
            dict.fromkeys(
                course_id.strip() for course_id in raw_course_ids if course_id.strip()
            )
        )

        if not normalized_course_ids:
            raise HTTPException(
                status_code=422, detail="Provide at least one valid course ID."
            )

        if any(
            any(char.isspace() for char in course_id)
            for course_id in normalized_course_ids
        ):
            raise HTTPException(
                status_code=422, detail="Course IDs must not contain whitespace."
            )

        logger.info(
            "[%s] Document ingestion started. Files=%d | Course IDs=%s",
            context.request_id,
            len(files),
            normalized_course_ids,
        )

        result = ingest_documents(
            files=files,
            business_id=business_id,
            course_ids=normalized_course_ids,
        )

        logger.info("[%s] Upload response: %s", context.request_id, result.model_dump())
        return {"request_id": context.request_id, **result.model_dump()}
    except Exception:
        logger.exception("[%s] Upload request failed.", context.request_id)
        raise
