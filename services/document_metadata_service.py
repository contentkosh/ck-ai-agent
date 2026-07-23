# ==========================================================
# Document Metadata Service
# Provides utilities to extract structured document metadata
# from raw text using the configured LLM.
# ==========================================================

import json
import re
from typing import Any
from dotenv import load_dotenv
from common.llm_client import get_llm
from common.logger import logger
from dto.document_metadata_dto import DocumentMetadataDto
from configuration.config import (METADATA_EXTRACTION_TEXT_LIMIT,)
from configuration.constants import (
    EMPTY_DOCUMENT_TEXT_ERROR,
    INVALID_METADATA_JSON_ERROR,
    METADATA_EXTRACTION_FAILED_ERROR,
    MARKDOWN_JSON_REGEX,
    LLM_INVOCATION_FAILED_LOG,
    METADATA_EXTRACTION_STARTED_LOG,
    METADATA_EXTRACTION_COMPLETED_LOG,
)

from configuration.context import (DOCUMENT_METADATA_EXTRACTION_PROMPT,)
from exceptions.llm_exception import (
    LLMResponseException,
)

from exceptions.metadata_exception import (
    InvalidMetadataException,
    MetadataExtractionException,
)

load_dotenv()

# ==========================================================
# Extract Metadata
# ==========================================================

def extract_document_metadata(
    text: str,
) -> DocumentMetadataDto:
    
    """
    Extract document metadata using the configured LLM.
    """
    try:
        if not text.strip():
            raise InvalidMetadataException(EMPTY_DOCUMENT_TEXT_ERROR,)

        logger.info(METADATA_EXTRACTION_STARTED_LOG,)
        prompt = DOCUMENT_METADATA_EXTRACTION_PROMPT.format(
            text=text[:METADATA_EXTRACTION_TEXT_LIMIT],
        )

        try:
            llmResponse = get_llm().invoke(
                prompt,
            )

        except Exception as ex:
            logger.exception(LLM_INVOCATION_FAILED_LOG,)
            raise LLMResponseException() from ex

        responseContent = re.sub(
            MARKDOWN_JSON_REGEX,
            "",
            llmResponse.content.strip(),
            flags=re.MULTILINE,
        ).strip()

        documentMetadata = json.loads(responseContent,)
        logger.info(METADATA_EXTRACTION_COMPLETED_LOG,)
        DocumentMetadataDto(**documentMetadata)

    except json.JSONDecodeError as ex:
        logger.exception(INVALID_METADATA_JSON_ERROR,)
        raise InvalidMetadataException(INVALID_METADATA_JSON_ERROR,) from ex

    except (
        InvalidMetadataException,
        LLMResponseException,
    ):
        raise

    except Exception as ex:
        logger.exception(METADATA_EXTRACTION_FAILED_ERROR,)
        raise MetadataExtractionException(METADATA_EXTRACTION_FAILED_ERROR,) from ex