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

from common.custom_exceptions import DatabaseException
from exceptions.contentkosh_exception import ContentKoshException
from common.logger import logger

from configuration.config import (
    SCROLL_LIMIT,
    SEARCH_LIMIT,
)

from dto.knowledge_base_record_dto import (
    KnowledgeBaseRecordDto,
)

from configuration.constants import (
    METADATA_BUSINESS_ID,
    METADATA_COURSE_ID,
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

from configuration.error_constants import (
    DATABASE_INSERT_ERROR_MESSAGE,
    DATABASE_SEARCH_ERROR_MESSAGE,
    DATABASE_FETCH_ERROR_MESSAGE,
    DATABASE_DELETE_ERROR_MESSAGE,
    DATABASE_CLEAR_ERROR_MESSAGE,
)

from database.qdrant_client_manager import client
from database.collection_setup import create_collection_if_missing

from common.collection_utils import (
    get_kb_collection_name,
)

from dto.file_response_dto import UploadedDocumentDto

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
    collectionName: str,
    queryFilter: Optional[Filter] = None,
) -> list:
    """
    Return all records from a business-specific Qdrant
    collection, paginating through the full collection.
    """
    allRecords: list = []
    nextOffset = None

    while True:
        records, nextOffset = client.scroll(
            collection_name=collectionName,
            scroll_filter=queryFilter,
            limit=SCROLL_LIMIT,
            offset=nextOffset,
            with_payload=True,
        )

        allRecords.extend(records)

        if nextOffset is None:
            break

    return allRecords


def ensureCollection(
    businessId: str,
) -> str:
    """
    Return the Knowledge Base collection for a business
    and create it if it does not already exist.
    """
    collectionName = get_kb_collection_name(
        businessId,
    )

    create_collection_if_missing(
        collectionName,
    )

    return collectionName


def buildUploadedDocument(
    payload: dict,
) -> UploadedDocumentDto:
    """
    Build document metadata.
    """
    return UploadedDocumentDto(
        document_id=payload.get(
            METADATA_DOCUMENT_ID,
        ),
        title=payload.get(
            METADATA_TITLE,
        ),
        document_type=payload.get(
            METADATA_DOCUMENT_TYPE,
        ),
        tag=payload.get(
            METADATA_TAG,
        ),
        summary=payload.get(
            METADATA_SUMMARY,
        ),
        source=payload.get(
            METADATA_SOURCE,
        ),
    )


def buildKnowledgeBaseRecord(
    payload: dict,
) -> KnowledgeBaseRecordDto:
    """
    Build a Knowledge Base record from a Qdrant payload.
    """
    return KnowledgeBaseRecordDto(
        document_id=payload.get(
            METADATA_DOCUMENT_ID,
        ),
        title=payload.get(
            METADATA_TITLE,
        ),
        document_type=payload.get(
            METADATA_DOCUMENT_TYPE,
        ),
        tag=payload.get(
            METADATA_TAG,
        ),
        summary=payload.get(
            METADATA_SUMMARY,
        ),
        source=payload.get(
            METADATA_SOURCE,
        ),
        page=payload.get(
            METADATA_PAGE,
        ),
        text=payload.get(
            METADATA_TEXT,
        ),
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
    businessId: str,
) -> None:
    """
    Save vectors into the business-specific Knowledge Base
    collection.
    """
    collectionName = ensureCollection(
        businessId,
    )

    try:
        client.upsert(
            collection_name=collectionName,
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

def _buildMetadataFilter(
    courseId: Optional[str] = None,
    tag: Optional[str] = None,
) -> Optional[Filter]:
    """
    Build a Qdrant filter using optional metadata fields.
    """
    mustConditions = []

    if courseId:
        mustConditions.append(
            FieldCondition(
                key=METADATA_COURSE_ID,
                match=MatchValue(
                    value=courseId,
                ),
            ),
        )

    if tag:
        mustConditions.append(
            FieldCondition(
                key=METADATA_TAG,
                match=MatchValue(
                    value=tag,
                ),
            ),
        )

    return (
        Filter(must=mustConditions)
        if mustConditions
        else None
    )


# ==========================================================
# Semantic Search
# ==========================================================

def searchChunks(
    queryEmbedding: list[float],
    businessId: str,
    courseId: str,
    limit: int = SEARCH_LIMIT,
    scoreThreshold: Optional[float] = None,
):
    """
    Search similar chunks within a specific business and
    course.

    The business determines the Qdrant collection.
    The course determines the payload filter.
    """
    collectionName = ensureCollection(
        businessId,
    )

    try:
        queryFilter = _buildMetadataFilter(
            courseId=courseId,
        )
        searchResult = client.query_points(
            collection_name=collectionName,
            query=queryEmbedding,
            query_filter=queryFilter,
            limit=limit,
            score_threshold=scoreThreshold,
        )

        logger.info(
            "%s: %s",
            SEMANTIC_SEARCH_LOG,
            len(searchResult.points),
        )

        return searchResult.points

    except Exception as ex:
        logger.exception(
            "%s: %s",
            SEMANTIC_SEARCH_FAILED_LOG,
            ex,
        )

        if isQdrantConnectionError(ex):
            raise ContentKoshException(
                DATABASE_SEARCH_ERROR_MESSAGE,
                cause=QdrantConnectionException(),
            ) from ex

        raise ContentKoshException(
            DATABASE_SEARCH_ERROR_MESSAGE,
            cause=QdrantSearchException(),
        ) from ex


# ==========================================================
# Get All Records
# ==========================================================

def getAllRecords(
    businessId: str,
    courseId: Optional[str] = None,
    tag: Optional[str] = None,
) -> list[KnowledgeBaseRecordDto]:
    """
    Retrieve stored chunks for a specific business.

    Optionally filter by course and tag.
    """
    collectionName = ensureCollection(
        businessId,
    )

    try:
        queryFilter = _buildMetadataFilter(
            courseId=courseId,
            tag=tag,
        )

        records = _scrollRecords(
            collectionName,
            queryFilter,
        )

        responseRecords = [
            buildKnowledgeBaseRecord(
                point.payload,
            )
            for point in records
        ]

        logger.info(
            "%s: %s",
            FETCH_RECORDS_LOG,
            len(responseRecords),
        )

        return responseRecords

    except Exception as ex:
        logger.exception(
            "%s: %s",
            FETCH_RECORDS_FAILED_LOG,
            ex,
        )

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
# Get Uploaded Files
# ==========================================================

def getUploadedFiles(
    businessId: str,
    courseId: str,
) -> list[UploadedDocumentDto]:
    """
    Return one entry per uploaded document for a specific
    business and course.
    """
    collectionName = ensureCollection(
        businessId,
    )

    try:
        courseFilter = _buildMetadataFilter(
            courseId=courseId,
        )

        records = _scrollRecords(
            collectionName,
            courseFilter,
        )

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

        logger.info(
            "%s: %s",
            FETCH_DOCUMENTS_LOG,
            len(documents),
        )

        return list(documents.values())

    except Exception as ex:
        logger.exception(
            "%s: %s",
            FETCH_DOCUMENTS_FAILED_LOG,
            ex,
        )

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
    businessId: str,
) -> bool:
    """
    Delete all chunks belonging to one document inside
    a specific business collection.
    """
    collectionName = ensureCollection(
        businessId,
    )

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
            collection_name=collectionName,
            scroll_filter=documentFilter,
            limit=1,
            with_payload=False,
        )

        if not existing:
            logger.info(
                "%s: %s",
                DOCUMENT_NOT_FOUND_LOG,
                documentId,
            )
            return False

        client.delete(
            collection_name=collectionName,
            points_selector=documentFilter,
        )

        logger.info(
            "%s: %s",
            DELETE_DOCUMENT_LOG,
            documentId,
        )

        return True

    except Exception as ex:
        logger.exception(
            "%s: %s",
            DELETE_DOCUMENT_FAILED_LOG,
            ex,
        )

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

def deleteAllDocuments(
    businessId: str,
) -> bool:
    """
    Remove every vector from one business's Knowledge Base.
    """
    collectionName = ensureCollection(
        businessId,
    )

    try:
        client.delete(
            collection_name=collectionName,
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