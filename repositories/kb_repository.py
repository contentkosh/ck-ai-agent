# ==========================================================
# Knowledge Base Repository
# Handles all Qdrant database operations including storing,
# searching, retrieving, and deleting knowledge base documents.
# ==========================================================

from typing import Optional
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from exceptions.qdrant_exception import (
    QdrantInsertException,
    QdrantSearchException,
    QdrantFetchException,
    QdrantDeleteException,
)
from exceptions.qdrant_exception import (
    QdrantInsertException,
    QdrantSearchException,
)
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
from dto.document_payload_dto import DocumentPayloadDto
from database.qdrant_client_manager import client

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

def buildDocumentPayload(
    payload: dict,
) -> DocumentPayloadDto:
    """
    Build document metadata.
    """
    return DocumentPayloadDto(
        document_id=payload.get(METADATA_DOCUMENT_ID),
        title=payload.get(METADATA_TITLE),
        document_type=payload.get(METADATA_DOCUMENT_TYPE),
        tag=payload.get(METADATA_TAG),
        summary=payload.get(METADATA_SUMMARY),
        source=payload.get(METADATA_SOURCE),
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

        client.upsert(collection_name=COLLECTION_NAME,points=points,)
        logger.info(VECTOR_INSERTION_LOG,len(points),)

    except Exception as ex:
        logger.exception(VECTOR_INSERTION_FAILED_LOG,ex,)
        raise QdrantInsertException() from ex

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
        logger.info(SEMANTIC_SEARCH_LOG,len(searchResult.points))
        return searchResult.points
    except Exception as ex:
        logger.exception(SEMANTIC_SEARCH_FAILED_LOG,ex)
        raise QdrantSearchException() from ex

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
        responseRecords: list[KnowledgeBaseRecordDto] = []

        for point in records:
           documentPayload = point.payload
           responseRecords.append(
                KnowledgeBaseRecordDto(
                    document_id=documentPayload.get(METADATA_DOCUMENT_ID,),
                    title=documentPayload.get(METADATA_TITLE,),
                    document_type=documentPayload.get(METADATA_DOCUMENT_TYPE,),
                    tag=documentPayload.get(METADATA_TAG,),
                    summary=documentPayload.get(METADATA_SUMMARY,),
                    source=documentPayload.get(METADATA_SOURCE,),
                    page=documentPayload.get(METADATA_PAGE,),
                    text=documentPayload.get(METADATA_TEXT,),
                )
            )

        logger.info(FETCH_RECORDS_LOG,len(responseRecords))
        return responseRecords

    except Exception as ex:
        logger.exception(FETCH_RECORDS_FAILED_LOG,ex)
        raise QdrantFetchException() from ex

def getUploadedFiles() -> list[DocumentPayloadDto]:
    """
    Return one entry per uploaded document.
    """
    try:
        records = _scrollRecords()
        documents: dict[str, DocumentPayloadDto] = {}
        for point in records:
            payload = point.payload
            documentId = payload.get(
                METADATA_DOCUMENT_ID,
            )
            if not documentId:
                continue
            if documentId not in documents:
                documents[documentId] = buildDocumentPayload(
                    payload,
                )
        logger.info(FETCH_DOCUMENTS_LOG,len(documents))
        return list(documents.values())
    except Exception as ex:
        logger.exception(FETCH_DOCUMENTS_FAILED_LOG,ex,)
        raise QdrantFetchException() from ex

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
            logger.info(DOCUMENT_NOT_FOUND_LOG,documentId,)
            return False
        client.delete(collection_name=COLLECTION_NAME,points_selector=documentFilter,)
        logger.info(DELETE_DOCUMENT_LOG,documentId,)
        return True
    except Exception as ex:
        logger.exception(DELETE_DOCUMENT_FAILED_LOG, ex,)
        raise QdrantDeleteException() from ex

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

        logger.info(CLEAR_KB_LOG,)
        return True
    except Exception as ex:
        logger.exception(CLEAR_KB_FAILED_LOG,ex,)
        raise QdrantDeleteException() from ex