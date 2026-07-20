from typing import Any
from typing import Optional
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from common.custom_exceptions import DatabaseException
from common.logger import logger
from configuration.config import (
    COLLECTION_NAME,
    SCROLL_LIMIT,
    SEARCH_LIMIT,
)

from configuration.constants import (
    METADATA_DOCUMENT_ID,
    METADATA_DOCUMENT_TYPE,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_SUMMARY,
    METADATA_TAG,
    METADATA_TEXT,
    METADATA_TITLE,
    DATABASE_DELETE_ERROR_MESSAGE,
    DATABASE_CLEAR_ERROR_MESSAGE,
    DELETE_DOCUMENT_LOG,
    DELETE_DOCUMENT_FAILED_LOG,
    CLEAR_KB_LOG,
    CLEAR_KB_FAILED_LOG,
    DATABASE_FETCH_DOCUMENTS_ERROR_MESSAGE,
    DATABASE_FETCH_ERROR_MESSAGE,
    DATABASE_INSERT_ERROR_MESSAGE,
    DATABASE_SEARCH_ERROR_MESSAGE,
    FETCH_DOCUMENTS_FAILED_LOG,
    FETCH_DOCUMENTS_LOG,
    FETCH_RECORDS_FAILED_LOG,
    FETCH_RECORDS_LOG,
    SEMANTIC_SEARCH_FAILED_LOG,
    SEMANTIC_SEARCH_LOG,
    VECTOR_INSERTION_FAILED_LOG,
    VECTOR_INSERTION_LOG,
)
from database.qdrant_client_manager import client
Payload = dict[str, Any]

# ==========================================================
# Internal Helper
# ==========================================================

def _scroll_records(
    query_filter: Optional[Filter] = None,
) -> list:
    """
    Return all records from Qdrant, paginating through
    the full collection regardless of size.
    """
    all_records: list = []
    next_offset = None

    while True:
        records, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=query_filter,
            limit=SCROLL_LIMIT,
            offset=next_offset,
            with_payload=True,
        )
        all_records.extend(records)
        if next_offset is None:
            break

    return all_records

def build_document_payload(
    payload: Payload,
) -> Payload:
    """
    Build document metadata.
    """
    return {
        METADATA_DOCUMENT_ID: payload.get(
            METADATA_DOCUMENT_ID
        ),
        METADATA_TITLE: payload.get(
            METADATA_TITLE
        ),
        METADATA_DOCUMENT_TYPE: payload.get(
            METADATA_DOCUMENT_TYPE
        ),
        METADATA_TAG: payload.get(
            METADATA_TAG
        ),
        METADATA_SUMMARY: payload.get(
            METADATA_SUMMARY
        ),
        METADATA_SOURCE: payload.get(
            METADATA_SOURCE
        ),
    }

# ==========================================================
# Save Chunks
# ==========================================================

def save_chunks(
    points: list,
) -> None:
    """
    Save vectors to Qdrant.
    """
    try:

        client.upsert(collection_name=COLLECTION_NAME,points=points,)
        logger.info(VECTOR_INSERTION_LOG,len(points),)

    except Exception as ex:
        logger.exception(VECTOR_INSERTION_FAILED_LOG,ex,)
        raise DatabaseException(DATABASE_INSERT_ERROR_MESSAGE,) from ex

# ==========================================================
# Semantic Search
# ==========================================================

def search_chunks(
    query_embedding: list[float],
    limit: int = SEARCH_LIMIT,
    score_threshold: Optional[float] = None,
):
    """
    Search similar chunks. Results below score_threshold
    (Qdrant cosine similarity) are excluded server-side.
    """
    try:

        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )
        logger.info(SEMANTIC_SEARCH_LOG,len(result.points),)
        return result.points

    except Exception as ex:
        logger.exception(SEMANTIC_SEARCH_FAILED_LOG,ex,)
        raise DatabaseException(DATABASE_SEARCH_ERROR_MESSAGE,) from ex
    
# ==========================================================
# Get All Records
# ==========================================================

def get_all_records(
    tag: Optional[str] = None,
) -> list[Payload]:
    """
    Retrieve all stored chunks, optionally filtered by tag.
    Filtering happens server-side in Qdrant rather than
    pulling the whole collection into memory.
    """
    try:
        query_filter = None
        if tag:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key=METADATA_TAG,
                        match=MatchValue(value=tag),
                    ),
                ],
            )

        records = _scroll_records(query_filter)
        response: list[Payload] = []
        for point in records:
            payload = point.payload
            record = build_document_payload(payload,)
            record[METADATA_PAGE] = payload.get(METADATA_PAGE)
            record[METADATA_TEXT] = payload.get(METADATA_TEXT)
            response.append(record)

        logger.info(FETCH_RECORDS_LOG,len(response),)
        return response

    except Exception as ex:
        logger.exception(FETCH_RECORDS_FAILED_LOG)
        raise DatabaseException(DATABASE_FETCH_ERROR_MESSAGE,) from ex

# ==========================================================
# Get Uploaded Documents
# ==========================================================

def get_uploaded_files() -> list[Payload]:
    """
    Return one entry per uploaded document.
    """
    try:

        records = _scroll_records()
        documents: dict[str, Payload] = {}
        for point in records:
            payload = point.payload
            document_id = payload.get(METADATA_DOCUMENT_ID,)
            if not document_id:
                continue
            if document_id not in documents:
                documents[
                    document_id
                ] = build_document_payload(
                    payload,
                )

        logger.info(FETCH_DOCUMENTS_LOG,len(documents),)
        return list(documents.values())
    
    except Exception as ex:
        logger.exception(FETCH_DOCUMENTS_FAILED_LOG)
        raise DatabaseException(DATABASE_FETCH_DOCUMENTS_ERROR_MESSAGE,) from ex

# ==========================================================
# Delete One Document
# ==========================================================

def delete_document(
    document_id: str,
) -> bool:
    """
    Delete all chunks belonging to one document.
    Returns False if no chunks matched that document_id.
    """
    try:
        document_filter = Filter(
            must=[
                FieldCondition(
                    key=METADATA_DOCUMENT_ID,
                    match=MatchValue(
                        value=document_id,)
                ),
            ],
        )

        existing, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=document_filter,
            limit=1,
            with_payload=False,
        )
        if not existing:
            logger.info("Document %s not found; nothing deleted.", document_id)
            return False

        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=document_filter,
        )
        logger.info(DELETE_DOCUMENT_LOG,document_id,)
        return True

    except Exception as ex:
        logger.exception(DELETE_DOCUMENT_FAILED_LOG)
        raise DatabaseException(DATABASE_DELETE_ERROR_MESSAGE,) from ex
    
# ==========================================================
# Delete Entire Knowledge Base
# ==========================================================

def delete_all_documents() -> bool:
    """
    Remove every vector from Qdrant.
    """
    try:

        client.delete(collection_name=COLLECTION_NAME,points_selector=Filter(),)
        logger.info(CLEAR_KB_LOG,)
        return True

    except Exception as ex:
        logger.exception(CLEAR_KB_FAILED_LOG)
        raise DatabaseException(DATABASE_CLEAR_ERROR_MESSAGE,) from ex