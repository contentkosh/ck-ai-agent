from io import BytesIO
from unittest.mock import patch

from fastapi import status

from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.validation_exception import InvalidFileException
from common.custom_exceptions import NotFoundException


BUSINESS_ID = "test-business"
COURSE_ID = "test-course"


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
# Knowledge Base API Tests
# ==========================================================

@patch("api.routes.kb_routes.get_knowledge_base_records")
def test_get_knowledge_base(
    mock_get_knowledge_base_records,
    client,
):
    """
    Verify fetching Knowledge Base records.
    """
    mock_get_knowledge_base_records.return_value = [
        {
            "title": "AI Notes",
            "tag": "ai",
        }
    ]

    response = client.get(
        "/llm/kb",
        params={
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total_records"] == 1
    assert len(data["records"]) == 1
    assert data["records"][0]["title"] == "AI Notes"

    mock_get_knowledge_base_records.assert_called_once_with(
        business_id=BUSINESS_ID,
        course_ids=[COURSE_ID],
        tag=None,
    )


# ==========================================================
# Ask Question API Tests
# ==========================================================

@patch("api.routes.kb_routes.ask_question")
def test_query_knowledge_base(
    mock_ask_question,
    client,
):
    """
    Verify that the Knowledge Base returns an answer
    for the requested business and courses.
    """
    mock_ask_question.return_value = {
        "answer": (
            "Artificial Intelligence is the simulation "
            "of human intelligence."
        ),
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
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert (
        data["answer"]
        == "Artificial Intelligence is the simulation "
        "of human intelligence."
    )
    assert data["title"] == "AI Notes"
    assert data["tag"] == "artificial_intelligence"
    assert data["source"] == "ai_notes.pdf"
    assert data["page"] == 12

    mock_ask_question.assert_called_once_with(
        query="What is Artificial Intelligence?",
        business_id=BUSINESS_ID,
        course_ids=[COURSE_ID],
    )


@patch("api.routes.kb_routes.ask_question")
def test_query_knowledge_base_failure(
    mock_ask_question,
    client,
):
    """
    Verify the query API handles service failure.
    """
    mock_ask_question.side_effect = KnowledgeBaseException()

    response = client.post(
        "/llm/kb/query",
        json={
            "query": "What is AI?",
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ==========================================================
# Upload Documents API Tests
# ==========================================================

@patch("api.routes.upload_routes.ingest_documents")
def test_upload_document(
    mock_ingest_documents,
    client,
    auth_headers,
):
    """
    Verify document upload with business and course metadata.
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
                    BytesIO(b"%PDF-1.4 Dummy PDF content"),
                    "application/pdf",
                ),
            ),
        ],
        data={
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
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
    Verify protected upload endpoint rejects requests
    without an API key.
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
        data={
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
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
    Verify invalid files are rejected.
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
        data={
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ==========================================================
# Get Uploaded Documents API Tests
# ==========================================================

@patch("api.routes.file_routes.get_uploaded_documents_service")
def test_get_uploaded_documents(
    mock_get_uploaded_documents_service,
    client,
):
    """
    Verify uploaded documents retrieval for courses.
    """
    mock_get_uploaded_documents_service.return_value = [
        {
            "document_id": "123",
            "title": "AI Notes",
            "source": "ai.pdf",
        }
    ]

    response = client.get(
        "/llm/files",
        params={
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
    )

    print(response.json())

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["total_documents"] == 1
    assert data["documents"][0]["title"] == "AI Notes"

    mock_get_uploaded_documents_service.assert_called_once_with(
        business_id=BUSINESS_ID,
        course_ids=[COURSE_ID],
    )


@patch("api.routes.file_routes.get_uploaded_documents_service")
def test_get_uploaded_documents_service_failure(
    mock_service,
    client,
):
    """
    Verify the API handles document retrieval failure.
    """
    mock_service.side_effect = KnowledgeBaseException()

    response = client.get(
        "/llm/files",
        params={
            "business_id": BUSINESS_ID,
            "course_ids": [COURSE_ID],
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ==========================================================
# Delete Document API Tests
# ==========================================================

@patch("api.routes.file_routes.delete_document_service")
def test_delete_document(
    mock_delete_document_service,
    client,
    auth_headers,
):
    """
    Verify deleting a document within a business.
    """
    response = client.delete(
        "/llm/files/123",
        params={
            "business_id": BUSINESS_ID,
        },
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "success"

    mock_delete_document_service.assert_called_once_with(
        documentId="123",
        business_id=BUSINESS_ID,
    )


def test_delete_document_rejected_without_api_key(
    client,
):
    """
    Verify protected delete endpoint rejects requests
    without an API key.
    """
    response = client.delete(
        "/llm/files/123",
        params={
            "business_id": BUSINESS_ID,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@patch("api.routes.file_routes.delete_document_service")
def test_delete_document_not_found(
    mock_delete_document_service,
    client,
    auth_headers,
):
    """
    Verify deleting a non-existing document returns Not Found.
    """
    mock_delete_document_service.side_effect = NotFoundException(
        "Document not found.",
    )

    response = client.delete(
        "/llm/files/123",
        params={
            "business_id": BUSINESS_ID,
        },
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# ==========================================================
# Clear Knowledge Base API Tests
# ==========================================================

@patch("api.routes.file_routes.clear_kb_service")
def test_clear_knowledge_base(
    mock_clear_kb_service,
    client,
    auth_headers,
):
    """
    Verify clearing the Knowledge Base for a business.
    """
    response = client.delete(
        "/llm/files",
        params={
            "business_id": BUSINESS_ID,
        },
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["status"] == "success"

    mock_clear_kb_service.assert_called_once_with(
        business_id=BUSINESS_ID,
    )


def test_clear_knowledge_base_rejected_without_api_key(
    client,
):
    """
    Verify protected clear-KB endpoint rejects requests
    without an API key.
    """
    response = client.delete(
        "/llm/files",
        params={
            "business_id": BUSINESS_ID,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED