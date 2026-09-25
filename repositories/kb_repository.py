from typing import Optional

from httpx import ConnectError
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
    MatchValue,
)

from common.collection_utils import get_kb_collection_name
from common.custom_exceptions import DatabaseException
from common.logger import logger
from configuration.config import (
    SCROLL_LIMIT,
    SEARCH_LIMIT,
    SEARCH_SCORE_THRESHOLD,
)
from configuration.constants import (
    CLEAR_KB_FAILED_LOG,
    CLEAR_KB_LOG,
    DELETE_DOCUMENT_FAILED_LOG,
    DELETE_DOCUMENT_LOG,
    DOCUMENT_NOT_FOUND_LOG,
    FETCH_DOCUMENTS_FAILED_LOG,
    FETCH_DOCUMENTS_LOG,
    FETCH_RECORDS_FAILED_LOG,
    FETCH_RECORDS_LOG,
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
    SEMANTIC_SEARCH_FAILED_LOG,
    SEMANTIC_SEARCH_LOG,
    VECTOR_INSERTION_FAILED_LOG,
    VECTOR_INSERTION_LOG,
)
from configuration.error_constants import (
    DATABASE_CLEAR_ERROR_MESSAGE,
    DATABASE_DELETE_ERROR_MESSAGE,
    DATABASE_FETCH_ERROR_MESSAGE,
    DATABASE_INSERT_ERROR_MESSAGE,
    DATABASE_SEARCH_ERROR_MESSAGE,
)
from database.collection_setup import create_collection_if_missing
from database.qdrant_client_manager import client
from dto.file_response_dto import UploadedDocumentDto
from dto.knowledge_base_record_dto import KnowledgeBaseRecordDto
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.qdrant_exception import (
    QdrantConnectionException,
    QdrantDeleteException,
    QdrantFetchException,
    QdrantInsertException,
    QdrantSearchException,
)


def _scrollRecords(
    collectionName: str,
    queryFilter: Optional[Filter] = None,
) -> list:
    allRecords: list = []
    nextOffset = None
    pageCount = 0

    logger.info(
        "Qdrant scroll started. Collection=%s",
        collectionName,
    )

    while True:
        records, nextOffset = client.scroll(
            collection_name=collectionName,
            scroll_filter=queryFilter,
            limit=SCROLL_LIMIT,
            offset=nextOffset,
            with_payload=True,
        )

        allRecords.extend(records)
        pageCount += 1

        if nextOffset is None:
            break

    logger.info(
        "Qdrant scroll completed. Collection=%s | records=%d | pages=%d",
        collectionName,
        len(allRecords),
        pageCount,
    )

    return allRecords


def ensureCollection(
    businessId: str,
) -> str:
    collectionName = get_kb_collection_name(
        businessId,
    )

    logger.info(
        "Ensuring Knowledge Base collection exists: %s",
        collectionName,
    )

    create_collection_if_missing(
        collectionName,
    )

    logger.info(
        "Knowledge Base collection ready: %s",
        collectionName,
    )

    return collectionName


def buildUploadedDocument(
    payload: dict,
) -> UploadedDocumentDto:
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


def isQdrantConnectionError(
    exception: Exception,
) -> bool:
    return isinstance(
        exception,
        ResponseHandlingException,
    ) and isinstance(
        getattr(
            exception,
            "source",
            None,
        ),
        ConnectError,
    )


def saveChunks(
    points: list,
    businessId: str,
) -> None:
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Qdrant vector insertion started. Collection=%s | points=%d",
            collectionName,
            len(points),
        )

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
    courseIds: Optional[list[str]] = None,
    tag: Optional[str] = None,
) -> Optional[Filter]:
    mustConditions = []

    if courseIds:
        mustConditions.append(
            FieldCondition(
                key=METADATA_COURSE_ID,
                match=MatchAny(
                    any=courseIds,
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
        Filter(
            must=mustConditions,
        )
        if mustConditions
        else None
    )


def searchChunks(
    queryEmbedding: list[float],
    businessId: str,
    courseIds: list[str],
    limit: int = SEARCH_LIMIT,
    scoreThreshold: Optional[float] = SEARCH_SCORE_THRESHOLD,
):
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Qdrant semantic search started. Collection=%s | courses=%s | limit=%d | score_threshold=%s",
            collectionName,
            courseIds,
            limit,
            scoreThreshold,
        )

        queryFilter = _buildMetadataFilter(
            courseIds=courseIds,
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

        if searchResult.points:
            logger.info(
                "Qdrant semantic search scores: %s",
                [round(point.score, 4) for point in searchResult.points],
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


def getAllRecords(
    businessId: str,
    courseIds: Optional[list[str]] = None,
    tag: Optional[str] = None,
) -> list[KnowledgeBaseRecordDto]:
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Fetching Knowledge Base records. Collection=%s | courses=%s | tag=%s",
            collectionName,
            courseIds,
            tag,
        )

        queryFilter = _buildMetadataFilter(
            courseIds=courseIds,
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


def getUploadedFiles(
    businessId: str,
    courseIds: list[str],
) -> list[UploadedDocumentDto]:
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Fetching uploaded documents. Collection=%s | courses=%s",
            collectionName,
            courseIds,
        )

        courseFilter = _buildMetadataFilter(
            courseIds=courseIds,
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


def getCourseIdsForDocument(
    *,
    documentId: str,
    businessId: str,
) -> list[str] | None:
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Retrieving course IDs for document. Collection=%s | document_id=%s",
            collectionName,
            documentId,
        )

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
            with_payload=True,
        )

        if not existing:
            logger.info(
                "No Knowledge Base record found for document: %s",
                documentId,
            )
            return None

        payload = existing[0].payload or {}
        courseIds = payload.get(
            METADATA_COURSE_ID,
        )

        if isinstance(courseIds, list):
            logger.info(
                "Course IDs retrieved for document %s: %s",
                documentId,
                courseIds,
            )
            return courseIds

        if courseIds is not None:
            logger.info(
                "Single course ID retrieved for document %s: %s",
                documentId,
                courseIds,
            )
            return [courseIds]

        logger.info(
            "Document %s has no course IDs.",
            documentId,
        )
        return None

    except Exception as ex:
        logger.exception(
            "Failed to retrieve course IDs for document %s: %s",
            documentId,
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


def deleteDocument(
    documentId: str,
    businessId: str,
) -> bool:
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Document deletion started. Collection=%s | document_id=%s",
            collectionName,
            documentId,
        )

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


def deleteAllDocuments(
    businessId: str,
) -> bool:
    collectionName = ensureCollection(
        businessId,
    )

    try:
        logger.info(
            "Knowledge Base deletion started. Collection=%s",
            collectionName,
        )

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
