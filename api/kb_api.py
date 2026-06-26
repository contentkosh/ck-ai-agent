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

    context = RequestContext()

    logger.info(

        f"[{context.request_id}] Fetching Knowledge Base."

    )

    try:

        validate_tag(tag)

        records = get_all_records(tag)

        logger.info(

            f"[{context.request_id}] "

            f"{len(records)} record(s) retrieved."

        )

        return {

            "request_id": context.request_id,

            "total_records": len(records),

            "records": records

        }

    except Exception as e:

        logger.exception(

            f"[{context.request_id}] "

            f"Failed to fetch Knowledge Base."

        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

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

    context = RequestContext()

    logger.info(

        f"[{context.request_id}] "

        f"Question received."

    )

    try:

        validate_query(

            request.query

        )

        result = ask_question(

            request.query

        )

        logger.info(

            f"[{context.request_id}] "

            f"Question answered successfully."

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

    except Exception as e:

        logger.exception(

            f"[{context.request_id}] "

            f"Query failed."

        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
    # ==========================================================
# Upload Documents
# ==========================================================

@app.post("/llm/upload")
def upload_documents(

    files: List[UploadFile] = File(...)

):

    context = RequestContext()

    logger.info(

        f"[{context.request_id}] Upload request received."

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

            f"[{context.request_id}] "

            f"Upload completed successfully."

        )

        return {

            "request_id": context.request_id,

            "message": result

        }

    except HTTPException:

        raise

    except Exception as e:

        logger.exception(

            f"[{context.request_id}] Upload failed."

        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ==========================================================
# Get Uploaded Documents
# ==========================================================

@app.get("/llm/files")
def get_uploaded_documents():

    context = RequestContext()

    logger.info(

        f"[{context.request_id}] Fetching uploaded documents."

    )

    try:

        documents = get_uploaded_files()

        logger.info(

            f"[{context.request_id}] "

            f"{len(documents)} document(s) found."

        )

        return {

            "request_id": context.request_id,

            "total_documents": len(documents),

            "documents": documents

        }

    except Exception as e:

        logger.exception(

            f"[{context.request_id}] "

            f"Unable to retrieve uploaded documents."

        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
    # ==========================================================
# Delete One Document
# ==========================================================

@app.delete("/llm/files/{document_id}")
def delete_uploaded_document(
    document_id: str
):

    context = RequestContext()

    logger.info(
        f"[{context.request_id}] Delete request for document: {document_id}"
    )

    try:

        delete_document(document_id)

        logger.info(
            f"[{context.request_id}] Document deleted successfully."
        )

        return {

            "request_id": context.request_id,

            "status": "success",

            "message": "Document deleted successfully.",

            "document_id": document_id

        }

    except Exception as e:

        logger.exception(
            f"[{context.request_id}] Failed to delete document."
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ==========================================================
# Delete Entire Knowledge Base
# ==========================================================

@app.delete("/llm/files")
def clear_knowledge_base():

    context = RequestContext()

    logger.info(
        f"[{context.request_id}] Clearing Knowledge Base."
    )

    try:

        delete_all_documents()

        logger.info(
            f"[{context.request_id}] Knowledge Base cleared."
        )

        return {

            "request_id": context.request_id,

            "status": "success",

            "message": "Knowledge Base cleared successfully."

        }

    except Exception as e:

        logger.exception(
            f"[{context.request_id}] Failed to clear Knowledge Base."
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )