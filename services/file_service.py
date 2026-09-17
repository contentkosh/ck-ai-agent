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
    CACHE_DOCUMENT_INVALIDATION_FAILED_LOG,
    CACHE_CLEAR_FAILED_LOG,
)

from exceptions.knowledge_base_exception import (
    KnowledgeBaseException,
)

from exceptions.contentkosh_exception import (
    ContentKoshException,
)

from dto.file_response_dto import (
    UploadedDocumentDto,
)

from exceptions.qdrant_exception import (
    QdrantConnectionException,
)

from repositories.kb_repository import (
    deleteAllDocuments,
    deleteDocument,
    getUploadedFiles,
    getCourseIdsForDocument,
)

from repositories.cache_repository import (
    delete_cache_for_document,
    delete_all_cache,
)


# ==========================================================
# Get Uploaded Documents
# ==========================================================

def get_uploaded_documents(
    business_id: str,
    course_ids: list[str],
) -> list[UploadedDocumentDto]:
    """
    Retrieve uploaded documents for a specific business
    and any of the specified courses.
    """
    try:
        return getUploadedFiles(
            businessId=business_id,
            courseIds=course_ids,
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
    Delete a single uploaded document and its associated
    cache entries.
    """
    try:
        course_ids = getCourseIdsForDocument(
            documentId=documentId,
            businessId=business_id,
        )

        deleted = deleteDocument(
            documentId=documentId,
            businessId=business_id,
        )

        if deleted and course_ids:
            try:
                delete_cache_for_document(
                    business_id=business_id,
                    course_ids=course_ids,
                    document_id=documentId,
                )
            except Exception as ex:
                logger.exception(
                    CACHE_DOCUMENT_INVALIDATION_FAILED_LOG,
                    documentId,
                    ex,
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
    Remove all uploaded documents and cached answers
    belonging to a specific business.
    """
    try:
        deleted = deleteAllDocuments(
            businessId=business_id,
        )

        if deleted:
            try:
                delete_all_cache(
                    business_id=business_id,
                )
            except Exception as ex:
                logger.exception(
                    CACHE_CLEAR_FAILED_LOG,
                    business_id,
                    ex,
                )

        return deleted

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