from io import BytesIO
from unittest.mock import patch
from fastapi import status
from tests.conftest import client
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.validation_exception import InvalidFileException
from common.custom_exceptions import NotFoundException

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
    mockGetKnowledgeBaseRecords,
    client,
):
    """
    Verify fetching all Knowledge Base records.
    """
    mockGetKnowledgeBaseRecords.return_value = [
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
    mockAskQuestion,
    client,
):
    """
    Verify that the Knowledge Base returns an answer.
    """
    mockAskQuestion.return_value = {
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

@patch("api.routes.kb_routes.ask_question")
def test_query_knowledge_base_failure(
    mock_ask_question,
    client,
):
    """
    Verify query API returns Internal Server Error
    when the service fails.
    """
    mock_ask_question.side_effect = KnowledgeBaseException()
    response = client.post(
        "/llm/kb/query",
        json={
            "query": "What is AI?",
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

# ==========================================================
# Upload Documents API Tests
# ==========================================================

@patch("api.routes.upload_routes.ingest_documents")
def test_upload_document(
    mockIngestDocuments,
    client,
    auth_headers,
):
    """
    Verify document upload.
    """
    mockIngestDocuments.return_value = (
        "Document uploaded successfully."
    )
    response = client.post(
        "/llm/upload",
        files=[
            (
                "files",
                (
                    "sample.pdf",
                    BytesIO(b"%PDF-1.4 Dummy PDF content"),
                    "application/pdf",
                ),
            ),
        ],
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        data["message"]
        == "Document uploaded successfully."
    )


def test_upload_document_rejected_without_api_key(
    client,
):
    """
    Verify upload is rejected when no API key is supplied.
    """
    response = client.post(
        "/llm/upload",
        files=[
            (
                "files",
                (
                    "sample.pdf",
                    BytesIO(b"%PDF-1.4 Dummy PDF content"),
                    "application/pdf",
                ),
            ),
        ],
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# ==========================================================
# Upload Documents - Negative Tests
# ==========================================================

@patch("api.routes.upload_routes.ingest_documents")
def test_upload_document_invalid_file(
    mock_ingest_documents,
    client,
    auth_headers,
):
    """
    Verify upload returns Bad Request when an invalid
    file is uploaded.
    """
    mock_ingest_documents.side_effect = InvalidFileException(
        "Invalid file type.",
    )

    response = client.post(
        "/llm/upload",
        files=[
            (
                "files",
                (
                    "sample.txt",
                    BytesIO(b"dummy"),
                    "text/plain",
                ),
            ),
        ],
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

# ==========================================================
# Get Uploaded Documents API Tests
# ==========================================================

@patch("api.routes.file_routes.get_uploaded_documents_service")
def test_get_uploaded_documents(
    mockGetUploadedDocumentsService,
    client,
):
    """
    Verify uploaded documents retrieval.
    """
    mockGetUploadedDocumentsService.return_value = [
        {
            "document_id": "123",
            "title": "AI Notes",
            "source": "ai.pdf",
        }
    ]

    response = client.get("/llm/files")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_documents"] == 1
    assert data["documents"][0]["title"] == "AI Notes"

@patch("api.routes.file_routes.get_uploaded_documents_service")
def test_get_uploaded_documents_service_failure(
    mock_service,
    client,
):
    """
    Verify API returns Internal Server Error when
    the service fails.
    """
    mock_service.side_effect = KnowledgeBaseException()
    response = client.get("/llm/files")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

# ==========================================================
# Delete Document API Tests
# ==========================================================

@patch("api.routes.file_routes.delete_document_service")
def test_delete_document(
    mockDeleteDocumentService,
    client,
    auth_headers,
):
    """
    Verify deleting one document.
    """
    response = client.delete(
        "/llm/files/123",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    mockDeleteDocumentService.assert_called_once_with(
        "123",
    )

def test_delete_document_rejected_without_api_key(
    client,
):
    """
    Verify delete is rejected when no API key is supplied.
    """
    response = client.delete(
        "/llm/files/123",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@patch("api.routes.file_routes.delete_document_service")
def test_delete_document_not_found(
    mock_delete_document_service,
    client,
    auth_headers,
):
    """
    Verify deleting a non-existing document
    returns Not Found.
    """
    mock_delete_document_service.side_effect = NotFoundException(
        "Document not found.",
    )

    response = client.delete(
        "/llm/files/123",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

# ==========================================================
# Clear Knowledge Base API Tests
# ==========================================================

@patch("api.routes.file_routes.clear_kb_service")
def test_clear_knowledge_base(
    mockClearKbService,
    client,
    auth_headers,
):
    """
    Verify clearing the Knowledge Base.
    """
    response = client.delete(
        "/llm/files",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    mockClearKbService.assert_called_once()

def test_clear_knowledge_base_rejected_without_api_key(
    client,
):
    """
    Verify clear KB is rejected when no API key is supplied.
    """
    response = client.delete(
        "/llm/files",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED