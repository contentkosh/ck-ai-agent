from sentence_transformers import SentenceTransformer

from common.logger import logger
from configuration.config import EMBEDDING_MODEL

_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Return the singleton embedding model shared across the application.
    """
    global _embedding_model

    if _embedding_model is not None:
        return _embedding_model

    logger.info(
        "Embedding model initialization started. Model=%s",
        EMBEDDING_MODEL,
    )

    try:
        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
        )

        logger.info(
            "Embedding model initialized successfully. Model=%s",
            EMBEDDING_MODEL,
        )

        return _embedding_model

    except Exception:
        logger.exception(
            "Embedding model initialization failed. Model=%s",
            EMBEDDING_MODEL,
        )
        raise
