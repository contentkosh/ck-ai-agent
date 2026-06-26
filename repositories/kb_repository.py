from typing import List, Optional

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


# ==========================================================
# Internal Helper
# ==========================================================

def _scroll_records():
    """
    Retrieve all records from Qdrant.
    """

    records, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=SCROLL_LIMIT,
        with_payload=True
    )

    return records


# ==========================================================
# Save Chunks
# ==========================================================

def save_chunks(points: List):
    """
    Save vectors into Qdrant.
    """

    try:

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        logger.info(
            f"{len(points)} vectors inserted."
        )

    except Exception as e:

        logger.exception(
            "Unable to insert vectors."
        )

        raise DatabaseException(str(e))


# ==========================================================
# Semantic Search
# ==========================================================

def search_chunks(
    query_embedding: List[float],
    limit: int = 5
):
    """
    Search similar chunks.
    """

    try:

        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit
        )

        logger.info(
            f"{len(result.points)} chunks retrieved."
        )

        return result.points

    except Exception as e:

        logger.exception(
            "Semantic search failed."
        )

        raise DatabaseException(str(e))


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

            response.append({

                "document_id": payload.get(
                    "document_id"
                ),

                "title": payload.get(
                    "title"
                ),

                "document_type": payload.get(
                    "document_type"
                ),

                "tag": payload.get(
                    "tag"
                ),

                "summary": payload.get(
                    "summary"
                ),

                "source": payload.get(
                    "source"
                ),

                "page": payload.get(
                    "page"
                ),

                "text": payload.get(
                    "text"
                )

            })

        logger.info(
            f"{len(response)} records fetched."
        )

        return response

    except Exception as e:

        logger.exception(
            "Unable to fetch records."
        )

        raise DatabaseException(str(e))


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

                documents[document_id] = {

                    "document_id": document_id,

                    "title": payload.get(
                        "title"
                    ),

                    "document_type": payload.get(
                        "document_type"
                    ),

                    "tag": payload.get(
                        "tag"
                    ),

                    "summary": payload.get(
                        "summary"
                    ),

                    "source": payload.get(
                        "source"
                    )

                }

        logger.info(
            f"{len(documents)} document(s) found."
        )

        return list(documents.values())

    except Exception as e:

        logger.exception(
            "Unable to fetch uploaded documents."
        )

        raise DatabaseException(str(e))


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
            f"{document_id} deleted."
        )

        return True

    except Exception as e:

        logger.exception(
            "Unable to delete document."
        )

        raise DatabaseException(str(e))


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

    except Exception as e:

        logger.exception(
            "Unable to clear Knowledge Base."
        )

        raise DatabaseException(str(e))