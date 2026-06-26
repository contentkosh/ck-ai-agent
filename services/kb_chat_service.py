import os
from typing import Dict, List

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI

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

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ==========================================================
# LLM
# ==========================================================

llm = ChatOpenAI(

    model=LLM_MODEL,

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY"),

    temperature=0

)


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
    context: str,
    query: str
) -> str:
    """
    Build the prompt for the LLM.
    """

    return f"""
You are an AI Knowledge Base Assistant.

Answer ONLY using the information provided in the context.

Rules:

1. Use ONLY the context below.
2. Do NOT use your own knowledge.
3. If the answer cannot be found, respond exactly:

Answer not found in the Knowledge Base.

4. Keep the answer concise and factual.
5. Do not mention the context or the document.

--------------------------------------------------

Context:

{context}

--------------------------------------------------

Question:

{query}

--------------------------------------------------

Answer:
"""
# ==========================================================
# Ask Question
# ==========================================================

def ask_question(query: str) -> Dict:
    """
    Search the Knowledge Base and generate an answer.
    """

    try:

        logger.info(
            f"Received query: {query}"
        )

        # --------------------------------------------------
        # Generate Query Embedding
        # --------------------------------------------------

        query_embedding = embedding_model.encode(
            query
        ).tolist()

        logger.info(
            "Query embedding generated."
        )

        # --------------------------------------------------
        # Search Knowledge Base
        # --------------------------------------------------

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
            f"{len(results)} relevant chunk(s) retrieved."
        )

        # --------------------------------------------------
        # Build Context
        # --------------------------------------------------

        context = build_context(
            results
        )

        payload = results[0].payload

        logger.info(
            f"Top matching document: {payload.get('source')}"
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

        response = llm.invoke(
            prompt
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

    except Exception as e:

        logger.exception(
            "Chat Service Error."
        )

        raise DatabaseException(
            f"Unable to process user query. {str(e)}"
        )