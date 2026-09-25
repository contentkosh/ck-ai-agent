import json
import re
from dotenv import load_dotenv

from common.llm_client import get_llm
from common.logger import logger
from configuration.config import METADATA_EXTRACTION_TEXT_LIMIT
from configuration.constants import (
    LLM_INVOCATION_FAILED_LOG,
    MARKDOWN_JSON_REGEX,
    METADATA_EXTRACTION_COMPLETED_LOG,
    METADATA_EXTRACTION_STARTED_LOG,
)
from configuration.context import DOCUMENT_METADATA_EXTRACTION_PROMPT
from configuration.error_constants import (
    EMPTY_DOCUMENT_TEXT_ERROR,
    INVALID_METADATA_JSON_ERROR,
    METADATA_EXTRACTION_FAILED_ERROR,
)
from dto.document_metadata_dto import DocumentMetadataDto
from exceptions.llm_exception import LLMResponseException
from exceptions.metadata_exception import (
    InvalidMetadataException,
    MetadataExtractionException,
)

load_dotenv()


def extract_first_json_object(response_content: str) -> dict:
    cleaned_content = re.sub(
        MARKDOWN_JSON_REGEX, "", response_content.strip(), flags=re.MULTILINE
    ).strip()
    json_start = cleaned_content.find("{")

    if json_start == -1:
        raise json.JSONDecodeError("No JSON object found.", cleaned_content, 0)

    decoder = json.JSONDecoder()
    document_metadata, _ = decoder.raw_decode(cleaned_content, json_start)

    if not isinstance(document_metadata, dict):
        raise json.JSONDecodeError(
            "Metadata JSON must be an object.", cleaned_content, json_start
        )

    if "metadata" in document_metadata:
        nested_metadata = document_metadata["metadata"]

        if not isinstance(nested_metadata, dict):
            raise json.JSONDecodeError(
                "Metadata field must contain an object.", cleaned_content, json_start
            )

        document_metadata = nested_metadata

    required_fields = {"title", "document_type", "tag", "summary"}
    missing_fields = required_fields.difference(document_metadata.keys())

    if missing_fields:
        raise json.JSONDecodeError(
            "Metadata JSON is missing required fields.", cleaned_content, json_start
        )

    empty_fields = [
        field
        for field in required_fields
        if not isinstance(document_metadata.get(field), str)
        or not document_metadata[field].strip()
    ]

    if empty_fields:
        raise InvalidMetadataException(
            "Metadata fields cannot be empty: " + ", ".join(sorted(empty_fields))
        )

    return document_metadata


def extract_document_metadata(text: str) -> DocumentMetadataDto:
    try:
        if not text.strip():
            raise InvalidMetadataException(EMPTY_DOCUMENT_TEXT_ERROR)

        logger.info(METADATA_EXTRACTION_STARTED_LOG)
        logger.info("Metadata extraction input prepared. Characters=%d", len(text))

        prompt = DOCUMENT_METADATA_EXTRACTION_PROMPT.format(
            text=text[:METADATA_EXTRACTION_TEXT_LIMIT]
        )
        logger.info("Metadata extraction prompt prepared. Characters=%d", len(prompt))

        try:
            logger.info("Metadata LLM invocation started.")
            llm_response = get_llm().invoke(prompt)
            logger.info(
                "Metadata LLM invocation completed. Response characters=%d",
                len(llm_response.content),
            )
        except Exception as exception:
            logger.exception(LLM_INVOCATION_FAILED_LOG)
            raise LLMResponseException() from exception

        logger.info("Metadata JSON parsing started.")
        document_metadata = extract_first_json_object(llm_response.content)
        logger.info(
            "Metadata JSON parsing completed. Fields=%d", len(document_metadata)
        )

        metadata = DocumentMetadataDto(**document_metadata)
        logger.info(METADATA_EXTRACTION_COMPLETED_LOG)

        return metadata

    except json.JSONDecodeError as exception:
        logger.exception(INVALID_METADATA_JSON_ERROR)
        raise InvalidMetadataException(INVALID_METADATA_JSON_ERROR) from exception

    except (InvalidMetadataException, LLMResponseException):
        raise

    except Exception as exception:
        logger.exception(METADATA_EXTRACTION_FAILED_ERROR, exception)
        raise MetadataExtractionException(
            METADATA_EXTRACTION_FAILED_ERROR
        ) from exception
