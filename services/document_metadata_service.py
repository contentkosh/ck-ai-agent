# ==========================================================
# Document Metadata Service
# Provides utilities to initialize the LLM and extract
# structured document metadata from raw text using prompts.
# ==========================================================

import json
import re
from typing import Any

from dotenv import load_dotenv

from common.llm_client import get_llm
from common.logger import logger

from configuration.config import (
    METADATA_EXTRACTION_TEXT_LIMIT,
)

from configuration.constants import (
    EMPTY_DOCUMENT_TEXT_ERROR,
    INVALID_METADATA_JSON_ERROR,
    METADATA_EXTRACTION_FAILED_ERROR,
)

from configuration.context import (
    DOCUMENT_METADATA_EXTRACTION_PROMPT,
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
) -> dict[str, Any]:
    """
    Extract document metadata using the configured LLM.
    """
    try:
        if not text.strip():
            raise InvalidMetadataException(
                EMPTY_DOCUMENT_TEXT_ERROR,
            )

        logger.info("Extracting document metadata.")

        prompt = DOCUMENT_METADATA_EXTRACTION_PROMPT.format(
            text=text[:METADATA_EXTRACTION_TEXT_LIMIT]
        )

        response = get_llm().invoke(prompt)

        content = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response.content.strip(),
            flags=re.MULTILINE,
        ).strip()

        metadata = json.loads(content)

        logger.info("Metadata extracted successfully.")

        return metadata

    except json.JSONDecodeError as ex:
        logger.exception(
            INVALID_METADATA_JSON_ERROR,
        )

        raise InvalidMetadataException(
            INVALID_METADATA_JSON_ERROR,
        ) from ex

    except InvalidMetadataException:
        raise

    except Exception as ex:
        logger.exception(
            "Metadata extraction failed: %s",
            ex,
        )

        raise MetadataExtractionException(
            METADATA_EXTRACTION_FAILED_ERROR,
        ) from ex