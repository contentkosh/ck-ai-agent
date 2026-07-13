from unittest.mock import MagicMock
from unittest.mock import patch
from services.kb_chat_service import (
    build_context,
    build_prompt,
    ask_question,
)
# ==========================================================
# Build Context Tests
# ==========================================================

def test_build_context():

    chunk1 = MagicMock()
    chunk1.payload = {
        "text": "Artificial Intelligence"
    }
    chunk2 = MagicMock()
    chunk2.payload = {
        "text": "Machine Learning"
    }
    context = build_context(
        [chunk1, chunk2]
    )
    assert (
        "Artificial Intelligence"
        in context
    )
    assert (
        "Machine Learning"
        in context
    )

# ==========================================================
# Build Prompt Tests
# ==========================================================

def test_build_prompt():

    prompt = build_prompt(
        context="AI Context",
        query="What is AI?",
    )
    assert "AI Context" in prompt
    assert "What is AI?" in prompt

# ==========================================================
# Ask Question Tests
# ==========================================================

@patch(
    "services.kb_chat_service.search_chunks"
)
@patch(
    "services.kb_chat_service.get_embedding_model"
)
@patch(
    "services.kb_chat_service.get_llm"
)
def test_ask_question(
    mock_llm,
    mock_embedding,
    mock_search,
):

    embedding = MagicMock()
    embedding.encode.return_value.tolist.return_value = [
        0.1,
        0.2,
    ]
    mock_embedding.return_value = embedding
    chunk = MagicMock()
    chunk.payload = {

        "text": "Artificial Intelligence",
        "title": "AI Notes",
        "document_id": "123",
        "document_type": "Notes",
        "tag": "ai",
        "summary": "AI basics",
        "source": "ai.pdf",
        "page": 5,

    }
    mock_search.return_value = [
        chunk
    ]

    response = MagicMock()
    response.content = (
        "Artificial Intelligence is..."
    )
    mock_llm.return_value.invoke.return_value = (
        response
    )
    result = ask_question(
        "What is AI?"
    )
    assert (
        result["answer"]
        == "Artificial Intelligence is..."
    )
    assert (
        result["title"]
        == "AI Notes"
    )
    assert (
        result["tag"]
        == "ai"
    )