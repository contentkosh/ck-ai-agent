import uuid
from typing import Any, TypedDict

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from qdrant_client.models import PointStruct

from common.custom_exceptions import EmbeddingException, PDFProcessingException
from common.embedding_client import get_embedding_model
from common.file_utils import delete_saved_file, save_uploaded_file
from common.logger import logger
from configuration.config import CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_BATCH_SIZE
from configuration.constants import (
    DOCUMENT_PROCESSING_FAILED_LOG,
    DOCUMENT_PROCESSED_LOG,
    DOCUMENT_PROCESSING_STARTED_LOG,
    FILE_PROCESSING_COMPLETED_LOG,
    FILE_PROCESSING_STARTED_LOG,
    FILE_SAVE_LOG,
    GENERATED_VECTORS_LOG,
    KB_INGESTION_COMPLETED_LOG,
    KB_INGESTION_FAILED_LOG,
    KB_INGESTION_STARTED_LOG,
    METADATA_BUSINESS_ID,
    METADATA_COURSE_ID,
    METADATA_DOCUMENT_ID,
    METADATA_DOCUMENT_TYPE,
    METADATA_EXTRACTION_COMPLETED_LOG,
    METADATA_EXTRACTION_FAILED_LOG,
    METADATA_EXTRACTION_STARTED_LOG,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_SUMMARY,
    METADATA_TAG,
    METADATA_TEXT,
    METADATA_TITLE,
    PAGE_CHUNK_GENERATION_LOG,
    PAGE_READ_FAILED_LOG,
    PAGES_EXTRACTED_LOG,
    PDF_READ_FAILED_LOG,
    SUCCESS_STATUS,
)

from configuration.error_constants import (
    EMBEDDING_GENERATION_FAILED_MESSAGE,
    PDF_READ_FAILED_MESSAGE,
    DOCUMENT_METADATA_EXTRACTION_FAILED_MESSAGE,
)
from dto.document_metadata_dto import DocumentMetadataDto
from dto.file_response_dto import UploadedDocumentDto, UploadedDocumentsResponse
from dto.processed_document_dto import ProcessedDocumentDto
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.document_exception import (
    DocumentProcessingException,
    EmptyDocumentException,
    NoReadableTextException,
)
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.qdrant_exception import QdrantConnectionException
from repositories.kb_repository import deleteDocument, saveChunks
from services.document_metadata_service import extract_document_metadata
from validators.file_validator import validate_saved_file
from validators.upload_validator import validate_upload


class Page(TypedDict):
    page: int
    text: str


_text_splitter: RecursiveCharacterTextSplitter | None = None


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    global _text_splitter

    if _text_splitter is None:
        _text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    return _text_splitter


def generate_uuid() -> str:
    return str(uuid.uuid4())


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


def read_pdf(file: UploadFile) -> tuple[PdfReader, str]:
    filename = file.filename
    saved_file = None

    try:
        logger.info("PDF processing started: %s", filename)
        logger.info(FILE_SAVE_LOG, filename)

        saved_file = save_uploaded_file(file)
        logger.info("PDF saved successfully: %s", filename)

        validate_saved_file(saved_file)
        logger.info("PDF validation completed successfully: %s", filename)

        pdf = PdfReader(saved_file)
        logger.info(
            "PDF loaded successfully: %s | pages=%d",
            filename,
            len(pdf.pages),
        )

        return pdf, saved_file
    except Exception as ex:
        logger.exception(
            PDF_READ_FAILED_LOG,
            filename,
            ex,
        )

        if saved_file is not None:
            try:
                delete_saved_file(saved_file)
                logger.info("Temporary PDF deleted after read failure: %s", filename)
            except Exception:
                logger.exception(
                    "Failed to delete temporary PDF after read failure: %s",
                    filename,
                )

        raise PDFProcessingException(
            PDF_READ_FAILED_MESSAGE.format(filename),
        ) from ex


def extract_document_text(
    pdf: PdfReader,
) -> tuple[str, list[Page]]:
    pages: list[Page] = []
    document_text: list[str] = []

    logger.info(
        "PDF text extraction started. Pages=%d",
        len(pdf.pages),
    )

    for page_number, page in enumerate(pdf.pages, start=1):
        try:
            page_text = page.extract_text() or ""
            logger.info(
                "Page %d text extracted. Characters=%d",
                page_number,
                len(page_text),
            )
        except Exception as ex:
            logger.warning(
                PAGE_READ_FAILED_LOG,
                page_number,
                ex,
            )
            page_text = ""

        pages.append(
            {
                "page": page_number,
                "text": page_text,
            }
        )
        document_text.append(page_text)

    full_text = "\n".join(document_text)

    logger.info(
        PAGES_EXTRACTED_LOG,
        len(pages),
    )
    logger.info(
        "PDF text extraction completed. Characters=%d",
        len(full_text),
    )

    return full_text, pages


def get_document_metadata(
    pages: list[Page],
) -> DocumentMetadataDto:
    try:
        metadata_source = "\n".join(page["text"] for page in pages[:3])

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


def process_embedding_batch(
    *,
    chunk_batch: list[tuple[str, int]],
    metadata: DocumentMetadataDto,
    filename: str,
    document_id: str,
    business_id: str,
    course_ids: list[str],
) -> int:
    chunk_texts = [chunk for chunk, _ in chunk_batch]

    logger.info(
        "Embedding batch started. File=%s | chunks=%d",
        filename,
        len(chunk_batch),
    )

    try:
        embeddings = get_embedding_model().encode(
            chunk_texts,
            batch_size=EMBEDDING_BATCH_SIZE,
        )
        logger.info(
            "Embedding batch generated successfully. File=%s | chunks=%d",
            filename,
            len(chunk_batch),
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

    logger.info(
        "Qdrant vector insertion started. File=%s | vectors=%d",
        filename,
        len(points),
    )

    try:
        saveChunks(
            points,
            business_id,
        )
        logger.info(
            "Qdrant vector insertion completed. File=%s | vectors=%d",
            filename,
            len(points),
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


def build_vectors(
    *,
    pages: list[Page],
    metadata: DocumentMetadataDto,
    filename: str,
    document_id: str,
    business_id: str,
    course_ids: list[str],
) -> int:
    splitter = get_text_splitter()
    chunk_batch: list[tuple[str, int]] = []
    total_chunks = 0

    logger.info(
        "Chunking started. File=%s | pages=%d | chunk_size=%d | overlap=%d",
        filename,
        len(pages),
        CHUNK_SIZE,
        CHUNK_OVERLAP,
    )

    try:
        for page in pages:
            page_text = page["text"]

            if not page_text.strip():
                logger.info(
                    "Page %d skipped because it contains no readable text.",
                    page["page"],
                )
                continue

            page_number = page["page"]

            chunks = splitter.split_text(page_text)

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
            logger.info(
                "Document rollback started. Document ID=%s",
                document_id,
            )
            deleteDocument(
                documentId=document_id,
                businessId=business_id,
            )
            logger.info(
                "Document rollback completed. Document ID=%s",
                document_id,
            )
        except Exception:
            logger.exception(
                "Failed to rollback document %s",
                document_id,
            )

        raise

    logger.info(
        GENERATED_VECTORS_LOG,
        total_chunks,
    )
    logger.info(
        "Chunking and vector generation completed. File=%s | chunks=%d",
        filename,
        total_chunks,
    )

    return total_chunks


def process_document(
    pdf: PdfReader,
    filename: str,
    business_id: str,
    course_ids: list[str],
) -> ProcessedDocumentDto:
    try:
        logger.info(
            DOCUMENT_PROCESSING_STARTED_LOG,
            filename,
        )

        document_id = generate_uuid()
        logger.info(
            "Document ID generated. File=%s | document_id=%s",
            filename,
            document_id,
        )

        full_text, pages = extract_document_text(pdf)

        if not full_text.strip():
            logger.error(
                "Document contains no readable text: %s",
                filename,
            )
            raise NoReadableTextException()

        logger.info(
            "Readable document text confirmed. File=%s",
            filename,
        )

        metadata = get_document_metadata(pages)

        logger.info(
            "Document metadata processing completed. File=%s",
            filename,
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


def ingest_documents(
    *,
    files: list[UploadFile],
    business_id: str,
    course_ids: list[str],
) -> dict[str, Any]:
    validate_upload(files)

    try:
        logger.info(
            KB_INGESTION_STARTED_LOG,
        )
        logger.info(
            "Ingestion request details. Files=%d | business_id=%s | course_ids=%s",
            len(files),
            business_id,
            course_ids,
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

                    if stream is not None and not stream.closed:
                        stream.close()
                        logger.info(
                            "PDF stream closed: %s",
                            file.filename,
                        )
                except Exception:
                    logger.exception(
                        "Failed to close PDF stream: %s",
                        file.filename,
                    )

                del pdf

                try:
                    delete_saved_file(saved_file_path)
                    logger.info(
                        "Temporary upload file deleted: %s",
                        file.filename,
                    )
                except Exception:
                    logger.exception(
                        "Failed to delete temporary upload file: %s",
                        file.filename,
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
