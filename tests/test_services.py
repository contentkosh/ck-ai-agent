import pytest
from io import BytesIO
from unittest.mock import MagicMock, patch
from dto.document_metadata_dto import DocumentMetadataDto
from dto.processed_document_dto import ProcessedDocumentDto
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.llm_exception import LLMResponseException
from services.kb_ingestion_service import ingest_documents
from services.kb_query_service import (
    ask_question,
    build_context,
    build_prompt,
)

# ==========================================================
# Build Context Tests
# ==========================================================

def test_build_context():
    chunk1 = MagicMock()
    chunk1.payload = {"text": "Artificial Intelligence",}
    chunk2 = MagicMock()
    chunk2.payload = {"text": "Machine Learning",}
    context = build_context([chunk1, chunk2])
    assert "Artificial Intelligence" in context
    assert "Machine Learning" in context

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
# Ask Question - No Results
# ==========================================================

@patch("services.kb_query_service.searchChunks")
@patch("services.kb_query_service.get_embedding_model")
def test_ask_question_no_results(
    mock_embedding,
    mock_search,
):
    """
    Verify a friendly response is returned when
    no relevant chunks are found.
    """
    embedding = MagicMock()
    embedding.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]
    mock_embedding.return_value = embedding
    mock_search.return_value = []
    result = ask_question("Unknown question")
    assert result.answer is not None
    assert result.document_id is None
    assert result.title is None
    assert result.source is None

# ==========================================================
# Ask Question - Repository Failure
# ==========================================================

@patch("services.kb_query_service.searchChunks")
@patch("services.kb_query_service.get_embedding_model")
def test_ask_question_repository_failure(
    mock_embedding,
    mock_search,
):
    """
    Verify repository failures are converted into
    KnowledgeBaseException.
    """
    embedding = MagicMock()
    embedding.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]
    mock_embedding.return_value = embedding
    mock_search.side_effect = ContentKoshException(
        "Database failure",
    )

    with pytest.raises(KnowledgeBaseException):
        ask_question("What is AI?")

# ==========================================================
# Ask Question - LLM Failure
# ==========================================================

@patch("services.kb_query_service.searchChunks")
@patch("services.kb_query_service.get_embedding_model")
@patch("services.kb_query_service.get_llm")
def test_ask_question_llm_failure(
    mock_llm,
    mock_embedding,
    mock_search,
):
    """
    Verify LLM failures raise LLMResponseException.
    """
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
    mock_llm.return_value.invoke.side_effect = Exception(
        "LLM unavailable",
    )

    with pytest.raises(LLMResponseException):
        ask_question("What is AI?")

# ==========================================================
# Ingestion — Temp File Cleanup Tests
# ==========================================================

@patch("services.kb_ingestion_service.delete_saved_file")
@patch("services.kb_ingestion_service.process_document")
@patch("services.kb_ingestion_service.read_pdf")
@patch("services.kb_ingestion_service.saveChunks")
def test_ingest_documents_cleans_up_saved_file_on_success(
    mock_save_chunks,
    mock_read_pdf,
    mock_process_document,
    mock_delete_saved_file,
):
    """
    Verify the saved PDF is deleted from disk after
    successful processing.
    """
    fake_pdf = MagicMock()
    mock_read_pdf.return_value = (
        fake_pdf,
        "/tmp/fake_saved.pdf",
    )

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

    mock_save_chunks.assert_called_once()

    mock_delete_saved_file.assert_called_once_with(
        "/tmp/fake_saved.pdf",
    )