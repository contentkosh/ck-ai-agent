from typing import Any
from typing import Optional
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from database.qdrant_client_manager import client

from configuration.app_settings import (
    COLLECTION_NAME,
    SCROLL_LIMIT
)

from common.logger import logger
from common.custom_exceptions import DatabaseException

Payload = dict[str, Any]


# ==========================================================
# Internal Helper
# ==========================================================

def _scroll_records():
    """Return all records from Qdrant."""

    records, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=SCROLL_LIMIT,
        with_payload=True,
    )

    return records


def build_document_payload(payload: Payload) -> Payload:
    """Build document metadata."""

    return {
        "document_id": payload.get("document_id"),
        "title": payload.get("title"),
        "document_type": payload.get("document_type"),
        "tag": payload.get("tag"),
        "summary": payload.get("summary"),
        "source": payload.get("source"),
    }


# ==========================================================
# Save Chunks
# ==========================================================

def save_chunks(points: list) -> None:
    """Save vectors to Qdrant."""

    try:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        logger.info(
            "Inserted %d vectors.",
            len(points),
        )

    except Exception as ex:
        logger.exception(
            "Vector insertion failed: %s",
            ex,
        )

        raise DatabaseException(
            "Unable to insert vectors."
        ) from ex

# ==========================================================
# Semantic Search
# ==========================================================

def search_chunks(
    query_embedding: list[float],
    limit: int = 5,
):
    """Search similar chunks."""

    try:
        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit,
        )

        logger.info(
            "Retrieved %d chunks.",
            len(result.points),
        )

        return result.points

    except Exception as ex:
        logger.exception(
            "Semantic search failed: %s",
            ex,
        )

        raise DatabaseException(
            "Semantic search failed."
        ) from ex


# ==========================================================
# Get All Records
# ==========================================================

def get_all_records(
    tag: Optional[str] = None
):
    """
    Retrieve all stored chunks.
    """

    try:

        records = _scroll_records()

        response = []

        for point in records:

            payload = point.payload

            if tag and payload.get("tag") != tag:
                continue

            record = build_document_payload(payload)

            record["page"] = payload.get("page")
            record["text"] = payload.get("text")

            response.append(record)
        
        logger.info(
            "Fetched %d records.",
            len(response),
        )

        return response

    except Exception as ex:

        logger.exception(
            "Unable to fetch records."
        )

        raise DatabaseException(
            "Unable to fetch records."
        ) from ex


# ==========================================================
# Get Uploaded Documents
# ==========================================================

def get_uploaded_files():
    """
    Return one entry per uploaded document.
    """

    try:

        records = _scroll_records()

        documents = {}

        for point in records:

            payload = point.payload

            document_id = payload.get(
                "document_id"
            )

            if not document_id:

                continue

            if document_id not in documents:

                documents[document_id] = build_document_payload(
                    payload
            )

        logger.info(
            "Found %d document(s).",
            len(documents),
        )

        return list(documents.values())

    except Exception as ex:

        logger.exception(
            "Unable to fetch uploaded documents."
        )

        raise DatabaseException(
            "Unable to fetch records."
        ) from ex


# ==========================================================
# Delete One Document
# ==========================================================

def delete_document(
    document_id: str
):
    """
    Delete all chunks belonging to one document.
    """

    try:

        client.delete(

            collection_name=COLLECTION_NAME,

            points_selector=Filter(

                must=[

                    FieldCondition(

                        key="document_id",

                        match=MatchValue(
                            value=document_id
                        )

                    )

                ]

            )

        )

        logger.info(
            "Deleted document %s.",
            document_id,
        )

        return True

    except Exception as ex:

        logger.exception(
            "Unable to delete document."
        )

        raise DatabaseException(
            "Unable to fetch records."
        ) from ex


# ==========================================================
# Delete Entire Knowledge Base
# ==========================================================

def delete_all_documents():
    """
    Remove every vector from Qdrant.
    """

    try:

        client.delete(

            collection_name=COLLECTION_NAME,

            points_selector=Filter()

        )

        logger.info(
            "Knowledge Base cleared."
        )

        return True

    except Exception as ex:

        logger.exception(
            "Unable to clear Knowledge Base."
        )

        raise DatabaseException(
            "Unable to clear Knowledge Base."
        ) from ex