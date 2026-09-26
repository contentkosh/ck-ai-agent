import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_request_context
from common.logger import logger
from configuration.constants import (
    FETCH_KB_REQUEST_LOG,
    FETCH_KB_SUCCESS_LOG,
    KNOWLEDGE_BASE_ROUTE,
    QUERY_KNOWLEDGE_BASE_ROUTE,
    QUERY_REQUEST_LOG,
    QUERY_SUCCESS_LOG,
)
from configuration.context import RequestContext
from dto.request_dto import QueryRequest
from dto.response_dto import KnowledgeBaseResponse, QueryJobResponse, QueryResponse
from services.kb_service import get_knowledge_base_records
from services.query_job_manager import query_job_manager
from validators.query_validator import validate_query
from validators.tag_validator import validate_tag

router = APIRouter()


@router.get(
    KNOWLEDGE_BASE_ROUTE,
    response_model=KnowledgeBaseResponse,
)
def get_knowledge_base(
    business_id: str,
    course_ids: List[str] = Query(...),
    tag: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
) -> KnowledgeBaseResponse:
    """Retrieve all Knowledge Base records."""

    logger.info(
        FETCH_KB_REQUEST_LOG,
        context.request_id,
    )

    try:
        logger.info(
            "[%s] Knowledge Base retrieval started. Business ID=%s | Course IDs=%s | Tag=%s",
            context.request_id,
            business_id,
            course_ids,
            tag,
        )

        logger.info(
            "[%s] Knowledge Base tag validation started.",
            context.request_id,
        )

        validate_tag(tag)

        logger.info(
            "[%s] Knowledge Base tag validation completed.",
            context.request_id,
        )

        logger.info(
            "[%s] Knowledge Base service call started.",
            context.request_id,
        )

        records = get_knowledge_base_records(
            business_id=business_id,
            course_ids=course_ids,
            tag=tag,
        )

        logger.info(
            "[%s] Knowledge Base service call completed. Records=%d",
            context.request_id,
            len(records),
        )

        logger.info(
            FETCH_KB_SUCCESS_LOG,
            context.request_id,
            len(records),
        )

        return KnowledgeBaseResponse(
            request_id=context.request_id,
            total_records=len(records),
            records=records,
        )

    except Exception:
        logger.exception(
            "[%s] Knowledge Base retrieval request failed.",
            context.request_id,
        )
        raise


@router.post(
    QUERY_KNOWLEDGE_BASE_ROUTE,
    response_model=QueryResponse,
)
def query_knowledge_base(
    request: QueryRequest,
    context: RequestContext = Depends(get_request_context),
) -> QueryResponse:
    """Answer a user query using the Knowledge Base."""

    request_start = time.perf_counter()

    logger.info(
        QUERY_REQUEST_LOG,
        context.request_id,
    )

    try:
        logger.info(
            "[%s] Knowledge Base query started. Business ID=%s | Course IDs=%s",
            context.request_id,
            request.business_id,
            request.course_ids,
        )

        validation_start = time.perf_counter()

        logger.info(
            "[%s] Query validation started.",
            context.request_id,
        )

        validate_query(
            request.query,
        )

        logger.info(
            "[%s] Query validation completed.",
            context.request_id,
        )

        logger.info(
            "[%s] Query validation duration: %.4f seconds",
            context.request_id,
            time.perf_counter() - validation_start,
        )

        logger.info(
            "[%s] Query job creation started.",
            context.request_id,
        )

        job_id = query_job_manager.create_job(
            query=request.query,
            business_id=request.business_id,
            course_ids=request.course_ids,
        )

        logger.info(
            "[%s] Query job created successfully. job_id=%s",
            context.request_id,
            job_id,
        )

        logger.info(
            "[%s] Waiting for query job result. job_id=%s",
            context.request_id,
            job_id,
        )

        result = query_job_manager.wait_for_result(job_id)

        job_status = query_job_manager.get_status(job_id)

        if job_status is None:
            raise HTTPException(
                status_code=500,
                detail="Query job was lost.",
            )

        if job_status["status"] == "cancelled":
            raise HTTPException(
                status_code=409,
                detail=f"Query job cancelled. job_id={job_id}",
            )

        if job_status["status"] == "failed":
            raise HTTPException(
                status_code=500,
                detail=job_status["error"] or "Query job failed.",
            )

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Query job completed without a result.",
            )

        logger.info(
            QUERY_SUCCESS_LOG,
            context.request_id,
        )

        logger.info(
            "[%s] API query request completed. job_id=%s Total duration=%.4f seconds",
            context.request_id,
            job_id,
            time.perf_counter() - request_start,
        )

        return result

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "[%s] Knowledge Base query request failed. Total duration=%.4f seconds",
            context.request_id,
            time.perf_counter() - request_start,
        )
        raise


@router.post(
    "/query/{job_id}/stop",
    response_model=QueryJobResponse,
)
def stop_query_job(
    job_id: str,
) -> QueryJobResponse:
    """Stop a running Knowledge Base query job."""

    result = query_job_manager.get_status(job_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Query job not found",
        )

    query_job_manager.stop_job(job_id)

    result = query_job_manager.get_status(job_id)

    return QueryJobResponse(**result)
