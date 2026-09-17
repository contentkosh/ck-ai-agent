from typing import List, Optional
from fastapi import APIRouter, Depends, Query
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
from dto.response_dto import (
    KnowledgeBaseResponse,
    QueryResponse,
)
from services.kb_query_service import ask_question
from services.kb_service import get_knowledge_base_records
from validators.query_validator import validate_query
from validators.tag_validator import validate_tag

router = APIRouter()


# ==========================================================
# Get Knowledge Base
# ==========================================================

@router.get(
    KNOWLEDGE_BASE_ROUTE,
    response_model=KnowledgeBaseResponse,
)
def get_knowledge_base(
    business_id: str,
    course_ids: List[str] = Query(...),
    tag: Optional[str] = Query(default=None),
    context: RequestContext = Depends(
        get_request_context,
    ),
) -> KnowledgeBaseResponse:
    """Retrieve all Knowledge Base records."""

    logger.info(
        FETCH_KB_REQUEST_LOG,
        context.request_id,
    )
    validate_tag(tag)
    records = get_knowledge_base_records(
        business_id=business_id,
        course_ids=course_ids,
        tag=tag,
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


# ==========================================================
# Ask Question
# ==========================================================

@router.post(
    QUERY_KNOWLEDGE_BASE_ROUTE,
    response_model=QueryResponse,
)
def query_knowledge_base(
    request: QueryRequest,
    context: RequestContext = Depends(
        get_request_context,
    ),
) -> QueryResponse:
    """Answer a user query using the Knowledge Base."""

    logger.info(
        QUERY_REQUEST_LOG,
        context.request_id,
    )
    validate_query(request.query)
    result = ask_question(
        query=request.query,
        business_id=request.business_id,
        course_ids=request.course_ids,
    )
    logger.info(
        QUERY_SUCCESS_LOG,
        context.request_id,
    )
    return result