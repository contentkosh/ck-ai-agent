from llmlingua import PromptCompressor

from common.logger import logger
from configuration.app_settings import (
    LLMLINGUA_DEVICE,
    LLMLINGUA_MODEL,
    LLMLINGUA_TARGET_TOKEN,
)

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
            model_name=LLMLINGUA_MODEL,
            use_llmlingua2=True,
            device_map=LLMLINGUA_DEVICE,
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
            target_token=LLMLINGUA_TARGET_TOKEN,
        )

        return result["compressed_prompt"]

    except Exception as ex:
        logger.exception("LLMLingua compression failed: %s", ex)
        # Fall back to original context
        return context