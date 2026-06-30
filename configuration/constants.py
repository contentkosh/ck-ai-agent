"""
Application-wide constants.

This module contains reusable constants to eliminate hardcoded
values throughout the Knowledge Base project.
"""

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

METADATA_TAG = "tag"

METADATA_SOURCE = "source"

METADATA_FILENAME = "filename"

METADATA_PAGE = "page"

METADATA_DOCUMENT_TYPE = "document_type"


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