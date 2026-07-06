# ==========================================================
# ==========================================
# FILE TYPES
# ==========================================

PDF_EXTENSION = ".pdf"
SUPPORTED_FILE_TYPES = [
    PDF_EXTENSION
]
SUPPORTED_CONTENT_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF-"

# ==========================================
# FILE VALIDATION
# ==========================================

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ==========================================
# DEFAULT VALUES
# ==========================================================

UNKNOWN_TAG = "Unknown"
DEFAULT_ENCODING = "utf-8"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
BYTES_PER_MB = 1024 * 1024

# ==========================================================
# REGEX
# ==========================================================

MARKDOWN_JSON_REGEX = r"^```(?:json)?\s*|\s*```$"

# ==========================================================
# METADATA KEYS
# ==========================================================

METADATA_DOCUMENT_ID = "document_id"
METADATA_TITLE = "title"
METADATA_DOCUMENT_TYPE = "document_type"
METADATA_TAG = "tag"
METADATA_SUMMARY = "summary"
METADATA_SOURCE = "source"
METADATA_FILENAME = "filename"
METADATA_PAGE = "page"
METADATA_TEXT = "text"
METADATA_CLASS = "class"
METADATA_CHAPTER = "chapter"
METADATA_CHAPTER_NO = "chapter_no"

# ==========================================================
# VECTOR SEARCH
# ==========================================================

DEFAULT_SCORE_THRESHOLD = 0.75
DEFAULT_TOP_K = 5

# ==========================================================
# API STATUS
# ==========================================================

SUCCESS_STATUS = "success"
FAILED_STATUS = "failed"
SERVICE_RUNNING_STATUS = "Running"

# ==========================================================
# API ROUTES
# ==========================================================

HEALTH_ROUTE = "/"
LLM_BASE_ROUTE = "/llm"
KNOWLEDGE_BASE_ROUTE = f"{LLM_BASE_ROUTE}/kb"
QUERY_KNOWLEDGE_BASE_ROUTE = f"{KNOWLEDGE_BASE_ROUTE}/query"
UPLOAD_DOCUMENTS_ROUTE = f"{LLM_BASE_ROUTE}/upload"
FILES_ROUTE = f"{LLM_BASE_ROUTE}/files"
DOCUMENTS_ROUTE = FILES_ROUTE
DELETE_DOCUMENT_ROUTE = f"{FILES_ROUTE}/{{document_id}}"
CLEAR_KB_ROUTE = FILES_ROUTE

# ==========================================================
# API SUCCESS MESSAGES
# ==========================================================

UPLOAD_SUCCESS = "Documents uploaded successfully."
DOCUMENT_DELETED_SUCCESS = "Document deleted successfully."
KNOWLEDGE_BASE_CLEARED_SUCCESS = "Knowledge Base cleared successfully."

# ==========================================================
# LOGGER
# ==========================================================

LOGGER_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

# ==========================================================
# COLLECTION SETUP LOGS
# ==========================================================

COLLECTION_CREATED_LOG = "Qdrant collection created successfully."
COLLECTION_ALREADY_EXISTS_LOG = "Qdrant collection already exists."
COLLECTION_SETUP_FAILED_LOG = "Failed to verify or create Qdrant collection."

# ==========================================================
# LLM LOGS
# ==========================================================

LLM_INVOCATION_FAILED_LOG = "LLM invocation failed."
METADATA_EXTRACTION_STARTED_LOG = "Extracting document metadata."
METADATA_EXTRACTION_COMPLETED_LOG = "Metadata extracted successfully."
METADATA_EXTRACTION_FAILED_LOG = ("Document metadata extraction failed: %s")

# ==========================================================
# DATABASE LOGS
# ==========================================================

EMBEDDING_GENERATION_FAILED_LOG = "Embedding generation failed: %s"
VECTOR_INSERTION_LOG = "Inserted %d vectors."
VECTOR_INSERTION_FAILED_LOG = "Vector insertion failed: %s"
SEMANTIC_SEARCH_LOG = "Retrieved %d chunks."
SEMANTIC_SEARCH_FAILED_LOG = "Semantic search failed: %s"
FETCH_RECORDS_LOG = "Fetched %d records."
FETCH_RECORDS_FAILED_LOG = "Unable to fetch records."
FETCH_DOCUMENTS_LOG = "Found %d document(s)."
FETCH_DOCUMENTS_FAILED_LOG = "Unable to fetch uploaded documents."
DELETE_DOCUMENT_LOG = "Deleted document %s."
DELETE_DOCUMENT_FAILED_LOG = "Unable to delete document."
DOCUMENT_NOT_FOUND_LOG = "Document %s not found; nothing deleted."
CLEAR_KB_LOG = "Knowledge Base cleared."
CLEAR_KB_FAILED_LOG = "Unable to clear Knowledge Base."

# ==========================================================
# KNOWLEDGE BASE INGESTION LOGS
# ==========================================================

FILE_SAVE_LOG = "Saving file: %s"
PDF_READ_FAILED_LOG = "Failed to read PDF '%s': %s"
PAGE_READ_FAILED_LOG = "Unable to read page %d: %s"
PAGES_EXTRACTED_LOG = "Extracted %d pages."
DOCUMENT_PROCESSING_STARTED_LOG = "Processing document: %s"
DOCUMENT_PROCESSED_LOG = "Processed %s (%d chunks)."
DOCUMENT_PROCESSING_FAILED_LOG = "Document processing failed: %s"
KB_INGESTION_STARTED_LOG = "Knowledge Base ingestion started."
KB_INGESTION_COMPLETED_LOG = ("Knowledge Base ingestion completed. Documents=%d Chunks=%d")
KB_INGESTION_FAILED_LOG = "Knowledge Base ingestion failed: %s"
FILE_PROCESSING_STARTED_LOG = "Processing file: %s"
FILE_PROCESSING_COMPLETED_LOG = "Successfully processed '%s'."
GENERATED_VECTORS_LOG = "Generated %d vectors."
PAGE_CHUNK_GENERATION_LOG = "Page %d generated %d chunks."

# ==========================================================
# QUERY SERVICE LOGS
# ==========================================================

EMPTY_QUERY_ERROR = "Query cannot be empty."

QUERY_LENGTH_ERROR = (
    "Query cannot exceed {} characters."
)

QUERY_RECEIVED_LOG = "Received query: %s"
NO_RELEVANT_CHUNKS_LOG = "No relevant chunks found."
RETRIEVED_CHUNKS_LOG = "Retrieved %d chunk(s)."
TOP_MATCHING_SOURCE_LOG = "Top matching source: %s"
CHAT_SERVICE_FAILED_LOG = "Chat service failed: %s"

# ==========================================================
# FILE SERVICE LOGS
# ==========================================================

TEMP_FILE_DELETED_LOG = "Deleted temporary upload file: %s"
TEMP_FILE_DELETE_FAILED_LOG = (
    "Failed to delete temporary upload file '%s': %s"
)

# ==========================================================
# API LOGS
# ==========================================================

HEALTH_API_LOG = "[%s] Health API called."
FETCH_KB_REQUEST_LOG = "[%s] Fetching Knowledge Base."
FETCH_KB_SUCCESS_LOG = "[%s] Retrieved %d record(s)."
QUERY_REQUEST_LOG = "[%s] Question received."
QUERY_SUCCESS_LOG = "[%s] Question answered successfully."
UPLOAD_REQUEST_LOG = "[%s] Upload request received."
UPLOAD_SUCCESS_LOG = "[%s] Uploaded %d document(s) successfully."
FETCH_UPLOADED_DOCUMENTS_LOG = "[%s] Fetching uploaded documents."
FETCH_UPLOADED_DOCUMENTS_SUCCESS_LOG = (
    "[%s] Retrieved %d uploaded document(s)."
)
DELETE_DOCUMENT_REQUEST_LOG = (
    "[%s] Delete request received. Document ID=%s"
)
DELETE_DOCUMENT_SUCCESS_LOG = "[%s] Document deleted successfully."
CLEAR_KB_REQUEST_LOG = "[%s] Clearing Knowledge Base."
CLEAR_KB_SUCCESS_LOG = "[%s] Knowledge Base cleared successfully."

# ==========================================================
# QDRANT CLIENT LOGS
# ==========================================================

QDRANT_CLIENT_INITIALIZING_LOG = (
    "Initializing Qdrant client. host=%s port=%s"
)
QDRANT_CLIENT_INITIALIZED_LOG = (
    "Qdrant client initialized successfully."
)

# ==========================================================
# COLLECTION SCRIPTS
# ==========================================================

DOCUMENTS_HEADER_LOG = "========== DOCUMENTS =========="
DOCUMENT_DETAILS_LOG = (
    "Title=%s | Type=%s | Tag=%s | Source=%s | Page=%s"
)
DOCUMENT_SEPARATOR_LOG = (
    "----------------------------------------"
)
COLLECTION_STATS_HEADER_LOG = (
    "========== Collection Statistics =========="
)
COLLECTION_STATS_LOG = (
    "Name=%s | Vectors=%s | Status=%s"
)
COLLECTION_CREATED_SUCCESS_LOG = (
    "Collection created successfully."
)
COLLECTION_ALREADY_EXISTS_SCRIPT_LOG = (
    "Collection already exists."
)
COLLECTION_CREATION_FAILED_LOG = (
    "Failed to create collection."
)
COLLECTION_DELETED_SUCCESS_LOG = (
    "Collection '%s' deleted successfully."
)

# ==========================================================
# GLOBAL LOGS
# ==========================================================

UNHANDLED_EXCEPTION_LOG = "Unhandled Exception: %s"

FETCH_UPLOADED_DOCUMENTS_FAILED_LOG = (
    "Failed to fetch uploaded documents: %s"
)
CLEAR_KNOWLEDGE_BASE_FAILED_LOG = (
    "Failed to clear Knowledge Base: %s"
)

# ==========================================================
# File Utility Logs
# ==========================================================

DELETE_TEMP_FILE_SUCCESS_LOG = (
    "Temporary file deleted successfully: %s"
)
DELETE_TEMP_FILE_FAILED_LOG = (
    "Failed to delete temporary file: %s"
)

# ==========================================================
# File Validation Constants
# ==========================================================

PDF_EXTENSION = ".pdf"
SUPPORTED_CONTENT_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF"
MAX_SCROLL_ITERATIONS_REACHED_LOG = (
    "Maximum scroll iterations reached while reading Qdrant records."
)

# ==========================================================
# CACHE
# ==========================================================

DOCUMENT_NOT_FOUND_ERROR = "Document '{}' does not exist."

INVALID_CACHE_RESPONSES = [
    "I don't know",
    "Answer not found",
    "No relevant context found",
]

CACHE_SOURCE = "CACHE"