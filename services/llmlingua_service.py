from llmlingua import PromptCompressor
from common.logger import logger

# ==========================================================
# LLMLingua-2 Compressor Singleton
# ==========================================================

_compressor: PromptCompressor | None = None


def get_compressor() -> PromptCompressor:
    """
    Return the singleton LLMLingua-2 compressor.
    """
    global _compressor

    if _compressor is None:
        logger.info("Loading LLMLingua-2 compressor...")

        _compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True,
            device_map="cuda:0",
        )

    return _compressor


# ==========================================================
# Compress Context
# ==========================================================

def compress_context(
    *,
    context: str,
    query: str,
) -> str:
    """
    Compress retrieved context before sending it to the LLM.
    """
    try:
        compressor = get_compressor()

        result = compressor.compress_prompt(
            context=[context],
            instruction=query,
            use_context_level_filter=True,
            target_token=512,
        )

        return result["compressed_prompt"]

    except Exception as ex:
        logger.exception("LLMLingua compression failed: %s",ex)
        # Fall back to original context
        return context