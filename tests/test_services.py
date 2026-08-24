import pytest
from unittest.mock import MagicMock, patch

from dto.response_dto import QueryResponse
from exceptions.contentkosh_exception import ContentKoshException
from exceptions.knowledge_base_exception import KnowledgeBaseException
from exceptions.llm_exception import LLMResponseException

from services.kb_query_service import (
    ask_question,
    build_context,
    build_prompt,
)
from services.kb_service import (
    get_knowledge_base_records,
)

from configuration.error_constants import (
    ANSWER_NOT_FOUND_MESSAGE,
)

from exceptions.qdrant_exception import (
    QdrantConnectionException,
)

BUSINESS_ID = "test-business"
COURSE_ID = "test-course"

QUERY = "What is Artificial Intelligence?"

ANSWER = "Artificial Intelligence is the simulation of human intelligence."

DOCUMENT_PAYLOAD = {
    "document_id": "doc-123",
    "title": "AI Notes",
    "document_type": "Notes",
    "tag": "artificial_intelligence",
    "summary": "Introduction to AI.",
    "source": "ai_notes.pdf",
    "page": 10,
    "text": "Artificial Intelligence is the simulation of human intelligence.",
}


# ==========================================================
# Helpers
# ==========================================================

def make_search_result(
    payload=None,
    score=0.95,
):
    result = MagicMock()

    result.payload = (
        payload
        if payload is not None
        else DOCUMENT_PAYLOAD.copy()
    )

    result.score = score

    return result


def make_llm_response(
    content=ANSWER,
):
    response = MagicMock()
    response.content = content
    return response


# ==========================================================
# Build Context
# ==========================================================

def test_build_context():
    result_one = make_search_result(
        payload={
            "text": "Artificial Intelligence is a field of computer science."
        }
    )

    result_two = make_search_result(
        payload={
            "text": "Machine learning is a subset of AI."
        }
    )

    context = build_context(
        [
            result_one,
            result_two,
        ]
    )

    assert context == (
        "Artificial Intelligence is a field of computer science.\n"
        "Machine learning is a subset of AI."
    )


def test_build_context_empty():
    assert build_context([]) == ""


def test_build_context_missing_text():
    result = make_search_result(
        payload={
            "title": "AI Notes",
        }
    )

    assert build_context([result]) == ""


# ==========================================================
# Build Prompt
# ==========================================================

def test_build_prompt():
    prompt = build_prompt(
        context="AI is artificial intelligence.",
        query="What is AI?",
    )

    assert isinstance(prompt, str)

    assert "AI is artificial intelligence." in prompt
    assert "What is AI?" in prompt


# ==========================================================
# Knowledge Base Service
# ==========================================================

@patch(
    "services.kb_service.getAllRecords"
)
def test_get_knowledge_base_records(
    mock_get_all_records,
):
    records = [
        {
            "document_id": "doc-1",
            "title": "AI Notes",
        }
    ]

    mock_get_all_records.return_value = records

    result = get_knowledge_base_records(
        business_id=BUSINESS_ID,
        course_id=COURSE_ID,
        tag="ai",
    )

    assert result == records

    mock_get_all_records.assert_called_once_with(
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
        tag="ai",
    )


@patch(
    "services.kb_service.getAllRecords"
)
def test_get_knowledge_base_records_without_course(
    mock_get_all_records,
):
    mock_get_all_records.return_value = []

    result = get_knowledge_base_records(
        business_id=BUSINESS_ID,
        course_id=None,
        tag=None,
    )

    assert result == []

    mock_get_all_records.assert_called_once_with(
        businessId=BUSINESS_ID,
        courseId=None,
        tag=None,
    )


@patch(
    "services.kb_service.getAllRecords"
)
def test_get_knowledge_base_records_failure(
    mock_get_all_records,
):
    mock_get_all_records.side_effect = (
        ContentKoshException(
            "Database failure"
        )
    )

    with pytest.raises(KnowledgeBaseException):
        get_knowledge_base_records(
            business_id=BUSINESS_ID,
            course_id=COURSE_ID,
            tag=None,
        )


# ==========================================================
# Ask Question - Cache Hit
# ==========================================================

@patch(
    "services.kb_query_service.cache_answer"
)
@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_cache_hit(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
    mock_cache_answer,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = {
        "answer": ANSWER,
        "document_id": "doc-123",
        "title": "AI Notes",
        "document_type": "Notes",
        "tag": "artificial_intelligence",
        "summary": "Introduction to AI.",
        "source": "ai_notes.pdf",
        "page": 10,
    }

    result = ask_question(
        QUERY,
        BUSINESS_ID,
        COURSE_ID,
    )

    assert isinstance(
        result,
        QueryResponse,
    )

    assert result.answer == ANSWER
    assert result.document_id == "doc-123"
    assert result.title == "AI Notes"
    assert result.source == "ai_notes.pdf"
    assert result.page == 10

    mock_get_cached_answer.assert_called_once_with(
        query_embedding=[
            0.1,
            0.2,
            0.3,
        ],
        business_id=BUSINESS_ID,
        course_id=COURSE_ID,
    )

    # Cache hit must stop the pipeline.
    mock_search_chunks.assert_not_called()
    mock_cache_answer.assert_not_called()


# ==========================================================
# Ask Question - No Relevant Chunks
# ==========================================================

@patch(
    "services.kb_query_service.cache_answer"
)
@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_no_relevant_chunks(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
    mock_cache_answer,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = None
    mock_search_chunks.return_value = []

    result = ask_question(
        QUERY,
        BUSINESS_ID,
        COURSE_ID,
    )

    assert isinstance(
        result,
        QueryResponse,
    )

    assert result.answer is not None
    assert result.document_id is None
    assert result.title is None
    assert result.source is None
    assert result.page is None

    mock_search_chunks.assert_called_once_with(
        queryEmbedding=[
            0.1,
            0.2,
            0.3,
        ],
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
        limit=5,
    )

    mock_cache_answer.assert_not_called()


# ==========================================================
# Ask Question - Successful LLM Flow
# ==========================================================

@patch(
    "services.kb_query_service.cache_answer"
)
@patch(
    "services.kb_query_service.get_llm"
)
@patch(
    "services.kb_query_service.compress_context"
)
@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_success(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
    mock_compress_context,
    mock_get_llm,
    mock_cache_answer,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
        0.3,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = None

    search_result = make_search_result()

    mock_search_chunks.return_value = [
        search_result
    ]

    mock_compress_context.return_value = (
        "Compressed AI context."
    )

    llm = MagicMock()

    llm.invoke.return_value = (
        make_llm_response()
    )

    mock_get_llm.return_value = llm

    result = ask_question(
        QUERY,
        BUSINESS_ID,
        COURSE_ID,
    )

    assert isinstance(
        result,
        QueryResponse,
    )

    assert result.answer == ANSWER
    assert result.document_id == "doc-123"
    assert result.title == "AI Notes"
    assert result.source == "ai_notes.pdf"
    assert result.page == 10

    mock_search_chunks.assert_called_once_with(
        queryEmbedding=[
            0.1,
            0.2,
            0.3,
        ],
        businessId=BUSINESS_ID,
        courseId=COURSE_ID,
        limit=5,
    )

    mock_compress_context.assert_called_once()

    llm.invoke.assert_called_once()

    mock_cache_answer.assert_called_once_with(
        question=QUERY,
        embedding=[
            0.1,
            0.2,
            0.3,
        ],
        context=(
            "Artificial Intelligence is the simulation "
            "of human intelligence."
        ),
        answer=ANSWER,
        documentPayload=DOCUMENT_PAYLOAD,
        business_id=BUSINESS_ID,
        course_id=COURSE_ID,
    )


# ==========================================================
# Ask Question - Qdrant Connection Failure
# ==========================================================

@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_qdrant_connection_failure(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = None

    mock_search_chunks.side_effect = (
        ContentKoshException(
            "Qdrant connection failed",
            cause=QdrantConnectionException(),
        )
    )

    with pytest.raises(
        KnowledgeBaseException
    ):
        ask_question(
            QUERY,
            BUSINESS_ID,
            COURSE_ID,
        )


# ==========================================================
# Ask Question - Knowledge Base Failure
# ==========================================================

@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_knowledge_base_failure(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = None

    mock_search_chunks.side_effect = (
        ContentKoshException(
            "Knowledge base failure",
        )
    )

    with pytest.raises(
        KnowledgeBaseException
    ):
        ask_question(
            QUERY,
            BUSINESS_ID,
            COURSE_ID,
        )


# ==========================================================
# Ask Question - LLM Failure
# ==========================================================

@patch(
    "services.kb_query_service.get_llm"
)
@patch(
    "services.kb_query_service.compress_context"
)
@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_llm_failure(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
    mock_compress_context,
    mock_get_llm,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = None

    mock_search_chunks.return_value = [
        make_search_result()
    ]

    mock_compress_context.return_value = (
        "Compressed context."
    )

    llm = MagicMock()

    llm.invoke.side_effect = Exception(
        "LLM failure"
    )

    mock_get_llm.return_value = llm

    with pytest.raises(
        LLMResponseException
    ):
        ask_question(
            QUERY,
            BUSINESS_ID,
            COURSE_ID,
        )


# ==========================================================
# Ask Question - LLM Says Answer Not Found
# ==========================================================

@patch(
    "services.kb_query_service.cache_answer"
)
@patch(
    "services.kb_query_service.get_llm"
)
@patch(
    "services.kb_query_service.compress_context"
)
@patch(
    "services.kb_query_service.searchChunks"
)
@patch(
    "services.kb_query_service.get_cached_answer"
)
@patch(
    "services.kb_query_service.get_embedding_model"
)
def test_ask_question_answer_not_found(
    mock_get_embedding_model,
    mock_get_cached_answer,
    mock_search_chunks,
    mock_compress_context,
    mock_get_llm,
    mock_cache_answer,
):
    embedding_model = MagicMock()

    embedding_model.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]

    mock_get_embedding_model.return_value = (
        embedding_model
    )

    mock_get_cached_answer.return_value = None

    mock_search_chunks.return_value = [
        make_search_result()
    ]

    mock_compress_context.return_value = (
        "Compressed context."
    )

    llm = MagicMock()

    llm.invoke.return_value = make_llm_response(
        content=ANSWER_NOT_FOUND_MESSAGE,
    )

    mock_get_llm.return_value = llm

    result = ask_question(
        QUERY,
        BUSINESS_ID,
        COURSE_ID,
    )

    assert isinstance(
        result,
        QueryResponse,
    )

    assert result.document_id is None
    assert result.title is None
    assert result.source is None
    assert result.page is None

    mock_cache_answer.assert_not_called()