import pytest
from unittest.mock import MagicMock, patch

from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)

from common.custom_exceptions import DatabaseException
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.qdrant_exception import (
    QdrantConnectionException,
    QdrantDeleteException,
    QdrantFetchException,
    QdrantInsertException,
    QdrantSearchException,
)

from repositories.kb_repository import (
    _buildMetadataFilter,
    _scrollRecords,
    ensureCollection,
    buildUploadedDocument,
    buildKnowledgeBaseRecord,
    saveChunks,
    searchChunks,
    getAllRecords,
    getUploadedFiles,
    deleteDocument,
    deleteAllDocuments,
)


BUSINESS_ID = "test-business"
OTHER_BUSINESS_ID = "other-business"

COURSE_ID = "test-course"
OTHER_COURSE_ID = "other-course"

DOCUMENT_ID = "test-document"
MISSING_DOCUMENT_ID = "missing-document"


# ==========================================================
# Test Helpers
# ==========================================================

def make_point(
    payload=None,
    point_id="point-1",
):
    point = MagicMock()
    point.id = point_id
    point.payload = payload or {}
    return point


def make_uploaded_payload(
    document_id=DOCUMENT_ID,
):
    return {
        "document_id": document_id,
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "artificial_intelligence",
        "summary": "Introduction to AI.",
        "source": "ai_notes.pdf",
    }


def make_record_payload(
    document_id=DOCUMENT_ID,
):
    return {
        "document_id": document_id,
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "artificial_intelligence",
        "summary": "Introduction to AI.",
        "source": "ai_notes.pdf",
        "page": 10,
        "text": "Artificial Intelligence is...",
    }


# ==========================================================
# Metadata Filter Tests
# ==========================================================

def test_build_metadata_filter_course():
    result = _buildMetadataFilter(
        courseId=COURSE_ID,
    )

    assert isinstance(result, Filter)
    assert len(result.must) == 1

    condition = result.must[0]

    assert isinstance(condition, FieldCondition)
    assert condition.key == "course_id"
    assert condition.match == MatchValue(
        value=COURSE_ID,
    )


def test_build_metadata_filter_course_and_tag():
    result = _buildMetadataFilter(
        courseId=COURSE_ID,
        tag="ai",
    )

    assert isinstance(result, Filter)
    assert len(result.must) == 2

    keys = {
        condition.key
        for condition in result.must
    }

    assert keys == {
        "course_id",
        "tag",
    }


def test_build_metadata_filter_empty():
    result = _buildMetadataFilter()

    assert result is None


def test_build_metadata_filter_tag_only():
    result = _buildMetadataFilter(
        tag="ai",
    )

    assert isinstance(result, Filter)
    assert len(result.must) == 1

    assert result.must[0].key == "tag"


# ==========================================================
# Collection Tests
# ==========================================================

@patch(
    "repositories.kb_repository.create_collection_if_missing"
)
@patch(
    "repositories.kb_repository.get_kb_collection_name"
)
def test_ensure_collection(
    mock_get_collection_name,
    mock_create_collection,
):
    mock_get_collection_name.return_value = (
        "kb_test_business"
    )

    result = ensureCollection(
        BUSINESS_ID,
    )

    assert result == "kb_test_business"

    mock_get_collection_name.assert_called_once_with(
        BUSINESS_ID,
    )

    mock_create_collection.assert_called_once_with(
        "kb_test_business",
    )


# ==========================================================
# Payload Builder Tests
# ==========================================================

def test_build_uploaded_document():
    payload = make_uploaded_payload()

    result = buildUploadedDocument(
        payload,
    )

    assert result.document_id == DOCUMENT_ID
    assert result.title == "AI Notes"
    assert result.document_type == "Notes"
    assert result.tag == "artificial_intelligence"
    assert result.summary == "Introduction to AI."
    assert result.source == "ai_notes.pdf"


def test_build_knowledge_base_record():
    payload = make_record_payload()

    result = buildKnowledgeBaseRecord(
        payload,
    )

    assert result.document_id == DOCUMENT_ID
    assert result.title == "AI Notes"
    assert result.document_type == "Notes"
    assert result.tag == "artificial_intelligence"
    assert result.summary == "Introduction to AI."
    assert result.source == "ai_notes.pdf"
    assert result.page == 10
    assert result.text == "Artificial Intelligence is..."


# ==========================================================
# Pagination Tests
# ==========================================================

@patch("repositories.kb_repository.client")
def test_scroll_records_single_page(
    mock_client,
):
    first_page = [
        make_point(point_id="1"),
        make_point(point_id="2"),
    ]

    mock_client.scroll.return_value = (
        first_page,
        None,
    )

    result = _scrollRecords(
        "kb_test",
    )

    assert len(result) == 2
    assert result == first_page

    mock_client.scroll.assert_called_once()


@patch("repositories.kb_repository.client")
def test_scroll_records_multiple_pages(
    mock_client,
):
    first_page = [
        make_point(point_id="1"),
    ]

    second_page = [
        make_point(point_id="2"),
    ]

    mock_client.scroll.side_effect = [
        (first_page, "offset-2"),
        (second_page, None),
    ]

    result = _scrollRecords(
        "kb_test",
    )

    assert result == [
        first_page[0],
        second_page[0],
    ]

    assert mock_client.scroll.call_count == 2

    first_call = mock_client.scroll.call_args_list[0]
    second_call = mock_client.scroll.call_args_list[1]

    assert first_call.kwargs["offset"] is None
    assert second_call.kwargs["offset"] == "offset-2"


# ==========================================================
# Save Chunks
# ==========================================================

@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_save_chunks_success(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    points = [
        make_point(point_id="1"),
        make_point(point_id="2"),
    ]

    saveChunks(
        points,
        BUSINESS_ID,
    )

    mock_ensure_collection.assert_called_once_with(
        BUSINESS_ID,
    )

    mock_client.upsert.assert_called_once_with(
        collection_name="kb_test_business",
        points=points,
    )


@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_save_chunks_failure(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_client.upsert.side_effect = Exception(
        "Qdrant failure"
    )

    with pytest.raises(ContentKoshException):
        saveChunks(
            [],
            BUSINESS_ID,
        )


# ==========================================================
# Semantic Search
# ==========================================================

@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_search_chunks_success(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    search_points = [
        make_point(
            payload=make_record_payload(),
        )
    ]

    mock_result = MagicMock()
    mock_result.points = search_points

    mock_client.query_points.return_value = (
        mock_result
    )

    result = searchChunks(
        queryEmbedding=[0.1, 0.2, 0.3],
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
    )

    assert result == search_points

    mock_ensure_collection.assert_called_once_with(
        BUSINESS_ID,
    )

    mock_client.query_points.assert_called_once()

    call_kwargs = (
        mock_client.query_points.call_args.kwargs
    )

    assert call_kwargs["collection_name"] == (
        "kb_test_business"
    )

    assert call_kwargs["query"] == [
        0.1,
        0.2,
        0.3,
    ]

    query_filter = call_kwargs["query_filter"]

    assert query_filter.must[0].key == "course_id"
    assert (
        query_filter.must[0].match.value
        == COURSE_ID
    )


@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_search_chunks_respects_limit_and_threshold(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_result = MagicMock()
    mock_result.points = []

    mock_client.query_points.return_value = (
        mock_result
    )

    searchChunks(
        queryEmbedding=[0.1, 0.2],
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
        limit=10,
        scoreThreshold=0.75,
    )

    call_kwargs = (
        mock_client.query_points.call_args.kwargs
    )

    assert call_kwargs["limit"] == 10
    assert call_kwargs["score_threshold"] == 0.75


@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_search_chunks_failure(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_client.query_points.side_effect = Exception(
        "Qdrant search failed"
    )

    with pytest.raises(ContentKoshException):
        searchChunks(
            queryEmbedding=[0.1, 0.2],
            businessId=BUSINESS_ID,
            courseId=COURSE_ID,
        )


# ==========================================================
# Get All Records
# ==========================================================

@patch("repositories.kb_repository._scrollRecords")
@patch("repositories.kb_repository.ensureCollection")
def test_get_all_records(
    mock_ensure_collection,
    mock_scroll_records,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    point = make_point(
        payload=make_record_payload(),
    )

    mock_scroll_records.return_value = [
        point,
    ]

    result = getAllRecords(
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
    )

    assert len(result) == 1
    assert result[0].document_id == DOCUMENT_ID

    mock_ensure_collection.assert_called_once_with(
        BUSINESS_ID,
    )

    mock_scroll_records.assert_called_once()

    call_args = (
        mock_scroll_records.call_args
    )

    assert call_args.args[0] == (
        "kb_test_business"
    )

    query_filter = call_args.args[1]

    assert query_filter.must[0].key == "course_id"
    assert (
        query_filter.must[0].match.value
        == COURSE_ID
    )


@patch("repositories.kb_repository._scrollRecords")
@patch("repositories.kb_repository.ensureCollection")
def test_get_all_records_with_tag(
    mock_ensure_collection,
    mock_scroll_records,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_scroll_records.return_value = []

    getAllRecords(
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
        tag="ai",
    )

    query_filter = (
        mock_scroll_records.call_args.args[1]
    )

    keys = {
        condition.key
        for condition in query_filter.must
    }

    assert keys == {
        "course_id",
        "tag",
    }


@patch("repositories.kb_repository._scrollRecords")
@patch("repositories.kb_repository.ensureCollection")
def test_get_all_records_failure(
    mock_ensure_collection,
    mock_scroll_records,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_scroll_records.side_effect = Exception(
        "Qdrant fetch failed"
    )

    with pytest.raises(ContentKoshException):
        getAllRecords(
            businessId=BUSINESS_ID,
            courseId=COURSE_ID,
        )


# ==========================================================
# Get Uploaded Files
# ==========================================================

@patch("repositories.kb_repository._scrollRecords")
@patch("repositories.kb_repository.ensureCollection")
def test_get_uploaded_files(
    mock_ensure_collection,
    mock_scroll_records,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    first_document = make_point(
        point_id="1",
        payload=make_uploaded_payload(
            document_id="doc-1",
        ),
    )

    second_chunk_same_document = make_point(
        point_id="2",
        payload=make_uploaded_payload(
            document_id="doc-1",
        ),
    )

    second_document = make_point(
        point_id="3",
        payload=make_uploaded_payload(
            document_id="doc-2",
        ),
    )

    mock_scroll_records.return_value = [
        first_document,
        second_chunk_same_document,
        second_document,
    ]

    result = getUploadedFiles(
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
    )

    assert len(result) == 2

    document_ids = {
        document.document_id
        for document in result
    }

    assert document_ids == {
        "doc-1",
        "doc-2",
    }


@patch("repositories.kb_repository._scrollRecords")
@patch("repositories.kb_repository.ensureCollection")
def test_get_uploaded_files_ignores_missing_document_id(
    mock_ensure_collection,
    mock_scroll_records,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    valid_point = make_point(
        payload=make_uploaded_payload(),
    )

    invalid_point = make_point(
        payload={
            "title": "No Document ID",
        },
    )

    mock_scroll_records.return_value = [
        valid_point,
        invalid_point,
    ]

    result = getUploadedFiles(
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
    )

    assert len(result) == 1
    assert result[0].document_id == DOCUMENT_ID


@patch("repositories.kb_repository._scrollRecords")
@patch("repositories.kb_repository.ensureCollection")
def test_get_uploaded_files_failure(
    mock_ensure_collection,
    mock_scroll_records,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_scroll_records.side_effect = Exception(
        "Qdrant fetch failed"
    )

    with pytest.raises(ContentKoshException):
        getUploadedFiles(
            businessId=BUSINESS_ID,
            courseId=COURSE_ID,
        )


# ==========================================================
# Delete One Document
# ==========================================================

@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_delete_document_success(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    existing_point = make_point()

    mock_client.scroll.return_value = (
        [existing_point],
        None,
    )

    result = deleteDocument(
        documentId=DOCUMENT_ID,
        businessId=BUSINESS_ID,
    )

    assert result is True

    mock_client.scroll.assert_called_once()

    scroll_kwargs = (
        mock_client.scroll.call_args.kwargs
    )

    assert scroll_kwargs["collection_name"] == (
        "kb_test_business"
    )

    document_filter = (
        scroll_kwargs["scroll_filter"]
    )

    assert (
        document_filter.must[0].key
        == "document_id"
    )

    assert (
        document_filter.must[0].match.value
        == DOCUMENT_ID
    )

    mock_client.delete.assert_called_once()


@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_delete_document_not_found(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_client.scroll.return_value = (
        [],
        None,
    )

    result = deleteDocument(
        documentId=MISSING_DOCUMENT_ID,
        businessId=BUSINESS_ID,
    )

    assert result is False

    mock_client.delete.assert_not_called()


@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_delete_document_failure(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_client.scroll.side_effect = Exception(
        "Qdrant delete failed"
    )

    with pytest.raises(ContentKoshException):
        deleteDocument(
            documentId=DOCUMENT_ID,
            businessId=BUSINESS_ID,
        )


# ==========================================================
# Delete Entire Knowledge Base
# ==========================================================

@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_delete_all_documents(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    result = deleteAllDocuments(
        BUSINESS_ID,
    )

    assert result is True

    mock_ensure_collection.assert_called_once_with(
        BUSINESS_ID,
    )

    mock_client.delete.assert_called_once()

    call_kwargs = (
        mock_client.delete.call_args.kwargs
    )

    assert call_kwargs["collection_name"] == (
        "kb_test_business"
    )

    assert isinstance(
        call_kwargs["points_selector"],
        Filter,
    )


@patch("repositories.kb_repository.client")
@patch("repositories.kb_repository.ensureCollection")
def test_delete_all_documents_failure(
    mock_ensure_collection,
    mock_client,
):
    mock_ensure_collection.return_value = (
        "kb_test_business"
    )

    mock_client.delete.side_effect = Exception(
        "Qdrant clear failed"
    )

    with pytest.raises(ContentKoshException):
        deleteAllDocuments(
            BUSINESS_ID,
        )