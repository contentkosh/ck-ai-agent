from typing import Dict, List
from dotenv import load_dotenv
from common.llm_client import get_llm
from common.embedding_client import get_embedding_model
from configuration.config import SEARCH_LIMIT
from configuration.constants import DEFAULT_SCORE_THRESHOLD
from repositories.kb_repository import search_chunks
from common.logger import logger
from common.custom_exceptions import DatabaseException

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

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
from configuration.context import KNOWLEDGE_BASE_QA_PROMPT
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
        logger.info("Received query: %s",query)

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
                "page": None
            }
        logger.info("Retrieved %d chunk(s).",len(results),)

        # --------------------------------------------------
        # Build Context
        # --------------------------------------------------

        context = build_context(
            results
        )
        payload = results[0].payload
        logger.info("Top matching source: %s",payload.get("source"),)
        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        prompt = build_prompt(
            context=context,
            query=query
        )
        logger.info("Sending prompt to LLM.")
        response = get_llm().invoke(
            prompt
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
            "page": payload.get("page")
        }

    except Exception as ex:
        logger.exception("Chat service failed: %s",ex,)
        raise DatabaseException(
            "Unable to process user query."
        ) from ex