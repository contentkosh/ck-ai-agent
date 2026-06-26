import os

from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# QDRANT
# ==========================================================

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    "localhost"
)

QDRANT_PORT = int(
    os.getenv(
        "QDRANT_PORT",
        6333
    )
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "knowledge_base"
)

# ==========================================================
# EMBEDDINGS
# ==========================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

EMBEDDING_DIMENSION = int(
    os.getenv(
        "EMBEDDING_DIMENSION",
        384
    )
)

# ==========================================================
# LLM
# ==========================================================

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "nvidia/nemotron-3-super-120b-a12b:free"
)

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        500
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        50
    )
)

# ==========================================================
# FILE STORAGE
# ==========================================================

UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "uploads"
)

MAX_FILE_SIZE = int(
    os.getenv(
        "MAX_FILE_SIZE",
        20971520
    )
)