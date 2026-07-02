import os

from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# OPENROUTER
# ==========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

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

SCROLL_LIMIT = int(
    os.getenv(
        "SCROLL_LIMIT",
        5000
    )
)

# ==========================================================
# EMBEDDING
# ==========================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================================
# LLM
# ==========================================================

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "nvidia/nemotron-3-super-120b-a12b:free"
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
# FILES
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