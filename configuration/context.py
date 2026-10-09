import uuid
from contextvars import ContextVar

request_id_context: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)


class RequestContext:
    """
    Manages request-specific information throughout the
    application lifecycle.
    """

    def __init__(self) -> None:
        request_id = self.get_request_id()

        if request_id is None:
            request_id = self.generate_request_id()

        self.request_id = request_id

    @staticmethod
    def generate_request_id() -> str:
        """
        Generate and store a unique request ID.
        """
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
        return request_id

    @staticmethod
    def get_request_id() -> str | None:
        """
        Return the current request ID.
        """
        return request_id_context.get()


KNOWLEDGE_BASE_QA_PROMPT = """
Answer the question using ONLY the supplied Knowledge Base context.

Rules:
- Never use outside knowledge, assumptions, or invented facts.
- Answer the exact question using directly supported information.
- Combine relevant context sections when necessary; ignore irrelevant ones.
- If the answer is not completely supported by the context, reply exactly:
Answer not found in the Knowledge Base.
- Be concise, accurate, and professional.
- Return only the answer, without explanations about the context.

Context:
{context}

Question:
{query}

Answer:
"""

DOCUMENT_METADATA_EXTRACTION_PROMPT = """
Extract metadata from the document below. Return exactly one valid JSON
object with these string fields:

{{
  "title": "",
  "document_type": "",
  "tag": "",
  "summary": ""
}}

Rules:
- title: Main document title, or "Unknown" if unavailable.
- document_type: Exactly one of Book, Research Paper, Manual, Policy,
  Question Bank, Notes, Report, Documentation, Other.
- tag: One lowercase semantic tag, maximum three words, underscores
  instead of spaces, no punctuation. Use "general" if unavailable.
- summary: Complete English sentence, maximum 30 words, describing
  only the document's main purpose. Do not repeat the title or give opinions.
- Use only information supported by the document.
- Use double quotes for keys and string values. Escape internal quotes.
- Return JSON only: no Markdown, comments, or surrounding text.

Document:
{text}
"""
