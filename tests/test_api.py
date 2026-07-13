from io import BytesIO
from unittest.mock import patch
from fastapi import status
from tests.conftest import client

# ==========================================================
# Health API Tests
# ==========================================================

def test_health_check(client):
    """
    Verify that the Health API is reachable.
    """
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "Running"
    assert "service" in data
    assert "version" in data

# ==========================================================
# Get Knowledge Base API Tests
# ==========================================================

@patch("api.routes.kb_routes.get_knowledge_base_records")
def test_get_knowledge_base(
    mock_get_knowledge_base_records,
    client,
):
    """
    Verify fetching all Knowledge Base records.
    """
    mock_get_knowledge_base_records.return_value = [
        {
            "title": "AI Notes",
            "tag": "ai",
        }
    ]

    response = client.get("/llm/kb")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_records"] == 1
    assert len(data["records"]) == 1
    assert data["records"][0]["title"] == "AI Notes"

# ==========================================================
# Ask Question API Tests
# ==========================================================

@patch("api.routes.kb_routes.ask_question")
def test_query_knowledge_base(
    mock_ask_question,
    client,
):
    """
    Verify that the Knowledge Base returns an answer.
    """
    mock_ask_question.return_value = {
        "answer": "Artificial Intelligence is the simulation of human intelligence.",
        "document_id": "123",
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "artificial_intelligence",
        "summary": "Introduction to AI.",
        "source": "ai_notes.pdf",
        "page": 12,
    }
    response = client.post(
        "/llm/kb/query",
        json={
            "query": "What is Artificial Intelligence?",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        data["answer"]
        == "Artificial Intelligence is the simulation of human intelligence."
    )
    assert data["title"] == "AI Notes"
    assert data["tag"] == "artificial_intelligence"
    assert data["source"] == "ai_notes.pdf"
    assert data["page"] == 12

# ==========================================================
# Upload Documents API Tests
# ==========================================================

@patch("api.routes.upload_routes.ingest_documents")
def test_upload_document(
    mock_ingest_documents,
    client,
):
    """
    Verify document upload.
    """
    mock_ingest_documents.return_value = (
        "Document uploaded successfully."
    )
    response = client.post(
        "/llm/upload",
        files=[
            (
                "files",
                (
                    "sample.pdf",
                    BytesIO(b"Dummy PDF content"),
                    "application/pdf",
                ),
            ),
        ],
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        data["message"]
        == "Document uploaded successfully."
    )

# ==========================================================
# Get Uploaded Documents API Tests
# ==========================================================

@patch("api.routes.file_routes.get_uploaded_documents_service")
def test_get_uploaded_documents(
    mock_get_uploaded_documents_service,
    client,
):
    """
    Verify uploaded documents retrieval.
    """
    mock_get_uploaded_documents_service.return_value = [
        {
            "document_id": "123",
            "title": "AI Notes",
            "source": "ai.pdf",
        }
    ]

    response = client.get("/llm/doc")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_documents"] == 1
    assert data["documents"][0]["title"] == "AI Notes"

# ==========================================================
# Delete Document API Tests
# ==========================================================

@patch("api.routes.file_routes.delete_document_service")
def test_delete_document(
    mock_delete_document_service,
    client,
):
    """
    Verify deleting one document.
    """
    response = client.delete(
        "/llm/files/delete/123",
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    mock_delete_document_service.assert_called_once_with(
        "123",
    )


# ==========================================================
# Clear Knowledge Base API Tests
# ==========================================================

@patch("api.routes.file_routes.clear_kb_service")
def test_clear_knowledge_base(
    mock_clear_kb_service,
    client,
):
    """
    Verify clearing the Knowledge Base.
    """
    response = client.delete(
        "/llm/files/delete",
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    mock_clear_kb_service.assert_called_once()