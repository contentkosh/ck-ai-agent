# ==========================================================
# File Service
# Handles uploaded document operations by interacting with
# the Knowledge Base repository.
# ==========================================================

from common.logger import logger

from configuration.constants import (
    DELETE_DOCUMENT_FAILED_LOG,
    CLEAR_KNOWLEDGE_BASE_FAILED_LOG,
    FETCH_UPLOADED_DOCUMENTS_FAILED_LOG,
)

from exceptions.knowledge_base_exception import (
    KnowledgeBaseException,
)

from exceptions.contentkosh_exception import (
    ContentKoshException,
)

from repositories.kb_repository import (
    deleteAllDocuments,
    deleteDocument,
    getUploadedFiles,
)

from dto.file_response_dto import (
    UploadedDocumentDto,
)

from exceptions.qdrant_exception import (
    QdrantConnectionException,
)


# ==========================================================
# Get Uploaded Documents
# ==========================================================

def get_uploaded_documents(
    business_id: str,
    course_id: str,
) -> list[UploadedDocumentDto]:
    """
    Retrieve uploaded documents for a specific business and course.
    """
    try:
        return getUploadedFiles(
            businessId=business_id,
            courseId=course_id,
        )

    except ContentKoshException as ex:
        logger.exception(
            FETCH_UPLOADED_DOCUMENTS_FAILED_LOG,
            ex,
        )

        if isinstance(
            ex.cause,
            QdrantConnectionException,
        ):
            raise ex.cause

        raise KnowledgeBaseException() from ex


# ==========================================================
# Delete Uploaded Document
# ==========================================================

def delete_uploaded_document(
    documentId: str,
    business_id: str,
):
    """
    Delete a single uploaded document from a specific
    business Knowledge Base.
    """
    try:
        deleted = deleteDocument(
            documentId=documentId,
            businessId=business_id,
        )

        return deleted

    except ContentKoshException as ex:
        logger.exception(
            DELETE_DOCUMENT_FAILED_LOG,
            ex,
        )

        if isinstance(
            ex.cause,
            QdrantConnectionException,
        ):
            raise ex.cause

        raise KnowledgeBaseException() from ex


# ==========================================================
# Clear Knowledge Base
# ==========================================================

def clear_knowledge_base(
    business_id: str,
):
    """
    Remove all uploaded documents belonging to a specific
    business.
    """
    try:
        return deleteAllDocuments(
            businessId=business_id,
        )

    except ContentKoshException as ex:
        logger.exception(
            CLEAR_KNOWLEDGE_BASE_FAILED_LOG,
            ex,
        )

        if isinstance(
            ex.cause,
            QdrantConnectionException,
        ):
            raise ex.cause

        raise KnowledgeBaseException() from ex