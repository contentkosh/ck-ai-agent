from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from exceptions.document_exception import (
    DocumentProcessingException,
)
from services.kb_ingestion_service import ingest_documents


BUSINESS_ID = "test-business"
COURSE_ID = "test-course"


# ==========================================================
# Helpers
# ==========================================================

def _build_minimal_pdf_bytes(
    text: str = "Hello Knowledge Base integration test",
) -> bytes:
    """
    Build a minimal valid single-page PDF with
    extractable text.
    """

    content_stream = (
        f"BT /F1 24 Tf 72 712 Td ({text}) Tj ET"
    )

    content_length = len(content_stream)

    objects = [
        (
            b"1 0 obj\n"
            b"<< /Type /Catalog /Pages 2 0 R >>\n"
            b"endobj\n"
        ),
        (
            b"2 0 obj\n"
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
            b"endobj\n"
        ),
        (
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R "
            b"/Resources << /Font << /F1 4 0 R >> >> "
            b"/MediaBox [0 0 612 792] "
            b"/Contents 5 0 R >>\n"
            b"endobj\n"
        ),
        (
            b"4 0 obj\n"
            b"<< /Type /Font /Subtype /Type1 "
            b"/BaseFont /Helvetica >>\n"
            b"endobj\n"
        ),
        (
            f"5 0 obj\n"
            f"<< /Length {content_length} >>\n"
            f"stream\n"
            f"{content_stream}\n"
            f"endstream\n"
            f"endobj\n"
        ).encode(),
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

    xref = (
        f"xref\n0 {num_objects}\n"
    ).encode()

    xref += b"0000000000 65535 f \n"

    for offset in offsets[1:]:
        xref += (
            f"{offset:010d} 00000 n \n"
        ).encode()

    trailer = (
        f"trailer\n"
        f"<< /Size {num_objects} /Root 1 0 R >>\n"
        f"startxref\n"
        f"{xref_offset}\n"
        f"%%EOF"
    ).encode()

    return header + body + xref + trailer


class FakeUploadFile:
    def __init__(
        self,
        filename: str,
        content: bytes,
    ):
        from io import BytesIO

        self.filename = filename
        self.file = BytesIO(content)


class FakeEmbedding:
    def __init__(self, values):
        self.values = values

    def tolist(self):
        return self.values


# ==========================================================
# End-to-End Ingestion
# ==========================================================

@patch(
    "services.kb_ingestion_service.saveChunks"
)
@patch(
    "services.document_metadata_service.get_llm"
)
@patch(
    "services.kb_ingestion_service.get_embedding_model"
)
def test_ingest_documents_end_to_end(
    mock_get_embedding_model,
    mock_get_llm,
    mock_save_chunks,
    tmp_path,
    monkeypatch,
):
    """
    Exercise the real ingestion pipeline:

    save -> validate -> PDF parsing -> text extraction
    -> metadata extraction -> chunking -> embeddings
    -> payload creation -> Qdrant save -> cleanup.

    External dependencies are mocked:
    - embedding model
    - LLM
    - Qdrant persistence
    """

    monkeypatch.setattr(
        "common.file_utils.UPLOAD_FOLDER",
        str(tmp_path),
    )

    # --------------------------------------------------
    # Embedding model
    # --------------------------------------------------

    fake_embedding_model = MagicMock()

    fake_embedding_model.encode.return_value = [
        FakeEmbedding(
            [0.1, 0.2, 0.3]
        )
    ]

    mock_get_embedding_model.return_value = (
        fake_embedding_model
    )

    # --------------------------------------------------
    # Metadata LLM
    # --------------------------------------------------

    fake_llm = MagicMock()

    fake_response = MagicMock()

    fake_response.content = (
        '{"title": "Integration Test Doc", '
        '"document_type": "Notes", '
        '"tag": "integration_test", '
        '"summary": '
        '"A short integration test document."}'
    )

    fake_llm.invoke.return_value = (
        fake_response
    )

    mock_get_llm.return_value = fake_llm

    # --------------------------------------------------
    # Upload
    # --------------------------------------------------

    pdf_bytes = _build_minimal_pdf_bytes(
        "Hello Knowledge Base integration test"
    )

    upload_file = FakeUploadFile(
        filename="integration_sample.pdf",
        content=pdf_bytes,
    )

    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    result = ingest_documents(
        files=[upload_file],
        business_id=BUSINESS_ID,
        course_id=COURSE_ID,
    )

    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    assert result.status == "success"
    assert result.documents_processed == 1
    assert result.chunks_inserted >= 1
    assert len(result.documents) == 1

    document = result.documents[0]

    assert document.title == "Integration Test Doc"
    assert document.document_type == "Notes"
    assert document.tag == "integration_test"
    assert document.source == "integration_sample.pdf"

    # --------------------------------------------------
    # Qdrant save
    # --------------------------------------------------

    mock_save_chunks.assert_called_once()

    saved_points = (
        mock_save_chunks.call_args.args[0]
    )

    saved_business_id = (
        mock_save_chunks.call_args.args[1]
    )

    assert saved_business_id == BUSINESS_ID
    assert len(saved_points) >= 1

    payload = saved_points[0].payload

    assert payload["source"] == (
        "integration_sample.pdf"
    )

    assert payload["tag"] == (
        "integration_test"
    )

    assert payload["business_id"] == (
        BUSINESS_ID
    )

    assert payload["course_id"] == (
        COURSE_ID
    )

    assert "Hello Knowledge Base" in (
        payload["text"]
    )

    assert payload["page"] == 1

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    remaining_files = list(
        Path(tmp_path).glob("*")
    )

    assert remaining_files == []


# ==========================================================
# Metadata Failure + Cleanup
# ==========================================================

@patch(
    "services.kb_ingestion_service.saveChunks"
)
@patch(
    "services.document_metadata_service.get_llm"
)
@patch(
    "services.kb_ingestion_service.get_embedding_model"
)
def test_ingest_documents_metadata_failure_cleans_up(
    mock_get_embedding_model,
    mock_get_llm,
    mock_save_chunks,
    tmp_path,
    monkeypatch,
):
    """
    Verify that a metadata extraction failure:

    - raises DocumentProcessingException
    - does not save chunks
    - removes the uploaded PDF
    """

    monkeypatch.setattr(
        "common.file_utils.UPLOAD_FOLDER",
        str(tmp_path),
    )

    # --------------------------------------------------
    # Embedding model
    # --------------------------------------------------

    fake_embedding_model = MagicMock()

    fake_embedding_model.encode.return_value = [
        FakeEmbedding(
            [0.1, 0.2, 0.3]
        )
    ]

    mock_get_embedding_model.return_value = (
        fake_embedding_model
    )

    # --------------------------------------------------
    # Invalid metadata response
    # --------------------------------------------------

    fake_llm = MagicMock()

    fake_response = MagicMock()

    fake_response.content = (
        "not valid json at all"
    )

    fake_llm.invoke.return_value = (
        fake_response
    )

    mock_get_llm.return_value = fake_llm

    # --------------------------------------------------
    # Upload
    # --------------------------------------------------

    pdf_bytes = _build_minimal_pdf_bytes(
        "Some real extractable text"
    )

    upload_file = FakeUploadFile(
        filename="broken_metadata.pdf",
        content=pdf_bytes,
    )

    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    with pytest.raises(
        DocumentProcessingException
    ):
        ingest_documents(
            files=[upload_file],
            business_id=BUSINESS_ID,
            course_id=COURSE_ID,
        )

    # --------------------------------------------------
    # Nothing should reach Qdrant
    # --------------------------------------------------

    mock_save_chunks.assert_not_called()

    # --------------------------------------------------
    # Uploaded PDF must be removed
    # --------------------------------------------------

    remaining_files = list(
        Path(tmp_path).glob("*")
    )

    assert remaining_files == []