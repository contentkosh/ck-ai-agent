import json
import os
import re

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from configuration.app_settings import LLM_MODEL

from common.logger import logger
from common.custom_exceptions import ValidationException

load_dotenv()


# ==========================================================
# LLM
# ==========================================================

llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model=LLM_MODEL,
    temperature=0
)


# ==========================================================
# Extract Metadata
# ==========================================================

def extract_document_metadata(text: str) -> dict:
    """
    Extract document metadata using the LLM.
    """

    try:

        if not text.strip():

            raise ValidationException(
                "Document text cannot be empty."
            )

        prompt = f"""
You are an intelligent document classifier.

Return ONLY valid JSON.

Format:

{{
    "title":"",
    "document_type":"",
    "tag":"",
    "summary":""
}}

Rules:

- No markdown
- No explanation
- Only JSON

Document:

{text[:4000]}
"""

        logger.info(
            "Calling metadata extraction LLM."
        )

        response = llm.invoke(prompt)

        content = response.content.strip()

        # Remove markdown if present

        content = re.sub(
            r"^```json|```$",
            "",
            content,
            flags=re.MULTILINE
        ).strip()

        metadata = json.loads(content)

        logger.info(
            "Metadata extracted successfully."
        )

        return metadata

    except Exception as e:

        logger.exception(
            "Metadata extraction failed."
        )

        raise ValidationException(
            f"Unable to extract metadata. {str(e)}"
        )