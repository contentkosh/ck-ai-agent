from common.custom_exceptions import (
    NotFoundException,
)
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

def delete_uploaded_document(
    document_id: str,
):
    """
    Delete a single uploaded document.
    """
    deleted = deleteDocument(document_id)

    if not deleted:
        raise NotFoundException(
            f"Document '{document_id}' does not exist."
        )

# ==========================================================
# Clear Knowledge Base
# ==========================================================

def clear_knowledge_base():
    """
    Remove all uploaded documents.
    """
    deleteAllDocuments()