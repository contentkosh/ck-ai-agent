# ==========================================================
# File Service
# Handles uploaded document operations by interacting with
# the Knowledge Base repository.
# ==========================================================

from common.custom_exceptions import NotFoundException
from common.logger import logger
from configuration.constants import (
    DELETE_DOCUMENT_FAILED_LOG,
    CLEAR_KNOWLEDGE_BASE_FAILED_LOG,
    FETCH_UPLOADED_DOCUMENTS_FAILED_LOG,
)
from configuration.error_constants import (DOCUMENT_NOT_FOUND_ERROR,)
from exceptions.knowledge_base_exception import (KnowledgeBaseException,)
from exceptions.contentkosh_exception import (ContentKoshException,)
from repositories.kb_repository import (
    deleteAllDocuments,
    deleteDocument,
    getUploadedFiles,
)

# ==========================================================
# Get Uploaded Documents
# ==========================================================

def get_uploaded_documents():
    """
    Retrieve uploaded documents from the repository.
    """
    try:
        return getUploadedFiles()

    except ContentKoshException as ex:
        logger.exception(FETCH_UPLOADED_DOCUMENTS_FAILED_LOG,ex,)
        raise KnowledgeBaseException() from ex
    
# ==========================================================
# Delete Uploaded Document
# ==========================================================

def delete_uploaded_document(
    documentId: str,
):
    """
    Delete a single uploaded document.
    """
    try:
        deleted = deleteDocument(documentId)

    except ContentKoshException as ex:
        logger.exception(DELETE_DOCUMENT_FAILED_LOG,ex,)
        raise KnowledgeBaseException() from ex
    
    if not deleted:
        raise NotFoundException(DOCUMENT_NOT_FOUND_ERROR.format(documentId))

# ==========================================================
# Clear Knowledge Base
# ==========================================================

def clear_knowledge_base():
    """
    Remove all uploaded documents.
    """
    try:
        deleteAllDocuments()

    except ContentKoshException as ex:
        logger.exception(CLEAR_KNOWLEDGE_BASE_FAILED_LOG,ex,)
        raise KnowledgeBaseException() from ex