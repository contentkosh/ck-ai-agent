from common.logger import logger
from configuration.constants import (
    CACHE_CLEAR_FAILED_LOG,
    CACHE_DOCUMENT_INVALIDATION_FAILED_LOG,
    CLEAR_KNOWLEDGE_BASE_FAILED_LOG,
    DELETE_DOCUMENT_FAILED_LOG,
    FETCH_UPLOADED_DOCUMENTS_FAILED_LOG,
)
from dto.file_response_dto import UploadedDocumentDto
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.qdrant_exception import QdrantConnectionException
from repositories.cache_repository import (
    delete_all_cache,
    delete_cache_for_document,
)
from repositories.kb_repository import (
    deleteAllDocuments,
    deleteDocument,
    getCourseIdsForDocument,
    getUploadedFiles,
)


def get_uploaded_documents(
    business_id: str,
    course_ids: list[str],
) -> list[UploadedDocumentDto]:
    try:
        logger.info(
            "Fetching uploaded documents started. Business ID=%s | Course IDs=%s",
            business_id,
            course_ids,
        )

        documents = getUploadedFiles(
            businessId=business_id,
            courseIds=course_ids,
        )

        logger.info(
            "Fetching uploaded documents completed. Business ID=%s | Documents=%d",
            business_id,
            len(documents),
        )

        return documents

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


def delete_uploaded_document(
    documentId: str,
    business_id: str,
):
    try:
        logger.info(
            "Document deletion workflow started. Business ID=%s | Document ID=%s",
            business_id,
            documentId,
        )

        logger.info(
            "Retrieving course IDs before document deletion. Document ID=%s",
            documentId,
        )

        course_ids = getCourseIdsForDocument(
            documentId=documentId,
            businessId=business_id,
        )

        logger.info(
            "Course ID lookup completed. Document ID=%s | Course IDs=%s",
            documentId,
            course_ids,
        )

        deleted = deleteDocument(
            documentId=documentId,
            businessId=business_id,
        )

        logger.info(
            "Document deletion completed. Document ID=%s | Deleted=%s",
            documentId,
            deleted,
        )

        if deleted and course_ids:
            try:
                logger.info(
                    "Cache invalidation started for deleted document. Document ID=%s",
                    documentId,
                )

                delete_cache_for_document(
                    business_id=business_id,
                    course_ids=course_ids,
                    document_id=documentId,
                )

                logger.info(
                    "Cache invalidation completed. Document ID=%s",
                    documentId,
                )

            except Exception as ex:
                logger.exception(
                    CACHE_DOCUMENT_INVALIDATION_FAILED_LOG,
                    documentId,
                    ex,
                )

        logger.info(
            "Document deletion workflow completed. Document ID=%s | Deleted=%s",
            documentId,
            deleted,
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


def clear_knowledge_base(
    business_id: str,
):
    try:
        logger.info(
            "Knowledge Base clearing workflow started. Business ID=%s",
            business_id,
        )

        deleted = deleteAllDocuments(
            businessId=business_id,
        )

        logger.info(
            "Knowledge Base document deletion completed. Business ID=%s | Deleted=%s",
            business_id,
            deleted,
        )

        if deleted:
            try:
                logger.info(
                    "Knowledge Base cache clearing started. Business ID=%s",
                    business_id,
                )

                delete_all_cache(
                    business_id=business_id,
                )

                logger.info(
                    "Knowledge Base cache clearing completed. Business ID=%s",
                    business_id,
                )

            except Exception as ex:
                logger.exception(
                    CACHE_CLEAR_FAILED_LOG,
                    business_id,
                    ex,
                )

        logger.info(
            "Knowledge Base clearing workflow completed. Business ID=%s | Deleted=%s",
            business_id,
            deleted,
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
