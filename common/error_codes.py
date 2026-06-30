"""
Application error codes.

Each error code uniquely identifies a specific failure
scenario across the Knowledge Base application.
"""


class ErrorCodes:
    """
    Centralized application error codes.
    """

    # ==========================================
    # Document Errors (DOC)
    # ==========================================

    DOCUMENT_NOT_FOUND = "DOC_001"
    INVALID_DOCUMENT = "DOC_002"
    DOCUMENT_PROCESSING_FAILED = "DOC_003"
    EMPTY_DOCUMENT = "DOC_004"

    # ==========================================
    # Validation Errors (VAL)
    # ==========================================

    INVALID_FILE_TYPE = "VAL_001"
    INVALID_TAG = "VAL_002"
    EMPTY_FILE = "VAL_003"
    INVALID_REQUEST = "VAL_004"

    # ==========================================
    # Metadata Errors (META)
    # ==========================================

    METADATA_EXTRACTION_FAILED = "META_001"
    INVALID_METADATA = "META_002"

    # ==========================================
    # Embedding Errors (EMB)
    # ==========================================

    EMBEDDING_GENERATION_FAILED = "EMB_001"

    # ==========================================
    # Qdrant Errors (QDR)
    # ==========================================

    QDRANT_CONNECTION_FAILED = "QDR_001"
    QDRANT_INSERT_FAILED = "QDR_002"
    QDRANT_SEARCH_FAILED = "QDR_003"

    # ==========================================
    # LLM Errors (LLM)
    # ==========================================

    LLM_RESPONSE_FAILED = "LLM_001"
    LLM_TIMEOUT = "LLM_002"

    # ==========================================
    # API Errors (API)
    # ==========================================

    INTERNAL_SERVER_ERROR = "API_500"
    BAD_REQUEST = "API_400"
    NOT_FOUND = "API_404"
