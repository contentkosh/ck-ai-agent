from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from common.logger import logger
from api.dependencies import get_request_context

from dto.request_dto import QueryRequest
from dto.response_dto import QueryResponse

from repositories.kb_repository import (
    get_all_records,
)

from services.kb_chat_service import ask_question

from validators.query_validator import validate_query
from validators.tag_validator import validate_tag


router = APIRouter()


# ==========================================================
# Get Knowledge Base
# ==========================================================

@router.get("/llm/kb")
def get_knowledge_base(
    tag: Optional[str] = Query(default=None),
):
    """
    Retrieve all Knowledge Base records.
    """

    context = get_request_context()

    logger.info(
        "[%s] Fetching Knowledge Base.",
        context.request_id,
    )

    try:

        validate_tag(tag)

        records = get_all_records(tag)

        logger.info(
            "[%s] Retrieved %d record(s).",
            context.request_id,
            len(records),
        )

        return {
            "request_id": context.request_id,
            "total_records": len(records),
            "records": records,
        }

    except HTTPException:
        raise

    except Exception as ex:

        logger.exception(
            "[%s] Failed to fetch Knowledge Base: %s",
            context.request_id,
            ex,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )


# ==========================================================
# Ask Question
# ==========================================================

@router.post(
    "/llm/kb",
    response_model=QueryResponse,
)
def query_knowledge_base(
    request: QueryRequest,
):
    """
    Answer a user query using the Knowledge Base.
    """

    context = get_request_context()

    logger.info(
        "[%s] Question received.",
        context.request_id,
    )

    try:

        validate_query(request.query)

        result = ask_question(request.query)

        logger.info(
            "[%s] Question answered successfully.",
            context.request_id,
        )

        return QueryResponse(
            answer=result.get("answer"),
            title=result.get("title"),
            document_type=result.get("document_type"),
            tag=result.get("tag"),
            summary=result.get("summary"),
            source=result.get("source"),
            page=result.get("page"),
        )

    except HTTPException:
        raise

    except Exception as ex:

        logger.exception(
            "[%s] Failed to process question: %s",
            context.request_id,
            ex,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )