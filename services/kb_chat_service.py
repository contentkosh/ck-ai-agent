import os
from typing import Dict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer

from common.custom_exceptions import DatabaseException
from common.logger import logger
from configuration.app_settings import (
    EMBEDDING_MODEL,
    LLM_MODEL,
    OPENROUTER_BASE_URL,
    SEARCH_LIMIT,
)
from configuration.context import KNOWLEDGE_BASE_QA_PROMPT
from repositories.kb_repository import search_chunks
from services.cache_service import (
    cache_answer,
    get_cached_answer,
)
from services.llmlingua_service import compress_context

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

# ==========================================================
# Embedding Model
# ==========================================================

_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Return the singleton embedding model."""
    global _embedding_model

    if _embedding_model is None:
        logger.info("Loading embedding model.")
        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

    return _embedding_model


# ==========================================================
# LLM
# ==========================================================

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    """Return the singleton LLM."""

    global _llm

    if _llm is None:
        _llm = ChatOpenAI(
            model=LLM_MODEL,
            base_url=OPENROUTER_BASE_URL,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0,
        )

    return _llm


# ==========================================================
# Build Context
# ==========================================================

def build_context(results: List) -> str:
    """
    Combine retrieved chunks into a single context string.
    """
    return "\n\n".join(
        result.payload.get(
            "text",
            ""
        )
        for result in results
    )


# ==========================================================
# Build Prompt
# ==========================================================

def build_prompt(
    *,
    context: str,
    query: str,
) -> str:
    """Build the LLM prompt."""
    return KNOWLEDGE_BASE_QA_PROMPT.format(
        context=context,
        query=query,
    )


# ==========================================================
# Ask Question
# ==========================================================

def ask_question(query: str) -> Dict:
    """
    Search the Knowledge Base and generate an answer.
    """
    try:
        logger.info("Received query: %s", query)

        # --------------------------------------------------
        # Generate Query Embedding
        # --------------------------------------------------

        query_embedding = (
            get_embedding_model()
            .encode(query)
            .tolist()
        )

        # --------------------------------------------------
        # Search Semantic Cache
        # --------------------------------------------------

        cached = get_cached_answer(query_embedding)

        if cached:
            logger.info("Returning cached answer.")
            return {
                "answer": cached.get("answer"),
                "source": "CACHE",
                "similarity_score": round(
                    cached.get("score"),
                    3,
                ),
            }

        # --------------------------------------------------
        # Search Knowledge Base
        # --------------------------------------------------

        results = search_chunks(
            query_embedding=query_embedding,
            limit=SEARCH_LIMIT,
        )

        if not results:
            logger.warning("No relevant chunks found.")
            return {
                "answer": "Answer not found in the Knowledge Base.",
                "document_id": None,
                "title": None,
                "document_type": None,
                "tag": None,
                "summary": None,
                "source": None,
                "page": None,
            }

        logger.info("Knowledge Base search returned %d results.", len(results))

        # --------------------------------------------------
        # Build Context
        # --------------------------------------------------

        context = build_context(results)

        compressed_context = compress_context(
            context=context,
            query=query,
        )

        payload = results[0].payload

        logger.info("Top matching source: %s",payload.get("source"))

        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        prompt = build_prompt(
            context=compressed_context,
            query=query,
        )

        response = get_llm().invoke(prompt)

        cache_answer(
            question=query,
            embedding=query_embedding,
            context=context,
            answer=response.content.strip(),
        )

        logger.info("LLM response generated successfully.")

        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return {
            "answer": response.content.strip(),
            "document_id": payload.get("document_id"),
            "title": payload.get("title"),
            "document_type": payload.get("document_type"),
            "tag": payload.get("tag"),
            "summary": payload.get("summary"),
            "source": payload.get("source"),
            "page": payload.get("page"),
        }

    except Exception as ex:
        logger.exception("Chat service failed: %s", ex)
        raise DatabaseException("Unable to process user query.") from ex