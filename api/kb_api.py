from typing import List, Optional

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile
)

from configuration.constants import (
    API_TITLE,
    API_VERSION
)

from configuration.context import RequestContext

from dto.request_dto import QueryRequest
from dto.response_dto import QueryResponse

from services.kb_chat_service import ask_question
from services.kb_ingestion_service import ingest_documents

from repositories.kb_repository import (
    get_all_records,
    get_uploaded_files,
    delete_document,
    delete_all_documents
)

from common.validators import (
    validate_pdf,
    validate_query,
    validate_tag
)

from common.logger import logger


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(

    title=API_TITLE,

    version=API_VERSION

)

# ==========================================================
# Request Context
# ==========================================================

def get_request_context() -> RequestContext:
    """Create a request context."""

    return RequestContext()

# ==========================================================
# Health Check
# ==========================================================

@app.get("/")
def health_check():

    logger.info(
        "Health Check API called."
    )

    return {

        "status": "Running",

        "service": API_TITLE,

        "version": API_VERSION

    }
# ==========================================================
# Get Knowledge Base
# ==========================================================

@app.get("/llm/kb")
def get_knowledge_base(

    tag: Optional[str] = Query(default=None)

):

    context = get_request_context()

    logger.info(

        "[%s] Fetching Knowledge Base.",
        context.request_id,

    )

    try:

        validate_tag(tag)

        records = get_all_records(tag)

        logger.info(

            "[%s] record(s) retrieved.",
            context.request_id,

        )

        return {

            "request_id": context.request_id,

            "total_records": len(records),

            "records": records

        }

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


# ==========================================================
# Ask Question
# ==========================================================

@app.post(

    "/llm/kb",

    response_model=QueryResponse

)
def query_knowledge_base(

    request: QueryRequest

):

    context = get_request_context()

    logger.info(

        "[%s] Question received.",
        context.request_id,

    )

    try:

        validate_query(

            request.query

        )

        result = ask_question(

            request.query

        )

        logger.info(

            "[%s] Question answered successfully.",
            context.request_id

        )

        return QueryResponse(

            answer=result.get("answer"),

            title=result.get("title"),

            document_type=result.get(
                "document_type"
            ),

            tag=result.get(
                "tag"
            ),

            summary=result.get(
                "summary"
            ),

            source=result.get(
                "source"
            ),

            page=result.get(
                "page"
            )

        )

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

# ==========================================================
# Upload Documents
# ==========================================================

@app.post("/llm/upload")
def upload_documents(

    files: List[UploadFile] = File(...)

):

    context = get_request_context()

    logger.info(

        "[%s] Upload request received.",
        context.request_id

    )

    try:

        if not files:

            raise HTTPException(

                status_code=400,

                detail="No files uploaded."

            )

        for file in files:

            validate_pdf(file)

        result = ingest_documents(

            files

        )

        logger.info(

            "[%s] Upload completed successfully.",
            context.request_id,

        )

        return {

            "request_id": context.request_id,

            "message": result

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

# ==========================================================
# Get Uploaded Documents
# ==========================================================

@app.get("/llm/files")
def get_uploaded_documents():

    context = get_request_context()

    logger.info(

        "[%s] Fetching uploaded documents.",
        context.request_id
    
    )

    try:

        documents = get_uploaded_files()

        logger.info(

            "[%s] %d document(s) found.",
            context.request_id,
            len(documents)
        )

        return {

            "request_id": context.request_id,

            "total_documents": len(documents),

            "documents": documents

        }

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
    # ==========================================================
# Delete One Document
# ==========================================================

@app.delete("/llm/files/{document_id}")
def delete_uploaded_document(
    document_id: str
):

    context = get_request_context()

    logger.info(
        "[%s] Delete request for document: %s",
        context.request_id,
        document_id
    )

    try:

        delete_document(document_id)

        logger.info(
            "[%s] Document deleted successfully.",
            context.request_id
        )

        return {

            "request_id": context.request_id,

            "status": "success",

            "message": "Document deleted successfully.",

            "document_id": document_id

        }

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


# ==========================================================
# Delete Entire Knowledge Base
# ==========================================================

@app.delete("/llm/files")
def clear_knowledge_base():

    context = get_request_context()
    logger.info(
        "[%s] Clearing Knowledge Base.",
        context.request_id
    )

    try:

        delete_all_documents()

        logger.info(
            "[%s] Knowledge Base cleared.",
            context.request_id,
        )

        return {

            "request_id": context.request_id,

            "status": "success",

            "message": "Knowledge Base cleared successfully."

        }

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