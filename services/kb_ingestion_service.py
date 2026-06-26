import uuid
from typing import List

from fastapi import UploadFile
from pypdf import PdfReader
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from configuration.app_settings import (
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

from repositories.kb_repository import save_chunks

from services.document_metadata_service import (
    extract_document_metadata
)

from common.file_utils import save_uploaded_file
from common.validators import validate_file_size
from common.logger import logger
from common.custom_exceptions import (
    PDFProcessingException,
    EmbeddingException
)


# ==========================================================
# Embedding Model
# ==========================================================

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ==========================================================
# Text Splitter
# ==========================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)


# ==========================================================
# Generate Embedding
# ==========================================================

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector.
    """

    try:

        return embedding_model.encode(
            text
        ).tolist()

    except Exception as e:

        logger.exception(
            "Embedding generation failed."
        )

        raise EmbeddingException(
            str(e)
        )


# ==========================================================
# Build Payload
# ==========================================================

def build_payload(
    chunk: str,
    metadata: dict,
    filename: str,
    document_id: str,
    page_number: int
):
    """
    Create payload for each chunk.
    """

    return {

        "document_id": document_id,

        "text": chunk,

        "title": metadata.get("title"),

        "document_type": metadata.get(
            "document_type"
        ),

        "tag": metadata.get(
            "tag"
        ),

        "summary": metadata.get(
            "summary"
        ),

        "source": filename,

        "page": page_number

    }
# ==========================================================
# Read PDF
# ==========================================================

def read_pdf(file: UploadFile):
    """
    Save the uploaded PDF and return the PdfReader
    along with the saved file path.
    """

    try:

        logger.info(
            f"Saving uploaded file: {file.filename}"
        )

        saved_file = save_uploaded_file(file)

        validate_file_size(saved_file)

        pdf = PdfReader(saved_file)

        logger.info(
            f"PDF loaded successfully: {file.filename}"
        )

        return pdf, saved_file

    except Exception as e:

        logger.exception(
            "Unable to read uploaded PDF."
        )

        raise PDFProcessingException(
            f"Unable to read PDF: {str(e)}"
        )


# ==========================================================
# Extract Document Text
# ==========================================================

def extract_document_text(pdf: PdfReader):
    """
    Extract text from all pages of the PDF.

    Returns:
        full_text -> Complete document text
        pages -> List of page dictionaries
    """

    full_text = ""

    pages = []

    for page_number, page in enumerate(
        pdf.pages,
        start=1
    ):

        try:

            page_text = page.extract_text() or ""

        except Exception:

            logger.warning(
                f"Unable to extract page {page_number}."
            )

            page_text = ""

        pages.append({

            "page": page_number,

            "text": page_text

        })

        full_text += page_text + "\n"

    logger.info(

        f"{len(pages)} pages extracted."

    )

    return full_text, pages


# ==========================================================
# Extract Metadata
# ==========================================================

def get_document_metadata(pages: list):
    """
    Extract metadata from the first few pages
    using the LLM.
    """

    metadata_source = "\n".join(

        page["text"]

        for page in pages[:3]

    )

    logger.info(
        "Extracting document metadata."
    )

    metadata = extract_document_metadata(
        metadata_source
    )

    logger.info(
        "Metadata extraction completed."
    )

    return metadata
# ==========================================================
# Process Document
# ==========================================================

def process_document(
    pdf: PdfReader,
    filename: str
):
    """
    Process a single document and return
    Qdrant PointStruct objects.
    """

    logger.info(
        f"Processing document: {filename}"
    )

    # ------------------------------------
    # Generate unique document id
    # ------------------------------------

    document_id = str(uuid.uuid4())

    # ------------------------------------
    # Extract text
    # ------------------------------------

    full_text, pages = extract_document_text(
        pdf
    )

    if not pages:

        raise PDFProcessingException(
            "No pages found in the document."
        )

    # ------------------------------------
    # Extract metadata
    # ------------------------------------

    metadata = get_document_metadata(
        pages
    )

    logger.info(
        f"Metadata extracted for {filename}"
    )

    # ------------------------------------
    # Build vectors
    # ------------------------------------

    points = []

    total_chunks = 0

    for page in pages:

        page_number = page["page"]

        page_text = page["text"]

        if not page_text.strip():

            continue

        chunks = text_splitter.split_text(
            page_text
        )

        logger.info(

            f"Page {page_number} : "

            f"{len(chunks)} chunk(s)"

        )

        for chunk in chunks:

            vector = generate_embedding(
                chunk
            )

            payload = build_payload(

                chunk=chunk,

                metadata=metadata,

                filename=filename,

                document_id=document_id,

                page_number=page_number

            )

            point = PointStruct(

                id=str(uuid.uuid4()),

                vector=vector,

                payload=payload

            )

            points.append(point)

            total_chunks += 1

    logger.info(

        f"{filename} processed successfully."

    )

    logger.info(

        f"Document ID : {document_id}"

    )

    logger.info(

        f"Total chunks : {total_chunks}"

    )

    return {

        "document_id": document_id,

        "metadata": metadata,

        "points": points,

        "chunks": total_chunks

    }
# ==========================================================
# Ingest Documents
# ==========================================================

def ingest_documents(
    files: List[UploadFile]
):
    """
    Ingest one or more PDF documents into
    the Knowledge Base.
    """

    try:

        logger.info(
            "Knowledge Base ingestion started."
        )

        documents = []

        total_chunks = 0

        for file in files:

            logger.info(
                f"Uploading document: {file.filename}"
            )

            # --------------------------------------
            # Read PDF
            # --------------------------------------

            pdf, _ = read_pdf(file)

            # --------------------------------------
            # Process PDF
            # --------------------------------------

            document = process_document(

                pdf=pdf,

                filename=file.filename

            )

            # --------------------------------------
            # Save vectors
            # --------------------------------------

            save_chunks(

                document["points"]

            )

            logger.info(

                f"{len(document['points'])} vectors "

                f"saved successfully."

            )

            total_chunks += document["chunks"]

            documents.append(

                {

                    "document_id": document["document_id"],

                    "title": document["metadata"].get(
                        "title"
                    ),

                    "document_type": document["metadata"].get(
                        "document_type"
                    ),

                    "tag": document["metadata"].get(
                        "tag"
                    ),

                    "summary": document["metadata"].get(
                        "summary"
                    ),

                    "source": file.filename,

                    "chunks": document["chunks"]

                }

            )

        logger.info(

            "Knowledge Base ingestion completed."

        )

        return {

            "status": "success",

            "documents_processed": len(documents),

            "chunks_inserted": total_chunks,

            "documents": documents

        }

    except Exception as e:

        logger.exception(

            "Knowledge Base ingestion failed."

        )

        raise PDFProcessingException(

            f"Unable to ingest document. {str(e)}"

        )