from unittest.mock import MagicMock
from unittest.mock import patch
from repositories.kb_repository import (
    build_document_payload,
    delete_all_documents,
    delete_document,
    get_all_records,
    get_uploaded_files,
    save_chunks,
    search_chunks,
)
# ==========================================================
# Build Payload Tests
# ==========================================================

def test_build_document_payload():
    payload = {
        "document_id": "123",
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "ai",
        "summary": "Introduction",
        "source": "ai.pdf",
    }

    result = build_document_payload(payload)
    assert result["document_id"] == "123"
    assert result["title"] == "AI Notes"
    assert result["tag"] == "ai"

# ==========================================================
# Save Chunks Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_save_chunks(
    mock_client,
):
    points = [MagicMock(), MagicMock()]
    save_chunks(points)
    mock_client.upsert.assert_called_once()

# ==========================================================
# Search Chunk Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_search_chunks(
    mock_client,
):
    point = MagicMock()
    result = MagicMock()
    result.points = [point]
    mock_client.query_points.return_value = result
    response = search_chunks(
        query_embedding=[0.1, 0.2]
    )
    assert len(response) == 1

# ==========================================================
# Get All Records Tests
# ==========================================================

@patch("repositories.kb_repository._scroll_records")
def test_get_all_records(
    mock_scroll,
):

    point = MagicMock()
    point.payload = {
        "document_id": "123",
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "ai",
        "summary": "Summary",
        "source": "ai.pdf",
        "page": 10,
        "text": "Artificial Intelligence",

    }

    mock_scroll.return_value = [point]
    records = get_all_records()
    assert len(records) == 1
    assert records[0]["title"] == "AI Notes"
    assert records[0]["page"] == 10

# ==========================================================
# Get Uploaded Files Tests
# ==========================================================

@patch("repositories.kb_repository._scroll_records")
def test_get_uploaded_files(
    mock_scroll,
):

    point = MagicMock()
    point.payload = {

        "document_id": "123",
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "ai",
        "summary": "Summary",
        "source": "ai.pdf",

    }

    mock_scroll.return_value = [point]
    documents = get_uploaded_files()
    assert len(documents) == 1
    assert documents[0]["title"] == "AI Notes"

# ==========================================================
# Delete Document Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_delete_document(
    mock_client,
):
    
    result = delete_document("123")
    assert result is True
    mock_client.delete.assert_called_once()

# ==========================================================
# Clear Knowledge Base Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_delete_all_documents(
    mock_client,
):

    result = delete_all_documents()
    assert result is True
    mock_client.delete.assert_called_once()