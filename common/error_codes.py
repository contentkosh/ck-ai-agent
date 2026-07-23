from enum import Enum

class ErrorCode(str, Enum):
    """
    Centralized application error codes.
    """
    # ==========================================
    # Document Errors (DOC)
    # ==========================================

    DOCUMENT_NOT_FOUND = "DOCUMENT_NOT_FOUND"
    INVALID_DOCUMENT = "INVALID_DOCUMENT"
    DOCUMENT_PROCESSING_FAILED = "DOCUMENT_PROCESSING_FAILED"
    EMPTY_DOCUMENT = "EMPTY_DOCUMENT"

    # ==========================================
    # Validation Errors (VAL)
    # ==========================================

    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    INVALID_TAG = "INVALID_TAG"
    EMPTY_FILE = "EMPTY_FILE"
    INVALID_REQUEST = "INVALID_REQUEST"
    EMPTY_QUERY = "EMPTY_QUERY"
    INVALID_QUERY = "INVALID_QUERY"

    # ==========================================
    # Metadata Errors (META)
    # ==========================================

    METADATA_EXTRACTION_FAILED = "METADATA_EXTRACTION_FAILED"
    INVALID_METADATA = "INVALID_METADATA"

    # ==========================================
    # Embedding Errors (EMB)
    # ==========================================

    EMBEDDING_GENERATION_FAILED = "EMBEDDING_GENERATION_FAILED"

    # ==========================================
    # Qdrant Errors (QDR)
    # ==========================================

    QDRANT_CONNECTION_FAILED = "QDRANT_CONNECTION_FAILED"
    QDRANT_INSERT_FAILED = "QDRANT_INSERT_FAILED"
    QDRANT_SEARCH_FAILED = "QDRANT_SEARCH_FAILED"

    # ==========================================
    # LLM Errors (LLM)
    # ==========================================

    LLM_RESPONSE_FAILED = "LLM_RESPONSE_FAILED"

    # ==========================================
    # API Errors (API)
    # ==========================================

    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"