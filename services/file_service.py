from common.custom_exceptions import NotFoundException
from configuration.constants import DOCUMENT_NOT_FOUND_ERROR
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
    return getUploadedFiles()

# ==========================================================
# Delete Uploaded Document
# ==========================================================

def delete_uploaded_document(documentId: str):
    """
    Delete a single uploaded document.
    """
    deleted = deleteDocument(documentId)

    if not deleted:
        raise NotFoundException(
            DOCUMENT_NOT_FOUND_ERROR.format(documentId)
        )

# ==========================================================
# Clear Knowledge Base
# ==========================================================

def clear_knowledge_base():
    """
    Remove all uploaded documents.
    """
    deleteAllDocuments()