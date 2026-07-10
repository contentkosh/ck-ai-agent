"""
Application Request Context

Stores request-specific data and centralized LLM prompts
used throughout the Knowledge Base application.
"""
import uuid
from contextvars import ContextVar

# ==========================================================
# REQUEST CONTEXT
# ==========================================================

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default=None,
)
class RequestContext:
    """
    Manages request-specific information throughout the
    application lifecycle.
    """

    def __init__(self) -> None:
        self.request_id = self.generate_request_id()

    @staticmethod
    def generate_request_id() -> str:
        """
        Generate and store a unique request ID.
        """

        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)

        return request_id

    @staticmethod
    def get_request_id() -> str:
        """
        Return the current request ID.
        """

        return request_id_context.get()

# ==========================================================
# KNOWLEDGE BASE QUESTION ANSWERING PROMPT
# ==========================================================

KNOWLEDGE_BASE_QA_PROMPT = """
You are an AI Knowledge Base Assistant.

Your responsibility is to answer user questions ONLY using
the information available in the provided Knowledge Base context.

==================================================
INSTRUCTIONS
==================================================

1. Use ONLY the provided Knowledge Base context.

2. Do NOT use:
   - External knowledge
   - Prior training knowledge
   - Assumptions
   - Personal opinions
   - Fabricated information

3. If the answer cannot be found completely or confidently
   from the provided context, respond EXACTLY with:

Answer not found in the Knowledge Base.

4. Never guess or infer missing information.

5. If multiple context sections are provided,
   combine only the relevant information required
   to answer the user's question.

6. Ignore irrelevant context.

7. Keep the response:

   - Accurate
   - Concise
   - Professional
   - Grammatically correct

8. Do NOT include statements such as:

   - According to the context...
   - Based on the provided information...
   - The context states...
   - I think...
   - My reasoning...

9. Return only the final answer.

==================================================
KNOWLEDGE BASE CONTEXT
==================================================

{context}

==================================================
USER QUESTION
==================================================

{query}

==================================================
FINAL ANSWER
==================================================
"""
# ==========================================================
# DOCUMENT METADATA EXTRACTION PROMPT
# ==========================================================

DOCUMENT_METADATA_EXTRACTION_PROMPT = """
You are an intelligent document metadata extraction assistant.

Analyze the provided document and extract structured metadata
that will be stored in the Knowledge Base.

Return ONLY valid JSON.

Do NOT return markdown, explanations, comments,
or any additional text.

==================================================
OUTPUT FORMAT
==================================================

{{
    "title": "",
    "document_type": "",
    "tag": "",
    "summary": ""
}}

==================================================
FIELD DEFINITIONS
==================================================

1. title

- Extract the primary title of the document.
- Remove unnecessary prefixes or suffixes.
- If no title exists, return:

Unknown

--------------------------------------------------

2. document_type

Return EXACTLY one of the following values:

Book
Research Paper
Manual
Policy
Question Bank
Notes
Report
Documentation
Other

Do not generate any custom document type.

--------------------------------------------------

3. tag

Generate ONE semantic tag representing the
main topic of the document.

Rules:

- lowercase only
- use underscores instead of spaces
- maximum three words
- no special characters
- no punctuation

Examples:

artificial_intelligence
machine_learning
deep_learning
cloud_computing
finance
healthcare
cyber_security

If no meaningful tag can be generated, return:

general

--------------------------------------------------

4. summary

Generate a concise summary.

Rules:

- Maximum 30 words
- Describe only the main purpose
- Do not repeat the title
- Do not include opinions
- Use complete English sentences

==================================================
GENERAL RULES
==================================================

1. Analyze the entire document before extracting metadata.

2. Do not hallucinate information.

3. If information is unavailable,
   return the closest valid value according
   to the rules above.

4. Ensure the response is valid JSON.

5. Do not wrap the JSON inside markdown.

6. Do not return any explanation before or after the JSON.

==================================================
DOCUMENT
==================================================

{text}
"""