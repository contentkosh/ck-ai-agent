import numpy as np
import requests

from common.logger import logger
from configuration.config import (
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    OPENROUTER_API_KEY,
)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/embeddings"
_embedding_model = None


class OpenRouterEmbeddingClient:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = EMBEDDING_MODEL

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

    def encode(self, texts, batch_size=32, convert_to_numpy=True, **kwargs):
        single_input = isinstance(texts, str)
        texts = [texts] if single_input else list(texts)

        if not texts:
            return np.empty((0, EMBEDDING_DIMENSION), dtype=np.float32)

        embeddings = []

        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]

            logger.info(
                "OpenRouter embedding request started. Model=%s | Batch=%d",
                self.model,
                len(batch),
            )

            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": batch,
                    "encoding_format": "float",
                },
                timeout=120,
            )

            response.raise_for_status()
            data = response.json()["data"]
            data.sort(key=lambda item: item["index"])
            batch_embeddings = [item["embedding"] for item in data]

            if len(batch_embeddings) != len(batch):
                raise ValueError("Embedding response count does not match input count.")

            embeddings.extend(batch_embeddings)
            logger.info(
                "OpenRouter embedding request completed. Model=%s | Batch=%d",
                self.model,
                len(batch_embeddings),
            )

        result = np.asarray(embeddings, dtype=np.float32)

        if result.ndim != 2 or result.shape[1] != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Expected {EMBEDDING_DIMENSION}-dimensional embeddings, got shape {result.shape}."
            )

        return result[0] if single_input else result


def get_embedding_model() -> OpenRouterEmbeddingClient:
    global _embedding_model

    if _embedding_model is None:
        logger.info(
            "OpenRouter embedding client initialization started. Model=%s",
            EMBEDDING_MODEL,
        )
        _embedding_model = OpenRouterEmbeddingClient()
        logger.info(
            "OpenRouter embedding client initialized successfully. Model=%s",
            EMBEDDING_MODEL,
        )

    return _embedding_model
