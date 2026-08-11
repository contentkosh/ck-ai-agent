import os
from dotenv import load_dotenv

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

# ==========================================================
# API SERVER
# ==========================================================

API_HOST = os.getenv("API_HOST","0.0.0.0",)
API_PORT = int(os.getenv("API_PORT",8000,))
API_RELOAD = os.getenv("API_RELOAD","False",).lower() == "true"

# ==========================================================
# Application Configuration
# ==========================================================

API_TITLE = "Knowledge Base API"
API_VERSION = "1.0.0"

# ==========================================================
# AUTHENTICATION
# ==========================================================

API_KEY = os.getenv("API_KEY")
API_KEY_HEADER_NAME = os.getenv("API_KEY_HEADER_NAME", "X-API-Key")
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "True").lower() == "true"

# ==========================================================
# QDRANT
# ==========================================================

QDRANT_HOST = os.getenv("QDRANT_HOST","localhost",)
QDRANT_PORT = int(os.getenv("QDRANT_PORT",6333,))
COLLECTION_NAME = os.getenv("COLLECTION_NAME","knowledge_base",)
SCROLL_LIMIT = int(os.getenv("SCROLL_LIMIT",5000,))

# ==========================================================
# SEARCH
# ==========================================================

SEARCH_LIMIT = int(os.getenv("SEARCH_LIMIT",5,))

# ==========================================================
# EMBEDDINGS
# ==========================================================

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2",)
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION",384,))

# ==========================================================
# QUERY VALIDATION
# ==========================================================

MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH",1000,))

# ==========================================================
# LLM
# ==========================================================

LLM_MODEL = os.getenv("LLM_MODEL","nvidia/nemotron-3-super-120b-a12b:free",)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY",)
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL","https://openrouter.ai/api/v1",)

# ==========================================================
# METADATA EXTRACTION
# ==========================================================

METADATA_EXTRACTION_TEXT_LIMIT = int(os.getenv("METADATA_EXTRACTION_TEXT_LIMIT",4000,))

# ==========================================================
# CHUNKING
# ==========================================================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE",500,))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP",50,))

# ==========================================================
# FILE STORAGE
# ==========================================================

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER","uploads",)
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE",DEFAULT_MAX_FILE_SIZE,))

# ==========================================================
# LOGGING
# ==========================================================

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/application.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10 MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# ==========================================================
# TAG VALIDATION
# ==========================================================

MAX_TAG_LENGTH = int(os.getenv("MAX_TAG_LENGTH",100))

# ==========================================================
# Environment Variable Names
# ==========================================================

OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"

# ==========================================
# FILE TYPES
# ==========================================

PDF_EXTENSION = ".pdf"
SUPPORTED_FILE_TYPES = [PDF_EXTENSION]
SUPPORTED_CONTENT_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF-"
MAX_SCROLL_ITERATIONS = 1000

POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")