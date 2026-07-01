import os
from typing import Dict, List

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI

from services.cache_service import (
    get_cached_answer,
    cache_answer,
)

from configuration.app_settings import (
    EMBEDDING_MODEL,
    LLM_MODEL
)

from repositories.kb_repository import search_chunks

from common.logger import logger
from common.custom_exceptions import DatabaseException


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
            base_url="https://openrouter.ai/api/v1",
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
from configuration.context import CHAT_PROMPT


def build_prompt(
    *,
    context: str,
    query: str,
) -> str:
    """Build the LLM prompt."""

    return CHAT_PROMPT.format(
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

        logger.info(
            "Received query:%s",
        )

        # --------------------------------------------------
        # Generate Query Embedding
        # --------------------------------------------------
        query_embedding = (
            get_embedding_model()
            .encode(query)
            .tolist()
        )
        # --------------------------------------------------
        # Search Knowledge Base
        # --------------------------------------------------

        cached = get_cached_answer(
            query_embedding
        )

        if cached:

            logger.info(
                "Returning cached answer."
            )

            return {

                "answer": cached.get("answer"),

                "source": "CACHE",

                "similarity_score": round(
                    cached.get("score"),
                    3,
                ),

            }

        results = search_chunks(
            query_embedding=query_embedding,
            limit=5
        )

        if not results:

            logger.warning(
                "No relevant chunks found."
            )

            return {

                "answer": "Answer not found in the Knowledge Base.",

                "document_id": None,

                "title": None,

                "document_type": None,

                "tag": None,

                "summary": None,

                "source": None,

                "page": None

            }
        logger.info(
            "Retrieved %d chunk(s).",
            len(results),
        )

        # --------------------------------------------------
        # Build Context
        # --------------------------------------------------

        context = build_context(
            results
        )

        payload = results[0].payload

        logger.info(
            "Top matching source: %s",
            payload.get("source"),
        )
        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        prompt = build_prompt(
            context=context,
            query=query
        )

        logger.info(
            "Sending prompt to LLM."
        )

        response = get_llm().invoke(
            prompt
        )

        cache_answer(

            question=query,

            embedding=query_embedding,

            context=context,

            answer=response.content.strip(),

        )

        logger.info(
            "LLM response generated successfully."
        )

        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return {

            "answer": response.content.strip(),

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
            )

        }

    except Exception as ex:

        logger.exception(
            "Chat service failed: %s",
            ex,
        )
        
        raise DatabaseException(
            "Unable to process user query."
        ) from ex