from common.custom_exceptions import NotFoundException
from repositories.kb_repository import (
    delete_all_documents,
    delete_document,
    get_uploaded_files,
)

# ==========================================================
# Get Uploaded Documents
# ==========================================================

def get_uploaded_documents():
    """
    Retrieve uploaded documents from the repository.
    """
    return get_uploaded_files()

# ==========================================================
# Delete Uploaded Document
# ==========================================================

def delete_uploaded_document(
    document_id: str,
):
    """
    Delete a single uploaded document.
    """
    deleted = delete_document(document_id)
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
    delete_all_documents()