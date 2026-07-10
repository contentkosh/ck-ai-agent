import os
from dotenv import load_dotenv

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

# ==========================================================
# API SERVER
# ==========================================================

API_HOST = os.getenv(
    "API_HOST",
    "0.0.0.0",
)

API_PORT = int(
    os.getenv(
        "API_PORT",
        8000,
    )
)

API_RELOAD = os.getenv(
    "API_RELOAD",
    "True",
).lower() == "true"

# ==========================================================
# QDRANT
# ==========================================================

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    "localhost",
)

QDRANT_PORT = int(
    os.getenv(
        "QDRANT_PORT",
        6333,
    )
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "knowledge_base",
)

SCROLL_LIMIT = int(
    os.getenv(
        "SCROLL_LIMIT",
        5000,
    )
)

# ==========================================================
# SEARCH
# ==========================================================

SEARCH_LIMIT = int(
    os.getenv(
        "SEARCH_LIMIT",
        5,
    )
)

# ==========================================================
# EMBEDDINGS
# ==========================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

EMBEDDING_DIMENSION = int(
    os.getenv(
        "EMBEDDING_DIMENSION",
        384,
    )
)

# ==========================================================
# QUERY VALIDATION
# ==========================================================

MAX_QUERY_LENGTH = int(
    os.getenv(
        "MAX_QUERY_LENGTH",
        1000,
    )
)

# ==========================================================
# FILE STORAGE
# ==========================================================

UPLOAD_FOLDER = ...

# ==========================================================
# LLM
# ==========================================================

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "nvidia/nemotron-3-super-120b-a12b:free",
)

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
)

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        500,
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        50,
    )
)

# ==========================================================
# FILE STORAGE
# ==========================================================

UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "uploads",
)

DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024

MAX_FILE_SIZE = int(
    os.getenv(
        "MAX_FILE_SIZE",
        DEFAULT_MAX_FILE_SIZE,
    )
)