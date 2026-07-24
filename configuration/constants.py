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
# DEFAULT VALUES
# ==========================================

UNKNOWN_TAG = "Unknown"
DEFAULT_ENCODING = "utf-8"

# ==========================================
# CHUNKING
# ==========================================

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

# ==========================================================
# REGEX PATTERNS
# ==========================================================

MARKDOWN_JSON_REGEX = r"^```(?:json)?\s*|\s*```$"

# ==========================================
# LOGGING
# ==========================================

DOCUMENT_UPLOAD_STARTED_LOG = "Document upload started."
DOCUMENT_UPLOAD_COMPLETED_LOG = "Document upload completed."
METADATA_EXTRACTION_STARTED = "Metadata extraction started."
METADATA_EXTRACTION_COMPLETED = "Metadata extraction completed."
EMBEDDING_GENERATION_STARTED = "Embedding generation started."
EMBEDDING_GENERATION_COMPLETED = "Embedding generation completed."
QDRANT_UPLOAD_STARTED = "Uploading vectors to Qdrant."
QDRANT_UPLOAD_COMPLETED = "Successfully uploaded vectors to Qdrant."

# ==========================================================
# LLM LOG MESSAGES
# ==========================================================

LLM_INVOCATION_FAILED_LOG = "LLM invocation failed."
METADATA_EXTRACTION_STARTED_LOG = "Extracting document metadata."
METADATA_EXTRACTION_COMPLETED_LOG = "Metadata extracted successfully."

# ==========================================================
# COLLECTION SETUP LOGS
# ==========================================================

COLLECTION_CREATED_LOG = "Qdrant collection created successfully."
COLLECTION_ALREADY_EXISTS_LOG = "Qdrant collection already exists."
COLLECTION_SETUP_FAILED_LOG = ("Failed to verify or create Qdrant collection.")

# ==========================================
# API RESPONSES
# ==========================================

SUCCESS_STATUS = "Success"
FAILED_STATUS = "Failed"
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
QUERY_KNOWLEDGE_BASE_ROUTE = f"{KNOWLEDGE_BASE_ROUTE}/query"

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
EMPTY_DOCUMENT_TEXT_ERROR = "Document text is empty; cannot extract metadata."
INVALID_METADATA_JSON_ERROR = "LLM returned invalid JSON metadata."
METADATA_EXTRACTION_FAILED_ERROR = "Metadata extraction failed."

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
# KNOWLEDGE BASE INGESTION ERROR MESSAGES
# ==========================================================

EMBEDDING_GENERATION_FAILED_MESSAGE = "Failed to generate embedding."
PDF_READ_FAILED_MESSAGE = "Unable to process '{}'."
DOCUMENT_METADATA_EXTRACTION_FAILED_MESSAGE = ("Unable to extract document metadata.")
DOCUMENT_PROCESSING_FAILED_MESSAGE = "Failed to process '{}'."
KNOWLEDGE_BASE_INGESTION_FAILED_MESSAGE = ("Knowledge Base ingestion failed.")
EMPTY_DOCUMENT_TEXT_MESSAGE = ("The uploaded PDF contains no readable text.")
# ==========================================================
# LOG MESSAGES
# ==========================================================

UNHANDLED_EXCEPTION_LOG = "Unhandled Exception: %s"

# ==========================================================
# DATABASE LOG MESSAGES
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
# KNOWLEDGE BASE INGESTION LOG MESSAGES
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
# VALIDATION MESSAGES
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
CHAT_SERVICE_ERROR_MESSAGE = "Unable to process user query."
ANSWER_NOT_FOUND_MESSAGE = "Answer not found in the Knowledge Base."
DOCUMENT_NOT_FOUND_LOG = "Document %s not found; nothing deleted."

# ==========================================================
# FILE SERVICE LOG MESSAGES
# ==========================================================

TEMP_FILE_DELETED_LOG = "Deleted temporary upload file: %s"
TEMP_FILE_DELETE_FAILED_LOG = ("Failed to delete temporary upload file '%s': %s")

# ==========================================================
# HEALTH API
# ==========================================================

HEALTH_ROUTE = "/"
HEALTH_API_LOG = "[%s] Health API called."
SERVICE_RUNNING_STATUS = "Running"

SUCCESS_STATUS = "success"
METADATA_EXTRACTION_FAILED_LOG = "Metadata extraction failed: %s"

# ==========================================================
# File Validation Messages
# ==========================================================

NO_FILENAME_ERROR = (
    "Uploaded file has no filename."
)
ONLY_PDF_ALLOWED_ERROR = (
    "Only PDF files are allowed."
)
INVALID_FILE_TYPE_ERROR = (
    "Invalid file type. Only PDF files are allowed."
)
EMPTY_UPLOADED_FILE_ERROR = (
    "Uploaded file is empty."
)
INVALID_PDF_SIGNATURE_ERROR = (
    "File content does not match a valid PDF."
)
FILE_SIZE_EXCEEDED_ERROR = (
    "File size exceeds the maximum allowed limit of {} MB."
)
UPLOADED_FILE_NOT_FOUND_ERROR = (
    "Uploaded file could not be found."
)
BYTES_PER_MB = 1024 * 1024

# ==========================================================
# Tag Validation Messages
# ==========================================================

EMPTY_TAG_ERROR = "Tag cannot be empty."

TAG_LENGTH_ERROR = (
    "Tag exceeds maximum length of {} characters."
)

# ==========================================================
# Upload Validation Messages
# ==========================================================

NO_FILES_UPLOADED_ERROR = "No files were uploaded."

# ==========================================================
# File API Response Messages
# ==========================================================

SUCCESS_STATUS = "success"

DOCUMENT_DELETED_SUCCESS = (
    "Document deleted successfully."
)

KNOWLEDGE_BASE_CLEARED_SUCCESS = (
    "Knowledge Base cleared successfully."
)

# ==========================================================
# Knowledge Base API Logs
# ==========================================================

FETCH_KB_REQUEST_LOG = "[%s] Fetching Knowledge Base."
FETCH_KB_SUCCESS_LOG = "[%s] Retrieved %d record(s)."
QUERY_REQUEST_LOG = "[%s] Question received."
QUERY_SUCCESS_LOG = "[%s] Question answered successfully."

# ==========================================================
# Upload API Logs
# ==========================================================

UPLOAD_REQUEST_LOG = "[%s] Upload request received."
UPLOAD_SUCCESS_LOG = "[%s] Uploaded %d document(s) successfully."

# ==========================================================
# File Service Logs
# ==========================================================

DELETE_TEMP_FILE_SUCCESS_LOG = ("Deleted temporary upload file: %s")
DELETE_TEMP_FILE_FAILED_LOG = ("Failed to delete temporary upload file '%s': %s")

# ==========================================================
# Logger
# ==========================================================

LOGGER_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

# ==========================================================
# Qdrant Client
# ==========================================================

QDRANT_CLIENT_INITIALIZING_LOG = (
    "Initializing Qdrant client. host=%s port=%s"
)

QDRANT_CLIENT_INITIALIZED_LOG = (
    "Qdrant client initialized successfully."
)
# ==========================================================
# Check Collection Script
# ==========================================================
DOCUMENTS_HEADER_LOG = "========== DOCUMENTS =========="
DOCUMENT_DETAILS_LOG = ("Title=%s | Type=%s | Tag=%s | Source=%s | Page=%s")
DOCUMENT_SEPARATOR_LOG = ("----------------------------------------")
# ==========================================================
# Collection Statistics
# ==========================================================
COLLECTION_STATS_HEADER_LOG = ("========== Collection Statistics ==========")
COLLECTION_STATS_LOG = ("Name=%s | Vectors=%s | Status=%s")
# ==========================================================
# Create Collection Script
# ==========================================================

COLLECTION_CREATED_SUCCESS_LOG = ("Collection created successfully.")
COLLECTION_ALREADY_EXISTS_SCRIPT_LOG = ("Collection already exists.")
COLLECTION_CREATION_FAILED_LOG = ("Failed to create collection.")

# ==========================================================
# Delete Collection Script
# ==========================================================

COLLECTION_DELETED_SUCCESS_LOG = ("Collection '%s' deleted successfully.")

DOCUMENT_NOT_FOUND_ERROR = "Document '{}' does not exist."