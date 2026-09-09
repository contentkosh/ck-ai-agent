import uuid
from typing import Any, TypedDict

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client.models import PointStruct

from common.custom_exceptions import (
    EmbeddingException,
    PDFProcessingException,
)
from common.embedding_client import get_embedding_model
from common.file_utils import (
    save_uploaded_file,
    delete_saved_file,
)
from common.logger import logger

from validators.file_validator import validate_saved_file

from configuration.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_BATCH_SIZE,
)

from configuration.constants import (
    FILE_SAVE_LOG,
    METADATA_BUSINESS_ID,
    METADATA_COURSE_ID,
    PDF_READ_FAILED_LOG,
    PAGE_READ_FAILED_LOG,
    PAGES_EXTRACTED_LOG,
    DOCUMENT_PROCESSING_STARTED_LOG,
    DOCUMENT_PROCESSED_LOG,
    DOCUMENT_PROCESSING_FAILED_LOG,
    KB_INGESTION_STARTED_LOG,
    KB_INGESTION_COMPLETED_LOG,
    KB_INGESTION_FAILED_LOG,
    FILE_PROCESSING_STARTED_LOG,
    FILE_PROCESSING_COMPLETED_LOG,
    PAGE_CHUNK_GENERATION_LOG,
    GENERATED_VECTORS_LOG,
    METADATA_EXTRACTION_STARTED_LOG,
    METADATA_EXTRACTION_COMPLETED_LOG,
    METADATA_EXTRACTION_FAILED_LOG,
    METADATA_DOCUMENT_ID,
    METADATA_TEXT,
    METADATA_TITLE,
    METADATA_DOCUMENT_TYPE,
    METADATA_TAG,
    METADATA_SUMMARY,
    METADATA_SOURCE,
    METADATA_PAGE,
    SUCCESS_STATUS,
)

from configuration.error_constants import (
    EMBEDDING_GENERATION_FAILED_MESSAGE,
    PDF_READ_FAILED_MESSAGE,
    DOCUMENT_METADATA_EXTRACTION_FAILED_MESSAGE,
)

from repositories.kb_repository import (
    deleteDocument,
    saveChunks,
)
from services.document_metadata_service import extract_document_metadata

from dto.file_response_dto import (
    UploadedDocumentsResponse,
    UploadedDocumentDto,
)

from dto.processed_document_dto import ProcessedDocumentDto
from dto.document_metadata_dto import DocumentMetadataDto

from validators.upload_validator import validate_upload

from exceptions.contentkosh_exception import ContentKoshException
from exceptions.document_exception import (
    DocumentProcessingException,
    EmptyDocumentException,
    NoReadableTextException,
)
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.qdrant_exception import QdrantConnectionException


class Page(TypedDict):
    page: int
    text: str


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
# Build Payload
# ==========================================================

def build_payload(
    *,
    chunk: str,
    metadata: DocumentMetadataDto,
    filename: str,
    document_id: str,
    page_number: int,
    business_id: str,
    course_ids: list[str],
) -> dict:
    """Build the Qdrant payload."""
    return {
        METADATA_DOCUMENT_ID: document_id,
        METADATA_TEXT: chunk,
        METADATA_TITLE: metadata.title,
        METADATA_DOCUMENT_TYPE: metadata.document_type,
        METADATA_TAG: metadata.tag,
        METADATA_SUMMARY: metadata.summary,
        METADATA_SOURCE: filename,
        METADATA_PAGE: page_number,
        METADATA_BUSINESS_ID: business_id,
        METADATA_COURSE_ID: course_ids,
    }


# ==========================================================
# Read PDF
# ==========================================================

def read_pdf(
    file: UploadFile,
) -> tuple[PdfReader, str]:
    """Validate, save and load a PDF."""
    filename = file.filename
    saved_file = None

    try:
        logger.info(FILE_SAVE_LOG, filename)

        saved_file = save_uploaded_file(file)
        validate_saved_file(saved_file)

        return PdfReader(saved_file), saved_file

    except Exception as ex:
        logger.exception(
            PDF_READ_FAILED_LOG,
            filename,
            ex,
        )

        if saved_file is not None:
            delete_saved_file(saved_file)

        raise PDFProcessingException(
            PDF_READ_FAILED_MESSAGE.format(filename),
        ) from ex


# ==========================================================
# Extract Document Text
# ==========================================================

def extract_document_text(
    pdf: PdfReader,
) -> tuple[str, list[Page]]:
    """Extract text from all PDF pages."""
    pages: list[Page] = []
    document_text: list[str] = []

    for page_number, page in enumerate(
        pdf.pages,
        start=1,
    ):
        try:
            page_text = page.extract_text() or ""

        except Exception as ex:
            logger.warning(
                PAGE_READ_FAILED_LOG,
                page_number,
                ex,
            )
            page_text = ""

        pages.append({
            "page": page_number,
            "text": page_text,
        })

        document_text.append(page_text)

    full_text = "\n".join(document_text)

    logger.info(
        PAGES_EXTRACTED_LOG,
        len(pages),
    )

    return full_text, pages


# ==========================================================
# Extract Metadata
# ==========================================================

def get_document_metadata(
    pages: list[Page],
) -> DocumentMetadataDto:
    """Extract document metadata."""
    try:
        metadata_source = "\n".join(
            page["text"]
            for page in pages[:3]
        )

        logger.info(
            METADATA_EXTRACTION_STARTED_LOG,
        )

        metadata = extract_document_metadata(
            metadata_source,
        )

        logger.info(
            METADATA_EXTRACTION_COMPLETED_LOG,
        )

        return metadata

    except Exception as ex:
        logger.exception(
            METADATA_EXTRACTION_FAILED_LOG,
            ex,
        )

        raise DocumentProcessingException(
            DOCUMENT_METADATA_EXTRACTION_FAILED_MESSAGE,
        ) from ex


# ==========================================================
# Process Embedding Batch
# ==========================================================

def process_embedding_batch(
    *,
    chunk_batch: list[tuple[str, int]],
    metadata: DocumentMetadataDto,
    filename: str,
    document_id: str,
    business_id: str,
    course_ids: list[str],
) -> int:
    """Generate embeddings and store one batch in Qdrant."""

    chunk_texts = [
        chunk
        for chunk, _ in chunk_batch
    ]

    try:
        embeddings = get_embedding_model().encode(
            chunk_texts,
            batch_size=EMBEDDING_BATCH_SIZE,
        )

    except Exception as ex:
        logger.exception(
            "Embedding generation failed: %s",
            ex,
        )

        raise EmbeddingException(
            EMBEDDING_GENERATION_FAILED_MESSAGE,
        ) from ex

    points: list[PointStruct] = []

    for (chunk, page_number), embedding in zip(
        chunk_batch,
        embeddings,
    ):
        points.append(
            PointStruct(
                id=generate_uuid(),
                vector=embedding.tolist(),
                payload=build_payload(
                    chunk=chunk,
                    metadata=metadata,
                    filename=filename,
                    document_id=document_id,
                    page_number=page_number,
                    business_id=business_id,
                    course_ids=course_ids,
                ),
            )
        )

    try:
        saveChunks(
            points,
            business_id,
        )

    except ContentKoshException as ex:
        logger.exception(
            KB_INGESTION_FAILED_LOG,
            ex,
        )

        if isinstance(
            ex.cause,
            QdrantConnectionException,
        ):
            raise ex.cause

        raise KnowledgeBaseException() from ex

    return len(points)


# ==========================================================
# Build Vectors
# ==========================================================

def build_vectors(
    *,
    pages: list[Page],
    metadata: DocumentMetadataDto,
    filename: str,
    document_id: str,
    business_id: str,
    course_ids: list[str],
) -> int:
    """Generate and store document vectors in batches."""

    splitter = get_text_splitter()
    chunk_batch: list[tuple[str, int]] = []
    total_chunks = 0

    try:
        for page in pages:
            page_text = page["text"]

            if not page_text.strip():
                continue

            page_number = page["page"]

            chunks = splitter.split_text(
                page_text,
            )

            logger.info(
                PAGE_CHUNK_GENERATION_LOG,
                page_number,
                len(chunks),
            )

            for chunk in chunks:
                chunk_batch.append(
                    (
                        chunk,
                        page_number,
                    )
                )

                if len(chunk_batch) >= EMBEDDING_BATCH_SIZE:
                    total_chunks += process_embedding_batch(
                        chunk_batch=chunk_batch,
                        metadata=metadata,
                        filename=filename,
                        document_id=document_id,
                        business_id=business_id,
                        course_ids=course_ids,
                    )

                    chunk_batch.clear()

        if chunk_batch:
            total_chunks += process_embedding_batch(
                chunk_batch=chunk_batch,
                metadata=metadata,
                filename=filename,
                document_id=document_id,
                business_id=business_id,
                course_ids=course_ids,
            )

    except Exception as ex:
        logger.exception(
            DOCUMENT_PROCESSING_FAILED_LOG,
            ex,
        )

        try:
            deleteDocument(
                documentId=document_id,
                businessId=business_id,
            )

        except Exception as rollback_ex:
            logger.exception(
                "Failed to rollback document %s: %s",
                document_id,
                rollback_ex,
            )

        raise

    logger.info(
        GENERATED_VECTORS_LOG,
        total_chunks,
    )

    return total_chunks


# ==========================================================
# Process Document
# ==========================================================

def process_document(
    pdf: PdfReader,
    filename: str,
    business_id: str,
    course_ids: list[str],
) -> ProcessedDocumentDto:
    """Process a PDF document."""

    try:
        logger.info(
            DOCUMENT_PROCESSING_STARTED_LOG,
            filename,
        )

        document_id = generate_uuid()

        full_text, pages = extract_document_text(
            pdf,
        )

        if not full_text.strip():
            raise NoReadableTextException()

        metadata = get_document_metadata(
            pages,
        )

        total_chunks = build_vectors(
            pages=pages,
            metadata=metadata,
            filename=filename,
            document_id=document_id,
            business_id=business_id,
            course_ids=course_ids,
        )

        logger.info(
            DOCUMENT_PROCESSED_LOG,
            filename,
            total_chunks,
        )

        return ProcessedDocumentDto(
            document_id=document_id,
            metadata=metadata,
            chunks=total_chunks,
        )

    except (
        EmptyDocumentException,
        NoReadableTextException,
        DocumentProcessingException,
        PDFProcessingException,
        KnowledgeBaseException,
        QdrantConnectionException,
    ):
        raise

    except Exception as ex:
        logger.exception(
            DOCUMENT_PROCESSING_FAILED_LOG,
            ex,
        )
        raise


# ==========================================================
# Ingest Documents
# ==========================================================

def ingest_documents(
    *,
    files: list[UploadFile],
    business_id: str,
    course_ids: list[str],
) -> dict[str, Any]:
    """Ingest PDF documents into the Knowledge Base."""

    validate_upload(files)

    try:
        logger.info(
            KB_INGESTION_STARTED_LOG,
        )

        documents: list[UploadedDocumentDto] = []
        total_chunks = 0

        for file in files:
            logger.info(
                FILE_PROCESSING_STARTED_LOG,
                file.filename,
            )

            pdf, saved_file_path = read_pdf(file)

            try:
                document = process_document(
                    pdf=pdf,
                    filename=file.filename,
                    business_id=business_id,
                    course_ids=course_ids,
                )

            finally:
                try:
                    stream = getattr(
                        pdf,
                        "stream",
                        None,
                    )

                    if (
                        stream is not None
                        and not stream.closed
                    ):
                        stream.close()

                except Exception:
                    pass

                del pdf

                delete_saved_file(
                    saved_file_path,
                )

            total_chunks += document.chunks

            documents.append(
                UploadedDocumentDto(
                    document_id=document.document_id,
                    title=document.metadata.title,
                    document_type=document.metadata.document_type,
                    tag=document.metadata.tag,
                    summary=document.metadata.summary,
                    source=file.filename,
                )
            )

            logger.info(
                FILE_PROCESSING_COMPLETED_LOG,
                file.filename,
            )

        logger.info(
            KB_INGESTION_COMPLETED_LOG,
            len(documents),
            total_chunks,
        )

        return UploadedDocumentsResponse(
            status=SUCCESS_STATUS,
            documents_processed=len(documents),
            chunks_inserted=total_chunks,
            documents=documents,
        )

    except (
        EmptyDocumentException,
        NoReadableTextException,
        DocumentProcessingException,
        PDFProcessingException,
        KnowledgeBaseException,
        QdrantConnectionException,
    ):
        raise

    except Exception as ex:
        logger.exception(
            KB_INGESTION_FAILED_LOG,
            ex,
        )
        raise