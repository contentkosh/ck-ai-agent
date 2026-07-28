import pytest
from unittest.mock import patch
from services.kb_query_service import (
    build_context,
    build_prompt,
    ask_question,
)
from io import BytesIO
from unittest.mock import MagicMock, patch
from services.kb_ingestion_service import ingest_documents
from dto.processed_document_dto import ProcessedDocumentDto
from dto.document_metadata_dto import DocumentMetadataDto

# =======================
# Build Context Tests
# ==========================================================

def test_build_context():

    chunk1 = MagicMock()
    chunk1.payload = {"text": "Artificial Intelligence"}
    chunk2 = MagicMock()
    chunk2.payload = {"text": "Machine Learning"}
    context = build_context([chunk1, chunk2])
    assert ("Artificial Intelligence"in context)
    assert ("Machine Learning"in context)

# ==========================================================
# Build Prompt Tests
# ==========================================================

def test_build_prompt():

    prompt = build_prompt(
        context="AI Context",
        query="What is AI?",
    )
    assert "AI Context" in prompt
    assert "What is AI?" in prompt

# ==========================================================
# Ask Question Tests
# ==========================================================

@patch("services.kb_query_service.searchChunks")
@patch("services.kb_query_service.get_embedding_model")
@patch("services.kb_query_service.get_llm")
def test_ask_question(
    mock_llm,
    mock_embedding,
    mock_search,
):

    embedding = MagicMock()
    embedding.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]
    mock_embedding.return_value = embedding
    chunk = MagicMock()
    chunk.payload = {
        "text": "Artificial Intelligence",
        "title": "AI Notes",
        "document_id": "123",
        "document_type": "Notes",
        "tag": "ai",
        "summary": "AI basics",
        "source": "ai.pdf",
        "page": 5,
    }

    mock_search.return_value = [chunk]
    response = MagicMock()
    response.content = "Artificial Intelligence is..."
    mock_llm.return_value.invoke.return_value = response
    result = ask_question("What is AI?")
    assert result.answer == "Artificial Intelligence is..."
    assert result.title == "AI Notes"
    assert result.tag == "ai"

# ==========================================================
# Ingestion — Temp File Cleanup Tests
# ==========================================================

@patch("services.kb_ingestion_service.delete_saved_file")
@patch("services.kb_ingestion_service.saveChunks")
@patch("services.kb_ingestion_service.process_document")
@patch("services.kb_ingestion_service.read_pdf")
def test_ingest_documents_cleans_up_saved_file_on_success(
    mock_read_pdf,
    mock_process_document,
    mock_save_chunks,
    mock_delete_saved_file,
):
    """
    Verify the saved PDF is deleted from disk after
    successful processing.
    """
    fake_pdf = MagicMock()
    mock_read_pdf.return_value = (fake_pdf, "/tmp/fake_saved.pdf")
    mock_process_document.return_value = ProcessedDocumentDto(
        document_id="123",
        metadata=DocumentMetadataDto(
            title="AI Notes",
            document_type="Notes",
            tag="ai",
            summary="s",
        ),
        points=[],
        chunks=2,
    )

    fake_file = MagicMock()
    fake_file.filename = "sample.pdf"
    fake_file.content_type = "application/pdf"
    fake_file.file = BytesIO(b"%PDF-1.4 dummy pdf")
    ingest_documents([fake_file])
    mock_delete_saved_file.assert_called_once_with("/tmp/fake_saved.pdf")