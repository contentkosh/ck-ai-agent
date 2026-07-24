import os

from langchain_openai import ChatOpenAI

from configuration.config import (
    LLM_MODEL,
    OPENROUTER_API_KEY_ENV,
    OPENROUTER_BASE_URL,
)
_llm: ChatOpenAI | None = None

def get_llm() -> ChatOpenAI:
    """
    Return the singleton LLM instance shared across the
    application. Both metadata extraction and Q&A use this
    same client so the model is only ever configured once.
    """
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            api_key=os.getenv(OPENROUTER_API_KEY_ENV),
            base_url=OPENROUTER_BASE_URL,
            model=LLM_MODEL,
            temperature=0,
        )
    return _llm