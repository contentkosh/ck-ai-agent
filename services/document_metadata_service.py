# ==========================================================
# Document Metadata Service
# Provides utilities to extract structured document metadata
# from raw text using the configured LLM.
# ==========================================================

import json
import re

from dotenv import load_dotenv

from common.llm_client import get_llm
from common.logger import logger

from configuration.config import (
    METADATA_EXTRACTION_TEXT_LIMIT,
)
from configuration.constants import (
    LLM_INVOCATION_FAILED_LOG,
    MARKDOWN_JSON_REGEX,
    METADATA_EXTRACTION_COMPLETED_LOG,
    METADATA_EXTRACTION_STARTED_LOG,
)
from configuration.context import (
    DOCUMENT_METADATA_EXTRACTION_PROMPT,
)
from configuration.error_constants import (
    EMPTY_DOCUMENT_TEXT_ERROR,
    INVALID_METADATA_JSON_ERROR,
    METADATA_EXTRACTION_FAILED_ERROR,
)
from dto.document_metadata_dto import (
    DocumentMetadataDto,
)
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
            raise InvalidMetadataException(
                EMPTY_DOCUMENT_TEXT_ERROR,
            )
        logger.info(METADATA_EXTRACTION_STARTED_LOG)
        prompt = DOCUMENT_METADATA_EXTRACTION_PROMPT.format(
            text=text[:METADATA_EXTRACTION_TEXT_LIMIT],
        )
        try:
            llmResponse = get_llm().invoke(
                prompt,
            )

        except Exception as exception:
            logger.exception(LLM_INVOCATION_FAILED_LOG, exception)
            raise LLMResponseException() from exception

        responseContent = re.sub(
            MARKDOWN_JSON_REGEX,
            "",
            llmResponse.content.strip(),
            flags=re.MULTILINE,
        ).strip()

        documentMetadata = json.loads(
            responseContent,
        )
        logger.info(METADATA_EXTRACTION_COMPLETED_LOG)
        return DocumentMetadataDto(
            **documentMetadata,
        )
    except json.JSONDecodeError as exception:
        logger.exception(
            INVALID_METADATA_JSON_ERROR,
            exception,
        )
        raise InvalidMetadataException(
            INVALID_METADATA_JSON_ERROR,
        ) from exception

    except (
        InvalidMetadataException,
        LLMResponseException,
    ):
        raise
    except Exception as exception:
        logger.exception(
            METADATA_EXTRACTION_FAILED_ERROR,
            exception,
        )
        raise MetadataExtractionException(
            METADATA_EXTRACTION_FAILED_ERROR,
        ) from exception