from unittest.mock import MagicMock
from unittest.mock import patch
from repositories.kb_repository import (
    buildDocumentPayload,
    deleteAllDocuments,
    deleteDocument,
    getAllRecords,
    getUploadedFiles,
    saveChunks,
    searchChunks,
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

    result = buildDocumentPayload(payload)
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
    saveChunks(points)
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
    response = searchChunks(queryEmbedding=[0.1, 0.2],)
    assert len(response) == 1

# ==========================================================
# Get All Records Tests
# ==========================================================

@patch("repositories.kb_repository._scrollRecords")
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
    records = getAllRecords()
    assert len(records) == 1
    assert records[0].title == "AI Notes"
    assert records[0].page == 10

# ==========================================================
# Get Uploaded Files Tests
# ==========================================================

@patch("repositories.kb_repository._scrollRecords")
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
    documents = getUploadedFiles()
    assert len(documents) == 1
    assert documents[0]["title"] == "AI Notes"

# ==========================================================
# Delete Document Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_delete_document(
    mock_client,
):
    point = MagicMock()
    mock_client.scroll.return_value = ([point], None)
    result = deleteDocument("123")
    assert result is True
    mock_client.delete.assert_called_once()

@patch("repositories.kb_repository.client")
def test_delete_document_not_found(
    mock_client,
):
    """
    Verify deleteDocument returns False when no chunks
    match the given document_id.
    """
    mock_client.scroll.return_value = ([], None)
    result = deleteDocument("does-not-exist")
    assert result is False
    mock_client.delete.assert_not_called()


@patch("repositories.kb_repository.client")
def test_delete_document_found(
    mock_client,
):
    """
    Verify deleteDocument returns True and calls delete
    when a matching chunk exists.
    """
    point = MagicMock()
    mock_client.scroll.return_value = ([point], None)
    result = deleteDocument("123")
    assert result is True
    mock_client.delete.assert_called_once()

# ==========================================================
# Get All Records - Tag Filter Tests
# ==========================================================

@patch("repositories.kb_repository._scrollRecords")
def test_get_all_records_with_tag_filter(
    mock_scroll,
):
    """
    Verify getAllRecords passes a server-side tag filter
    through to _scrollRecords rather than filtering in
    Python.
    """
    point = MagicMock()
    point.payload = {
        "document_id": "123",
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "ai",
        "summary": "Summary",
        "source": "ai.pdf",
        "page": 1,
        "text": "text",
    }

    mock_scroll.return_value = [point]
    records = getAllRecords(tag="ai")
    assert len(records) == 1
    passed_filter = mock_scroll.call_args[0][0]
    assert passed_filter is not None

# =========================================================
# Scroll Records - Pagination Test
# ==========================================================

@patch("repositories.kb_repository.client")
def test_scroll_records_paginates(
    mock_client,
):
    """
    Verify _scrollRecords follows next_offset until
    exhausted instead of stopping after one page.
    """
    from repositories.kb_repository import _scrollRecords

    page_1_point = MagicMock()
    page_2_point = MagicMock()
    mock_client.scroll.side_effect = [
        ([page_1_point], "offset-2"),
        ([page_2_point], None),
    ]

    records = _scrollRecords()
    assert len(records) == 2
    assert mock_client.scroll.call_count == 2

# ==========================================================
# Clear Knowledge Base Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_delete_all_documents(
    mock_client,
):
    result = deleteAllDocuments()
    assert result is True
    mock_client.delete.assert_called_once()