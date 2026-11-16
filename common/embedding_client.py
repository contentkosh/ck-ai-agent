import threading

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from configuration.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION
from common.logger import logger

_embedding_model = None
_embedding_lock = threading.Lock()


class LocalEmbeddingClient:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(
            "Local embedding model initialization started. Model=%s | Device=%s",
            EMBEDDING_MODEL,
            self.device,
        )
        try:
            self.model = SentenceTransformer(EMBEDDING_MODEL, device=self.device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            if self.dimension != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Expected {EMBEDDING_DIMENSION}-dimensional embeddings, got {self.dimension}."
                )
            logger.info(
                "Local embedding model initialized successfully. Model=%s | Device=%s | Dimensions=%d",
                EMBEDDING_MODEL,
                self.device,
                self.dimension,
            )
        except Exception:
            logger.exception(
                "Local embedding model initialization failed. Model=%s", EMBEDDING_MODEL
            )
            raise

    def encode(self, texts, batch_size=32, convert_to_numpy=True, **kwargs):
        single_input = isinstance(texts, str)
        texts = [texts] if single_input else list(texts)

        if not texts:
            if convert_to_numpy:
                return np.empty((0, self.dimension), dtype=np.float32)
            return torch.empty((0, self.dimension), device=self.device)

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        logger.info(
            "Local embedding generation started. Model=%s | Inputs=%d | Batch size=%d | Device=%s",
            EMBEDDING_MODEL,
            len(texts),
            batch_size,
            self.device,
        )

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=convert_to_numpy,
                **kwargs,
            )

            if convert_to_numpy:
                embeddings = np.asarray(embeddings, dtype=np.float32)
                if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
                    raise ValueError(
                        f"Expected embedding shape (N, {self.dimension}), got {embeddings.shape}."
                    )
            else:
                if isinstance(embeddings, list):
                    if not embeddings:
                        raise ValueError(
                            "Embedding generation returned an empty result."
                        )
                    embeddings = torch.stack(embeddings)
                if embeddings.ndim != 2 or embeddings.shape[1] != self.dimension:
                    raise ValueError(
                        f"Expected embedding shape (N, {self.dimension}), got {tuple(embeddings.shape)}."
                    )

            logger.info(
                "Local embedding generation completed. Model=%s | Inputs=%d | Dimensions=%d",
                EMBEDDING_MODEL,
                len(texts),
                self.dimension,
            )
            return embeddings[0] if single_input else embeddings

        except Exception:
            logger.exception(
                "Local embedding generation failed. Model=%s | Inputs=%d",
                EMBEDDING_MODEL,
                len(texts),
            )
            raise


def get_embedding_model() -> LocalEmbeddingClient:
    global _embedding_model

    if _embedding_model is None:
        with _embedding_lock:
            if _embedding_model is None:
                _embedding_model = LocalEmbeddingClient()

    return _embedding_model
