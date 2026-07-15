
# ==========================================
# FILE TYPES
# ==========================================

PDF_EXTENSION = ".pdf"
SUPPORTED_FILE_TYPES = [
    PDF_EXTENSION
]
SUPPORTED_CONTENT_TYPE = "application/pdf"

# ==========================================
# DEFAULT VALUES
# ==========================================

UNKNOWN_TAG = "Unknown"
DEFAULT_ENCODING = "utf-8"

# ==========================================
# CHUNKING
# ==========================================

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

# ==========================================
# LOGGING
# ==========================================

UPLOAD_STARTED = "Document upload started."
UPLOAD_COMPLETED = "Document upload completed."
METADATA_EXTRACTION_STARTED = "Metadata extraction started."
METADATA_EXTRACTION_COMPLETED = "Metadata extraction completed."
EMBEDDING_GENERATION_STARTED = "Embedding generation started."
EMBEDDING_GENERATION_COMPLETED = "Embedding generation completed."
QDRANT_UPLOAD_STARTED = "Uploading vectors to Qdrant."
QDRANT_UPLOAD_COMPLETED = "Successfully uploaded vectors to Qdrant."

# ==========================================
# API RESPONSES
# ==========================================

SUCCESS = "Success"
FAILED = "Failed"
UPLOAD_SUCCESS = "Documents uploaded successfully."
UPLOAD_FAILED = "Document upload failed."
INVALID_FILE = "Only PDF files are allowed."
INVALID_TAG = "Tag cannot be empty."

# ==========================================
# METADATA KEYS
# ==========================================

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

# ==========================================
# VECTOR DATABASE
# ==========================================

DEFAULT_SCORE_THRESHOLD = 0.75
DEFAULT_TOP_K = 5

# ==========================================
# API
# ==========================================

API_TITLE = "Knowledge Base API"
API_VERSION = "1.0.0"

# ==========================================================
# API ROUTES
# ==========================================================

LLM_BASE_ROUTE = "/llm"

KNOWLEDGE_BASE_ROUTE = f"{LLM_BASE_ROUTE}/kb"
UPLOAD_DOCUMENTS_ROUTE = f"{LLM_BASE_ROUTE}/upload"
FILES_ROUTE = f"{LLM_BASE_ROUTE}/files"
DOCUMENTS_ROUTE = f"{LLM_BASE_ROUTE}/doc"
DELETE_DOCUMENT_ROUTE = f"{FILES_ROUTE}/delete/{{document_id}}"
CLEAR_KB_ROUTE = f"{FILES_ROUTE}/delete"
# ==========================================================
# FILE ROUTE LOG MESSAGES
# ==========================================================

FETCH_UPLOADED_DOCUMENTS_LOG = "[%s] Fetching uploaded documents."
FETCH_UPLOADED_DOCUMENTS_SUCCESS_LOG = ("[%s] Retrieved %d uploaded document(s).")
DELETE_DOCUMENT_REQUEST_LOG = ("[%s] Delete request received. Document ID=%s")
DELETE_DOCUMENT_SUCCESS_LOG = ("[%s] Document deleted successfully.")
CLEAR_KB_REQUEST_LOG = ("[%s] Clearing Knowledge Base.")
CLEAR_KB_SUCCESS_LOG = ("[%s] Knowledge Base cleared successfully.")

# ==========================================================
# EXCEPTION MESSAGES
# ==========================================================

DATABASE_ERROR_MESSAGE = "Database operation failed."
PDF_PROCESSING_ERROR_MESSAGE = "Unable to process PDF."
EMBEDDING_ERROR_MESSAGE = "Embedding generation failed."
VALIDATION_ERROR_MESSAGE = "Validation failed."
RESOURCE_NOT_FOUND_MESSAGE = "Resource not found."
AUTHENTICATION_FAILED_MESSAGE = "Authentication failed."
INTERNAL_SERVER_ERROR_MESSAGE = "Internal Server Error"

# ==========================================================
# DOCUMENT EXCEPTION MESSAGES
# ==========================================================

DOCUMENT_PROCESSING_ERROR_MESSAGE = "Document processing failed."
DOCUMENT_NOT_FOUND_MESSAGE = "Document not found."
INVALID_DOCUMENT_MESSAGE = "Invalid document."
EMPTY_DOCUMENT_MESSAGE = "Document is empty."

# ==========================================================
# LLM EXCEPTION MESSAGES
# ==========================================================

LLM_RESPONSE_ERROR_MESSAGE = "LLM response generation failed."
LLM_TIMEOUT_ERROR_MESSAGE = "LLM request timed out."

# ==========================================================
# METADATA EXCEPTION MESSAGES
# ==========================================================

METADATA_EXTRACTION_ERROR_MESSAGE = "Metadata extraction failed."
INVALID_METADATA_ERROR_MESSAGE = "Invalid metadata."

# ==========================================================
# QDRANT EXCEPTION MESSAGES
# ==========================================================

QDRANT_CONNECTION_ERROR_MESSAGE = "Unable to connect to Qdrant."
QDRANT_INSERT_ERROR_MESSAGE = "Failed to insert vectors into Qdrant."
QDRANT_SEARCH_ERROR_MESSAGE = "Failed to search Qdrant."

# ==========================================================
# VALIDATION EXCEPTION MESSAGES
# ==========================================================

INVALID_FILE_ERROR_MESSAGE = "Invalid file uploaded."
INVALID_TAG_ERROR_MESSAGE = "Invalid tag."
EMPTY_FILE_ERROR_MESSAGE = "Uploaded file is empty."
INVALID_REQUEST_ERROR_MESSAGE = "Invalid request."

# ==========================================================
# DATABASE EXCEPTION MESSAGES
# ==========================================================

DATABASE_INSERT_ERROR_MESSAGE = "Unable to insert vectors."
DATABASE_SEARCH_ERROR_MESSAGE = "Semantic search failed."
DATABASE_FETCH_ERROR_MESSAGE = "Unable to fetch records."
DATABASE_FETCH_DOCUMENTS_ERROR_MESSAGE = "Unable to fetch uploaded documents."
DATABASE_DELETE_ERROR_MESSAGE = "Unable to delete document."
DATABASE_CLEAR_ERROR_MESSAGE = "Unable to clear Knowledge Base."

# ==========================================================
# LOG MESSAGES
# ==========================================================

UNHANDLED_EXCEPTION_LOG = "Unhandled Exception: %s"

# ==========================================================
# DATABASE LOG MESSAGES
# ==========================================================

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

CLEAR_KB_LOG = "Knowledge Base cleared."
CLEAR_KB_FAILED_LOG = "Unable to clear Knowledge Base."

# ==========================================================
# VALIDATION MESSAGES
# ==========================================================

EMPTY_QUERY_ERROR = "Query cannot be empty."
QUERY_LENGTH_ERROR = (
    "Query cannot exceed {} characters."
)
