from fastapi import (
    APIRouter,
    HTTPException,
)

from common.logger import logger

from api.dependencies import get_request_context

from repositories.kb_repository import (
    delete_all_documents,
    delete_document,
    get_uploaded_files,
)

router = APIRouter()

# ==========================================================
# Get Uploaded Documents
# ==========================================================

@router.get("/llm/files")
def get_uploaded_documents():
    """
    Retrieve all uploaded documents.
    """

    context = get_request_context()

    logger.info(
        "[%s] Fetching uploaded documents.",
        context.request_id,
    )

    try:

        documents = get_uploaded_files()

        logger.info(
            "[%s] Retrieved %d uploaded document(s).",
            context.request_id,
            len(documents),
        )

        return {
            "request_id": context.request_id,
            "total_documents": len(documents),
            "documents": documents,
        }

    except Exception as ex:

        logger.exception(
            "[%s] Failed to retrieve uploaded documents: %s",
            context.request_id,
            ex,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )


# ==========================================================
# Delete Uploaded Document
# ==========================================================

@router.delete("/llm/files/{document_id}")
def delete_uploaded_document(
    document_id: str,
):
    """
    Delete a document and all its associated chunks.
    """

    context = get_request_context()

    logger.info(
        "[%s] Delete request received. Document ID=%s",
        context.request_id,
        document_id,
    )

    try:

        delete_document(document_id)

        logger.info(
            "[%s] Document deleted successfully.",
            context.request_id,
        )

        return {
            "request_id": context.request_id,
            "status": "success",
            "message": "Document deleted successfully.",
            "document_id": document_id,
        }

    except Exception as ex:

        logger.exception(
            "[%s] Failed to delete document: %s",
            context.request_id,
            ex,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )


# ==========================================================
# Clear Knowledge Base
# ==========================================================

@router.delete("/llm/files")
def clear_knowledge_base():
    """
    Delete all documents from the Knowledge Base.
    """

    context = get_request_context()

    logger.info(
        "[%s] Clearing Knowledge Base.",
        context.request_id,
    )

    try:

        delete_all_documents()

        logger.info(
            "[%s] Knowledge Base cleared successfully.",
            context.request_id,
        )

        return {
            "request_id": context.request_id,
            "status": "success",
            "message": "Knowledge Base cleared successfully.",
        }

    except Exception as ex:

        logger.exception(
            "[%s] Failed to clear Knowledge Base: %s",
            context.request_id,
            ex,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )