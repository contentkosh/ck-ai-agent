from sentence_transformers import SentenceTransformer
from common.logger import logger
from configuration.config import EMBEDDING_MODEL

_embedding_model: SentenceTransformer | None = None

def get_embedding_model() -> SentenceTransformer:
    """
    Return the singleton embedding model shared across the
    application. Loading a sentence-transformer model is
    expensive, so ingestion and chat must not each keep
    their own copy in memory.
    """
    global _embedding_model

    if _embedding_model is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    return _embedding_model