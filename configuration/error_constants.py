# ==========================================================
# GENERIC ERROR MESSAGES
# ==========================================================

DATABASE_ERROR_MESSAGE = "Database operation failed."
PDF_PROCESSING_ERROR_MESSAGE = "Unable to process PDF."
EMBEDDING_ERROR_MESSAGE = "Embedding generation failed."
VALIDATION_ERROR_MESSAGE = "Validation failed."
RESOURCE_NOT_FOUND_MESSAGE = "Resource not found."
AUTHENTICATION_FAILED_MESSAGE = "Authentication failed."
INTERNAL_SERVER_ERROR_MESSAGE = "Internal Server Error"

# ==========================================================
# DOCUMENT ERROR MESSAGES
# ==========================================================

DOCUMENT_PROCESSING_ERROR_MESSAGE = "Document processing failed."
DOCUMENT_NOT_FOUND_MESSAGE = "Document not found."
INVALID_DOCUMENT_MESSAGE = "Invalid document."
EMPTY_DOCUMENT_MESSAGE = "Document is empty."

# ==========================================================
# LLM ERROR MESSAGES
# ==========================================================

LLM_RESPONSE_ERROR_MESSAGE = "LLM response generation failed."
LLM_TIMEOUT_ERROR_MESSAGE = "LLM request timed out."

# ==========================================================
# METADATA ERROR MESSAGES
# ==========================================================

METADATA_EXTRACTION_ERROR_MESSAGE = "Metadata extraction failed."
INVALID_METADATA_ERROR_MESSAGE = "Invalid metadata."
EMPTY_DOCUMENT_TEXT_ERROR = ("Document text is empty; cannot extract metadata.")
INVALID_METADATA_JSON_ERROR = ("LLM returned invalid JSON metadata.")
METADATA_EXTRACTION_FAILED_ERROR = ("Metadata extraction failed.")

# ==========================================================
# QDRANT ERROR MESSAGES
# ==========================================================

QDRANT_CONNECTION_ERROR_MESSAGE = ("Unable to connect to Qdrant.")
QDRANT_INSERT_ERROR_MESSAGE = ("Failed to insert vectors into Qdrant.")
QDRANT_SEARCH_ERROR_MESSAGE = ("Failed to search Qdrant.")
QDRANT_FETCH_ERROR_MESSAGE = ("Failed to fetch Knowledge Base records.")
QDRANT_DELETE_ERROR_MESSAGE = ("Failed to delete Knowledge Base records.")

# ==========================================================
# VALIDATION ERROR MESSAGES
# ==========================================================

INVALID_FILE_ERROR_MESSAGE = "Invalid file uploaded."
INVALID_TAG_ERROR_MESSAGE = "Invalid tag."
EMPTY_FILE_ERROR_MESSAGE = "Uploaded file is empty."
INVALID_REQUEST_ERROR_MESSAGE = "Invalid request."

# ==========================================================
# DATABASE ERROR MESSAGES
# ==========================================================

DATABASE_INSERT_ERROR_MESSAGE = ("Unable to insert vectors.")
DATABASE_SEARCH_ERROR_MESSAGE = ("Semantic search failed.")
DATABASE_FETCH_ERROR_MESSAGE = ("Unable to fetch records.")
DATABASE_FETCH_DOCUMENTS_ERROR_MESSAGE = ("Unable to fetch uploaded documents.")
DATABASE_DELETE_ERROR_MESSAGE = ("Unable to delete document.")
DATABASE_CLEAR_ERROR_MESSAGE = ("Unable to clear Knowledge Base.")

# ==========================================================
# KNOWLEDGE BASE INGESTION ERRORS
# ==========================================================

EMBEDDING_GENERATION_FAILED_MESSAGE = ("Failed to generate embedding.")
PDF_READ_FAILED_MESSAGE = ("Unable to process '{}'.")
DOCUMENT_METADATA_EXTRACTION_FAILED_MESSAGE = ("Unable to extract document metadata.")
DOCUMENT_PROCESSING_FAILED_MESSAGE = ("Failed to process '{}'.")
KNOWLEDGE_BASE_INGESTION_FAILED_MESSAGE = ("Knowledge Base ingestion failed.")
EMPTY_DOCUMENT_TEXT_MESSAGE = ("The uploaded PDF contains no readable text.")

# ==========================================================
# QUERY ERROR MESSAGES
# ==========================================================

EMPTY_QUERY_ERROR = "Query cannot be empty."
QUERY_LENGTH_ERROR = ("Query cannot exceed {} characters.")
ANSWER_NOT_FOUND_MESSAGE = ("Answer not found in the Knowledge Base.")
CHAT_SERVICE_ERROR_MESSAGE = ("Unable to process user query.")

# ==========================================================
# FILE VALIDATION ERRORS
# ==========================================================

NO_FILENAME_ERROR = ("Uploaded file has no filename.")
INVALID_FILE_TYPE_ERROR = ("Invalid file type. Only PDF files are allowed.")
EMPTY_UPLOADED_FILE_ERROR = ("Uploaded file is empty.")
INVALID_PDF_SIGNATURE_ERROR = ("File content does not match a valid PDF.")
FILE_SIZE_EXCEEDED_ERROR = ("File size exceeds the maximum allowed limit of {} MB.")
UPLOADED_FILE_NOT_FOUND_ERROR = ("Uploaded file could not be found.")

# ==========================================================
# TAG VALIDATION ERRORS
# ==========================================================

EMPTY_TAG_ERROR = "Tag cannot be empty."
TAG_LENGTH_ERROR = ("Tag exceeds maximum length of {} characters.")

# ==========================================================
# UPLOAD VALIDATION ERRORS
# ==========================================================

NO_FILES_UPLOADED_ERROR = ("No files were uploaded.")

# ==========================================================
# API ERROR RESPONSES
# ==========================================================

UPLOAD_FAILED = "Document upload failed."
INVALID_FILE = "Only PDF files are allowed."
INVALID_TAG = "Tag cannot be empty."

# ==========================================================
# COLLECTION SCRIPT ERRORS
# ==========================================================

DOCUMENT_NOT_FOUND_ERROR = ("Document '{}' does not exist.")
KNOWLEDGE_BASE_ERROR_MESSAGE = ("Knowledge Base operation failed.")

DATABASE_INSERT_ERROR_MESSAGE = ("Unable to insert vectors.")
DATABASE_SEARCH_ERROR_MESSAGE = ("Semantic search failed.")
DATABASE_FETCH_ERROR_MESSAGE = ("Unable to fetch records.")
DATABASE_FETCH_DOCUMENTS_ERROR_MESSAGE = ("Unable to fetch uploaded documents.")
DATABASE_DELETE_ERROR_MESSAGE = ("Unable to delete document.")
DATABASE_CLEAR_ERROR_MESSAGE = ("Unable to clear Knowledge Base.")