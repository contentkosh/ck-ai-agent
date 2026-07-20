from typing import Optional
from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from api.dependencies import get_request_context
from common.logger import logger
from configuration.constants import (
    KNOWLEDGE_BASE_ROUTE,
    QUERY_KNOWLEDGE_BASE_ROUTE,
)
from configuration.context import RequestContext
from dto.request_dto import QueryRequest
from dto.response_dto import (
    KnowledgeBaseResponse,
    QueryResponse,
)
from services.kb_chat_service import ask_question
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
    tag: Optional[str] = Query(default=None),
    context: RequestContext = Depends(get_request_context),
):
    """
    Retrieve all Knowledge Base records.
    """
    logger.info("[%s] Fetching Knowledge Base.",context.request_id,)
    validate_tag(tag)
    records = get_knowledge_base_records(tag)
    logger.info("[%s] Retrieved %d record(s).",context.request_id,len(records),)
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
    context: RequestContext = Depends(get_request_context),
):
    """
    Answer a user query using the Knowledge Base.
    """
    logger.info("[%s] Question received.",context.request_id,)
    validate_query(request.query)
    result = ask_question(request.query)
    logger.info("[%s] Question answered successfully.", context.request_id)
    return QueryResponse(
        answer=result.get("answer"),
        document_id=result.get("document_id"),
        title=result.get("title"),
        document_type=result.get("document_type"),
        tag=result.get("tag"),
        summary=result.get("summary"),
        source=result.get("source"),
        page=result.get("page"),
    )