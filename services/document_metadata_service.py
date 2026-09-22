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
# Extract First JSON Object
# ==========================================================


def extract_first_json_object(
    response_content: str,
) -> dict:
    """
    Extract the first JSON object from the LLM response.

    The local LLM may sometimes return the required metadata
    JSON followed by additional JSON or explanatory content.

    This function parses only the first JSON object, which
    contains the document metadata.
    """

    cleanedContent = re.sub(
        MARKDOWN_JSON_REGEX,
        "",
        response_content.strip(),
        flags=re.MULTILINE,
    ).strip()

    jsonStart = cleanedContent.find("{")

    if jsonStart == -1:
        raise json.JSONDecodeError(
            "No JSON object found.",
            cleanedContent,
            0,
        )

    decoder = json.JSONDecoder()

    documentMetadata, _ = decoder.raw_decode(
        cleanedContent,
        jsonStart,
    )

    if not isinstance(
        documentMetadata,
        dict,
    ):
        raise json.JSONDecodeError(
            "Metadata JSON must be an object.",
            cleanedContent,
            jsonStart,
        )

    return documentMetadata


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

        logger.info(
            METADATA_EXTRACTION_STARTED_LOG,
        )

        prompt = DOCUMENT_METADATA_EXTRACTION_PROMPT.format(
            text=text[:METADATA_EXTRACTION_TEXT_LIMIT],
        )

        # --------------------------------------------------
        # LLM Invocation
        # --------------------------------------------------

        try:
            llmResponse = get_llm().invoke(
                prompt,
            )

            # Temporary logging to inspect the exact
            # response returned by the local LLM.
            logger.error(
                "RAW METADATA LLM RESPONSE: %s",
                llmResponse.content,
            )

        except Exception as exception:
            logger.exception(
                LLM_INVOCATION_FAILED_LOG,
            )

            raise LLMResponseException() from exception

        # --------------------------------------------------
        # Parse Metadata JSON
        # --------------------------------------------------

        documentMetadata = extract_first_json_object(
            llmResponse.content,
        )

        logger.info(
            METADATA_EXTRACTION_COMPLETED_LOG,
        )

        return DocumentMetadataDto(
            **documentMetadata,
        )

    # ------------------------------------------------------
    # Invalid JSON
    # ------------------------------------------------------

    except json.JSONDecodeError as exception:
        logger.exception(
            INVALID_METADATA_JSON_ERROR,
        )

        raise InvalidMetadataException(
            INVALID_METADATA_JSON_ERROR,
        ) from exception

    # ------------------------------------------------------
    # Known Exceptions
    # ------------------------------------------------------

    except (
        InvalidMetadataException,
        LLMResponseException,
    ):
        raise

    # ------------------------------------------------------
    # Unexpected Exceptions
    # ------------------------------------------------------

    except Exception as exception:
        logger.exception(
            METADATA_EXTRACTION_FAILED_ERROR,
            exception,
        )

        raise MetadataExtractionException(
            METADATA_EXTRACTION_FAILED_ERROR,
        ) from exception
