# ==========================================================
# Knowledge Base Ingestion Service
# Handles the end-to-end document ingestion pipeline by
# processing PDFs, generating embeddings, extracting metadata,
# and storing document vectors in the knowledge base.
# ==========================================================

import uuid
from typing import Any
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client.models import PointStruct
from common.custom_exceptions import (
    EmbeddingException,
    PDFProcessingException,
)
from common.embedding_client import get_embedding_model
from common.file_utils import save_uploaded_file, delete_saved_file
from common.logger import logger
from validators.file_validator import validate_saved_file
from configuration.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
)
from exceptions.document_exception import (
    DocumentProcessingException,
    EmptyDocumentException,
)
from repositories.kb_repository import save_chunks
from services.document_metadata_service import extract_document_metadata

Page = dict[str, Any]
Metadata = dict[str, Any]
_text_splitter: RecursiveCharacterTextSplitter | None = None

def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Return the singleton text splitter."""
    global _text_splitter
    if _text_splitter is None:
        _text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    return _text_splitter

def generate_uuid() -> str:
    """Generate a UUID."""
    return str(uuid.uuid4())

# ==========================================================
# Generate Embedding
# ==========================================================

def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector."""
    try:
        return get_embedding_model().encode(text).tolist()
    except Exception as ex:
        logger.exception("Embedding generation failed: %s", ex)
        raise EmbeddingException(
            "Failed to generate embedding."
        ) from ex

# ==========================================================
# Build Payload
# ==========================================================

def build_payload(
    *,
    chunk: str,
    metadata: Metadata,
    filename: str,
    document_id: str,
    page_number: int,
) -> Metadata:
    """Build the Qdrant payload."""
    return {
        "document_id": document_id,
        "text": chunk,
        "title": metadata.get("title"),
        "document_type": metadata.get("document_type"),
        "tag": metadata.get("tag"),
        "summary": metadata.get("summary"),
        "source": filename,
        "page": page_number,
    }

# ==========================================================
# Read PDF
# ==========================================================

def read_pdf(file: UploadFile) -> tuple[PdfReader, str]:
    """Validate, save and load a PDF."""
    filename = file.filename
    saved_file = None

    try:
        logger.info("Saving file: %s", filename)
        saved_file = save_uploaded_file(file)
        validate_saved_file(saved_file)
        return PdfReader(saved_file), saved_file
    except Exception as ex:
        logger.exception(
            "Failed to read PDF '%s': %s",
            filename,
            ex,
        )

        # The file was already written to disk above; if parsing
        # or validation fails here, ingest_documents' cleanup
        # never runs (it only wraps process_document, which we
        # never reach), so clean up here instead.
        if saved_file is not None:
            delete_saved_file(saved_file)

        raise PDFProcessingException(
            f"Unable to process '{filename}'."
        ) from ex

def extract_document_text(
    pdf: PdfReader,
) -> tuple[str, list[Page]]:
    """Extract text from all PDF pages."""
    pages: list[Page] = []
    document_text: list[str] = []
    for page_number, page in enumerate(pdf.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as ex:
            logger.warning("Unable to read page %d: %s",page_number,ex,)
            page_text = ""
        pages.append({
            "page": page_number,
            "text": page_text,
        })
        document_text.append(page_text)
    full_text = "\n".join(document_text)
    logger.info("Extracted %d pages.",len(pages),)
    return full_text, pages

# ==========================================================
# Extract Metadata
# ==========================================================
def get_document_metadata(pages: list[Page]) -> Metadata:
    """Extract document metadata."""
    try:
        metadata_source = "\n".join(
            page["text"] for page in pages[:3]
        )
        logger.info("Extracting document metadata.")
        metadata = extract_document_metadata(metadata_source)
        logger.info("Metadata extracted successfully.")
        return metadata
    except Exception as ex:
        logger.exception("Metadata extraction failed: %s",ex,)
        raise DocumentProcessingException(
            "Unable to extract document metadata."
        ) from ex
    
def generate_document_id() -> str:
    """Generate a unique document ID."""
    return generate_uuid()

def build_vectors(
    *,
    pages: list[Page],
    metadata: Metadata,
    filename: str,
    document_id: str,
) -> tuple[list[PointStruct], int]:
    """Generate vectors for all document chunks."""
    splitter = get_text_splitter()
    points: list[PointStruct] = []
    total_chunks = 0
    for page in pages:
        page_text = page["text"]
        if not page_text.strip():
            continue
        page_number = page["page"]
        chunks = splitter.split_text(page_text)
        logger.info("Page %d generated %d chunks.",page_number,len(chunks),)
        for chunk in chunks:
            points.append(
                PointStruct(
                    id=generate_uuid(),
                    vector=generate_embedding(chunk),
                    payload=build_payload(
                        chunk=chunk,
                        metadata=metadata,
                        filename=filename,
                        document_id=document_id,
                        page_number=page_number,
                    ),
                )
            )
            total_chunks += 1
    logger.info("Generated %d vectors.",total_chunks,)
    return points, total_chunks

def process_document(
    pdf: PdfReader,
    filename: str,
) -> dict[str, Any]:
    """Process a PDF document."""
    try:
        logger.info(
            "Processing document: %s",
            filename,
        )

        document_id = generate_uuid()

        full_text, pages = extract_document_text(pdf)

        if not full_text.strip():
            raise EmptyDocumentException(
                "The uploaded PDF contains no readable text."
            )

        metadata = get_document_metadata(pages)

        points, total_chunks = build_vectors(
            pages=pages,
            metadata=metadata,
            filename=filename,
            document_id=document_id,
        )

        logger.info(
            "Processed %s (%d chunks).",
            document_id,
            total_chunks,
        )

        return {
            "document_id": document_id,
            "metadata": metadata,
            "points": points,
            "chunks": total_chunks,
        }

    except (
        EmptyDocumentException,
        DocumentProcessingException,
        PDFProcessingException,
    ):
        raise

    except Exception as ex:
        logger.exception(
            "Document processing failed: %s",
            ex,
        )

        raise DocumentProcessingException(
            f"Failed to process '{filename}'."
        ) from ex

def ingest_documents(
    files: list[UploadFile],
) -> dict[str, Any]:
    """Ingest PDF documents into the Knowledge Base."""
    try:
        logger.info("Knowledge Base ingestion started.")

        documents: list[Metadata] = []
        total_chunks = 0

        for file in files:
            logger.info(
                "Processing file: %s",
                file.filename,
            )

            pdf, saved_file_path = read_pdf(file)

            try:
                document = process_document(
                    pdf=pdf,
                    filename=file.filename,
                )

            finally:
                # On Windows, pypdf may still hold the file open
                # internally, which blocks deletion. Explicitly
                # release it before cleanup.
                try:
                    stream = getattr(pdf, "stream", None)
                    if stream is not None and not stream.closed:
                        stream.close()
                except Exception:
                    pass

                del pdf
                delete_saved_file(saved_file_path)

            save_chunks(document["points"])

            total_chunks += document["chunks"]

            documents.append(
                {
                    "document_id": document["document_id"],
                    "title": document["metadata"].get("title"),
                    "document_type": document["metadata"].get("document_type"),
                    "tag": document["metadata"].get("tag"),
                    "summary": document["metadata"].get("summary"),
                    "source": file.filename,
                    "chunks": document["chunks"],
                }
            )

            logger.info(
                "Successfully processed '%s'.",
                file.filename,
            )

        logger.info(
            "Knowledge Base ingestion completed. Documents=%d Chunks=%d",
            len(documents),
            total_chunks,
        )

        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_inserted": total_chunks,
            "documents": documents,
        }

    except (
        EmptyDocumentException,
        DocumentProcessingException,
        PDFProcessingException,
    ):
        raise

    except Exception as ex:
        logger.exception(
            "Knowledge Base ingestion failed: %s",
            ex,
        )

        raise PDFProcessingException(
            "Knowledge Base ingestion failed."
        ) from ex