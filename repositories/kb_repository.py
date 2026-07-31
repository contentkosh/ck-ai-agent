# ==========================================================
# Knowledge Base Repository
# Handles all Qdrant database operations including storing,
# searching, retrieving, and deleting knowledge base documents.
# ==========================================================

from sys import exception
from typing import Any, Optional
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from exceptions.contentkosh_exception import (ContentKoshException,)
from common.logger import logger
from configuration.config import (
    COLLECTION_NAME,
    SCROLL_LIMIT,
    SEARCH_LIMIT
)
from dto.knowledge_base_record_dto import (KnowledgeBaseRecordDto,)
from configuration.constants import (
    METADATA_DOCUMENT_ID,
    METADATA_DOCUMENT_TYPE,
    METADATA_PAGE,
    METADATA_SOURCE,
    METADATA_SUMMARY,
    METADATA_TAG,
    METADATA_TEXT,
    METADATA_TITLE,
    DELETE_DOCUMENT_LOG,
    DELETE_DOCUMENT_FAILED_LOG,
    DOCUMENT_NOT_FOUND_LOG,
    CLEAR_KB_LOG,
    CLEAR_KB_FAILED_LOG,
    FETCH_DOCUMENTS_FAILED_LOG,
    FETCH_DOCUMENTS_LOG,
    FETCH_RECORDS_FAILED_LOG,
    FETCH_RECORDS_LOG,
    SEMANTIC_SEARCH_FAILED_LOG,
    SEMANTIC_SEARCH_LOG,
    VECTOR_INSERTION_FAILED_LOG,
    VECTOR_INSERTION_LOG,
)
<<<<<<< HEAD
from configuration.error_constants import(
    DATABASE_INSERT_ERROR_MESSAGE,
    DATABASE_FETCH_ERROR_MESSAGE,
    DATABASE_SEARCH_ERROR_MESSAGE,
    DATABASE_DELETE_ERROR_MESSAGE,
    DATABASE_CLEAR_ERROR_MESSAGE,
=======
from database.qdrant_client_manager import client

from configuration.config import (
    COLLECTION_NAME,
    SCROLL_LIMIT,
>>>>>>> 83843a0 (Rebased recent commits)
)

from dto.file_response_dto import UploadedDocumentDto
from database.qdrant_client_manager import client
from exceptions.qdrant_exception import (
    QdrantConnectionException,
    QdrantDeleteException,
    QdrantFetchException,
    QdrantInsertException,
    QdrantSearchException,
)

from httpx import ConnectError
from qdrant_client.http.exceptions import ResponseHandlingException

# ==========================================================
# Internal Helper
# ==========================================================

def _scrollRecords(
    queryFilter: Optional[Filter] = None,
) -> list:
    """
    Return all records from Qdrant, paginating through
    the full collection regardless of size.
    """
    allRecords: list = []
    nextOffset = None

    while True:
        records, nextOffset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=queryFilter,
            limit=SCROLL_LIMIT,
            offset=nextOffset,
            with_payload=True,
        )
        allRecords.extend(records)
        if nextOffset is None:
            break

    return allRecords

def buildUploadedDocument(
    payload: dict,
) -> UploadedDocumentDto:
    """
    Build document metadata.
    """
    return UploadedDocumentDto(
        document_id=payload.get(METADATA_DOCUMENT_ID),
        title=payload.get(METADATA_TITLE),
        document_type=payload.get(METADATA_DOCUMENT_TYPE),
        tag=payload.get(METADATA_TAG),
        summary=payload.get(METADATA_SUMMARY),
        source=payload.get(METADATA_SOURCE),
    )

def buildKnowledgeBaseRecord(
    payload: dict,
) -> KnowledgeBaseRecordDto:
    """
    Build a Knowledge Base record from a Qdrant payload.
    """
    return KnowledgeBaseRecordDto(
        document_id=payload.get(METADATA_DOCUMENT_ID),
        title=payload.get(METADATA_TITLE),
        document_type=payload.get(METADATA_DOCUMENT_TYPE),
        tag=payload.get(METADATA_TAG),
        summary=payload.get(METADATA_SUMMARY),
        source=payload.get(METADATA_SOURCE),
        page=payload.get(METADATA_PAGE),
        text=payload.get(METADATA_TEXT),
    )

# ==========================================================
# Detect Qdrant Connection Failure
# ==========================================================

def isQdrantConnectionError(
    exception: Exception,
) -> bool:
    """
    Return True when the Qdrant server is unreachable.
    """
    return (
        isinstance(
            exception,
            ResponseHandlingException,
        )
        and isinstance(
            getattr(
                exception,
                "source",
                None,
            ),
            ConnectError,
        )
    )
# ==========================================================
# Save Chunks
# ==========================================================

def saveChunks(
    points: list,
) -> None:
    """
    Save vectors to Qdrant.
    """
    try:
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        logger.info(
            VECTOR_INSERTION_LOG,
            len(points),
        )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        logger.info(
            VECTOR_INSERTION_LOG,
            len(points),
        )

    except Exception as exception:
        logger.exception(
            VECTOR_INSERTION_FAILED_LOG,
            exception,
        )

        if isQdrantConnectionError(exception):
            raise ContentKoshException(
                DATABASE_INSERT_ERROR_MESSAGE,
                cause=QdrantConnectionException(),
            ) from exception

        raise ContentKoshException(
            DATABASE_INSERT_ERROR_MESSAGE,
            cause=QdrantInsertException(),
        ) from exception

# ==========================================================
# Semantic Search
# ==========================================================

def searchChunks(
    queryEmbedding: list[float],
    limit: int = SEARCH_LIMIT,
    scoreThreshold: Optional[float] = None,
):
    """
    Search similar chunks. Results below scoreThreshold
    (Qdrant cosine similarity) are excluded server-side.
    """
    try:
        searchResult = client.query_points(
            collection_name=COLLECTION_NAME,
            query=queryEmbedding,
            limit=limit,
            score_threshold=scoreThreshold,
        )
        logger.info("%s: %s",SEMANTIC_SEARCH_LOG,len(searchResult.points))
        return searchResult.points
    
    except Exception as ex:
        logger.exception("%s: %s",SEMANTIC_SEARCH_FAILED_LOG,ex,)

        if isQdrantConnectionError(ex):
            raise ContentKoshException(DATABASE_SEARCH_ERROR_MESSAGE,cause=QdrantConnectionException(),) from ex
        raise ContentKoshException(DATABASE_SEARCH_ERROR_MESSAGE,cause=QdrantSearchException(),) from ex


def getAllRecords(
    tag: Optional[str] = None,
) -> list[KnowledgeBaseRecordDto]:
    """
    Retrieve all stored chunks, optionally filtered by tag.
    Filtering happens server-side in Qdrant rather than
    pulling the whole collection into memory.
    """
    try:
        queryFilter = None
        if tag:
            queryFilter = Filter(
                must=[
                    FieldCondition(
                        key=METADATA_TAG,
                        match=MatchValue(value=tag),
                    ),
                ],
            )

        records = _scrollRecords(queryFilter)

        responseRecords = [
            buildKnowledgeBaseRecord(point.payload)
            for point in records
            ]

        logger.info("%s: %s",FETCH_RECORDS_LOG,len(responseRecords),)
        return responseRecords

    except Exception as ex:
        logger.exception("%s: %s",FETCH_RECORDS_FAILED_LOG,ex,)

        if isQdrantConnectionError(ex):
            raise ContentKoshException(
                DATABASE_FETCH_ERROR_MESSAGE,
                cause=QdrantConnectionException(),
            ) from ex

        raise ContentKoshException(
            DATABASE_FETCH_ERROR_MESSAGE,
            cause=QdrantFetchException(),
        ) from ex

def getUploadedFiles() -> list[UploadedDocumentDto]:
    """
    Return one entry per uploaded document.
    """
    try:
        records = _scrollRecords()
        documents: dict[str, UploadedDocumentDto] = {}

        for point in records:
            payload = point.payload

            documentId = payload.get(
                METADATA_DOCUMENT_ID,
            )

            if not documentId:
                continue

            if documentId not in documents:
                documents[documentId] = buildUploadedDocument(
                    payload,
                )
        logger.info("%s: %s",FETCH_DOCUMENTS_LOG,len(documents))
        return list(documents.values())
    except Exception as ex:
        logger.exception("%s: %s",FETCH_DOCUMENTS_FAILED_LOG,ex,)

        if isQdrantConnectionError(ex):
            raise ContentKoshException(
                DATABASE_FETCH_ERROR_MESSAGE,
                cause=QdrantConnectionException(),
            ) from ex

        raise ContentKoshException(
            DATABASE_FETCH_ERROR_MESSAGE,
            cause=QdrantFetchException(),
        ) from ex

# ==========================================================
# Delete One Document
# ==========================================================

def deleteDocument(
    documentId: str,
) -> bool:
    """
    Delete all chunks belonging to one document.
    Returns False if no chunks matched that documentId.
    """
    try:
        documentFilter = Filter(
            must=[
                FieldCondition(
                    key=METADATA_DOCUMENT_ID,
                    match=MatchValue(
                        value=documentId,
                    ),
                ),
            ],
        )

        existing, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=documentFilter,
            limit=1,
            with_payload=False,
        )

        if not existing:
            logger.info("%s: %s",DOCUMENT_NOT_FOUND_LOG,documentId,)
            return False
        client.delete(collection_name=COLLECTION_NAME,points_selector=documentFilter,)
        logger.info("%s: %s",DELETE_DOCUMENT_LOG,documentId,)
        return True
    except Exception as ex:
        logger.exception("%s: %s",DELETE_DOCUMENT_FAILED_LOG,ex,)

        if isQdrantConnectionError(ex):
            raise ContentKoshException(
                DATABASE_DELETE_ERROR_MESSAGE,
                cause=QdrantConnectionException(),
            ) from ex

        raise ContentKoshException(
            DATABASE_DELETE_ERROR_MESSAGE,
            cause=QdrantDeleteException(),
        ) from ex

# ==========================================================
# Delete Entire Knowledge Base
# ==========================================================

def deleteAllDocuments() -> bool:
    """
    Remove every vector from Qdrant.
    """
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(),
        )

        logger.info(
            CLEAR_KB_LOG,
        )

        return True

    except Exception as exception:
        logger.exception(
            "%s: %s",
            CLEAR_KB_FAILED_LOG,
            exception,
        )

        if isQdrantConnectionError(exception):
            raise ContentKoshException(
                DATABASE_CLEAR_ERROR_MESSAGE,
                cause=QdrantConnectionException(),
            ) from exception

        raise ContentKoshException(
            DATABASE_CLEAR_ERROR_MESSAGE,
            cause=QdrantDeleteException(
                DATABASE_CLEAR_ERROR_MESSAGE,
            ),
        ) from exception