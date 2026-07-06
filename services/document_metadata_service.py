import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from common.custom_exceptions import ValidationException
from common.logger import logger

from configuration.app_settings import LLM_MODEL
from configuration.context import DOCUMENT_METADATA_PROMPT

load_dotenv()

_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    """Return the singleton LLM instance."""

    global _llm

    if _llm is None:
        _llm = ChatOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model=LLM_MODEL,
            temperature=0,
        )

    return _llm

# ==========================================================
# Extract Metadata
# ==========================================================

def extract_document_metadata(text: str) -> dict[str, Any]:
    """Extract document metadata using the configured LLM."""

    try:
        if not text.strip():
            raise ValidationException(
                "Document text cannot be empty."
            )

        logger.info("Extracting document metadata.")

        prompt = DOCUMENT_METADATA_PROMPT.format(
            text=text[:4000]
        )

        response = get_llm().invoke(prompt)

        content = re.sub(
            r"^```json|```$",
            "",
            response.content.strip(),
            flags=re.MULTILINE,
        ).strip()

        metadata = json.loads(content)

        logger.info("Metadata extracted successfully.")

        return metadata

    except json.JSONDecodeError as ex:
        logger.exception(
            "Invalid metadata JSON returned by LLM."
        )

        raise ValidationException(
            "Invalid JSON returned by the LLM."
        ) from ex

    except ValidationException:
        raise

    except Exception as ex:
        logger.exception(
            "Metadata extraction failed: %s",
            ex,
        )

        raise ValidationException(
            "Unable to extract document metadata."
        ) from ex