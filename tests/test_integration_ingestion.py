from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from services.kb_ingestion_service import ingest_documents

def _build_minimal_pdf_bytes(text: str = "Hello Knowledge Base integration test") -> bytes:
    """
    Hand-craft a minimal but structurally valid single-page
    PDF with extractable text and a proper xref table, so
    PdfReader.extract_text() returns real content without any
    external dependency (no reportlab/fpdf needed).
    """
    content_stream = f"BT /F1 24 Tf 72 712 Td ({text}) Tj ET"
    content_length = len(content_stream)

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources "
        b"<< /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] "
        b"/Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {content_length} >>\nstream\n{content_stream}\nendstream\nendobj\n".encode(),
    ]

    header = b"%PDF-1.4\n"
    body = b""
    offsets = [0]
    current_offset = len(header)
    for obj in objects:
        offsets.append(current_offset)
        body += obj
        current_offset += len(obj)

    xref_offset = len(header) + len(body)
    num_objects = len(objects) + 1

    xref = f"xref\n0 {num_objects}\n".encode()
    xref += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        xref += f"{off:010d} 00000 n \n".encode()

    trailer = (
        f"trailer\n<< /Size {num_objects} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode()

    return header + body + xref + trailer

class FakeUploadFile:
    def __init__(self, filename: str, content: bytes):
        from io import BytesIO
        self.filename = filename
        self.file = BytesIO(content)

@patch("services.kb_ingestion_service.saveChunks")
@patch("services.document_metadata_service.get_llm")
@patch("services.kb_ingestion_service.get_embedding_model")
def test_ingest_documents_end_to_end(
    mock_get_embedding_model,
    mock_get_llm,
    mock_save_chunks,
    tmp_path,
    monkeypatch,
):
    """
    Exercise the real ingestion pipeline against an actual
    PDF on disk: save -> validate -> PdfReader parse ->
    real text extraction -> real chunk splitting -> cleanup.
    Only the embedding model, LLM, and Qdrant client are
    mocked, since those require live infrastructure.
    """
    monkeypatch.setattr("common.file_utils.UPLOAD_FOLDER", str(tmp_path))
    fake_embedding_model = MagicMock()
    fake_embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    mock_get_embedding_model.return_value = fake_embedding_model
    fake_llm = MagicMock()
    fake_response = MagicMock()
    fake_response.content = (
        '{"title": "Integration Test Doc", '
        '"document_type": "Notes", '
        '"tag": "integration_test", '
        '"summary": "A short integration test document."}'
    )
    fake_llm.invoke.return_value = fake_response
    mock_get_llm.return_value = fake_llm
    pdf_bytes = _build_minimal_pdf_bytes("Hello Knowledge Base integration test")
    upload_file = FakeUploadFile(filename="integration_sample.pdf", content=pdf_bytes)

    result = ingest_documents([upload_file])

    assert result.status == "success"
    assert result.documents_processed == 1
    assert result.chunks_inserted >= 1
    print(result)
    document = result.documents[0]
    assert document.title == "Integration Test Doc"
    assert document.tag == "integration_test"
    assert document.source == "integration_sample.pdf"

    mock_save_chunks.assert_called_once()
    saved_points = mock_save_chunks.call_args[0][0]
    assert len(saved_points) >= 1
    assert saved_points[0].payload["source"] == "integration_sample.pdf"
    assert saved_points[0].payload["tag"] == "integration_test"
    assert "Hello Knowledge Base" in saved_points[0].payload["text"]

    remaining_files = list(Path(tmp_path).glob("*"))
    assert remaining_files == []

@patch("services.kb_ingestion_service.saveChunks")
@patch("services.document_metadata_service.get_llm")
@patch("services.kb_ingestion_service.get_embedding_model")
def test_ingest_documents_end_to_end_cleans_up_on_metadata_failure(
    mock_get_embedding_model,
    mock_get_llm,
    mock_save_chunks,
    tmp_path,
    monkeypatch,
):
    """
    Verify that even when metadata extraction fails (e.g. the
    LLM returns invalid JSON), the real saved PDF file is
    still cleaned up from disk.
    """
    from exceptions.document_exception import DocumentProcessingException
    monkeypatch.setattr("common.file_utils.UPLOAD_FOLDER", str(tmp_path))
    fake_embedding_model = MagicMock()
    fake_embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    mock_get_embedding_model.return_value = fake_embedding_model

    fake_llm = MagicMock()
    fake_response = MagicMock()
    fake_response.content = "not valid json at all"
    fake_llm.invoke.return_value = fake_response
    mock_get_llm.return_value = fake_llm

    pdf_bytes = _build_minimal_pdf_bytes("Some real extractable text")
    upload_file = FakeUploadFile(filename="broken_metadata.pdf", content=pdf_bytes)

    with pytest.raises(DocumentProcessingException):
        ingest_documents([upload_file])

    mock_save_chunks.assert_not_called()
    remaining_files = list(Path(tmp_path).glob("*"))
    assert remaining_files == []