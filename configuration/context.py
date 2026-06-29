"""
Application Request Context
Stores request-specific data and all LLM prompts.
"""

import uuid
from contextvars import ContextVar


# ==========================================================
# REQUEST CONTEXT
# ==========================================================

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default=None
)


class RequestContext:
    """
    Handles request-specific information.
    """

    @staticmethod
    def generate_request_id() -> str:
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
        return request_id

    @staticmethod
    def get_request_id() -> str:
        return request_id_context.get()


# ==========================================================
# CHAT PROMPT
# ==========================================================

CHAT_PROMPT = """
You are an AI Knowledge Base Assistant.

Answer the user's question ONLY using the provided context.

Rules:

1. Use ONLY the provided context.
2. Do NOT use external knowledge.
3. If the answer is not present, reply exactly:

Answer not found in the Knowledge Base.

4. Keep the answer concise, accurate and professional.
5. Do not mention the context or explain your reasoning.

--------------------------------------------------

Context:

{context}

--------------------------------------------------

Question:

{query}

--------------------------------------------------

Answer:
"""


# ==========================================================
# DOCUMENT METADATA EXTRACTION PROMPT
# ==========================================================

DOCUMENT_METADATA_PROMPT = """
You are an intelligent document analyzer.

Analyze the following document.

Return ONLY valid JSON.

JSON format:

{{
    "title": "",
    "document_type": "",
    "tag": "",
    "summary": ""
}}

Rules:

1. title
   - Extract the main document title.

2. document_type
   Must be exactly one of:

   Book
   Research Paper
   Manual
   Policy
   Question Bank
   Notes
   Report
   Documentation
   Other

3. tag
   - Generate ONE semantic lowercase tag.

Examples:

artificial_intelligence
machine_learning
finance
healthcare
cloud_computing

4. summary
   - Maximum 30 words.

Document:

{text}
"""