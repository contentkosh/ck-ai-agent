import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common.logger import logger
from configuration.config import (
    LLM_MAX_NEW_TOKENS,
    LLM_MODEL_NAME,
    LLM_REPETITION_PENALTY,
)

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / LLM_MODEL_NAME

_llm = None
_tokenizer = None
_device = None


class LocalLLM:
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def invoke(self, prompt: str):
        start_time = time.perf_counter()

        logger.info(
            "LLM generation started. Model=%s | device=%s",
            LLM_MODEL_NAME,
            self.device,
        )

        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]

            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            )

            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            input_length = inputs["input_ids"].shape[-1]

            logger.info(
                "LLM input prepared. Tokens=%d",
                input_length,
            )

            logger.info(
                "LLM model generation started. Max new tokens=%d",
                LLM_MAX_NEW_TOKENS,
            )

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=LLM_MAX_NEW_TOKENS,
                    do_sample=False,
                    repetition_penalty=LLM_REPETITION_PENALTY,
                )

            output_length = outputs[0].shape[-1]
            generated_tokens = max(
                output_length - input_length,
                0,
            )

            answer = self.tokenizer.decode(
                outputs[0][input_length:],
                skip_special_tokens=True,
            )

            response = type("LLMResponse", (), {})()
            response.content = answer.strip()

            duration = time.perf_counter() - start_time

            logger.info(
                "LLM generation completed. Generated tokens=%d | duration=%.3fs",
                generated_tokens,
                duration,
            )

            return response

        except Exception:
            duration = time.perf_counter() - start_time

            logger.exception(
                "LLM generation failed. Duration=%.3fs",
                duration,
            )
            raise


def get_llm():
    global _llm, _tokenizer, _device

    if _llm is not None:
        return _llm

    _device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(
        "Local LLM initialization started. Model=%s | device=%s",
        LLM_MODEL_NAME,
        _device,
    )

    if not MODEL_PATH.exists():
        logger.error(
            "Local LLM model not found: %s",
            MODEL_PATH,
        )
        raise FileNotFoundError(f"Local LLM model not found: {MODEL_PATH}")

    try:
        logger.info(
            "Loading tokenizer for local LLM '%s'.",
            LLM_MODEL_NAME,
        )

        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            local_files_only=True,
        )

        logger.info(
            "Tokenizer loaded successfully.",
        )

        logger.info(
            "Loading local LLM model '%s'.",
            LLM_MODEL_NAME,
        )

        if _device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                device_map="auto",
                dtype=torch.bfloat16,
                local_files_only=True,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                dtype=torch.float32,
                local_files_only=True,
            )
            model.to(_device)

        logger.info(
            "Local LLM model loaded successfully.",
        )

        model.eval()

        _llm = LocalLLM(
            model=model,
            tokenizer=_tokenizer,
            device=_device,
        )

        logger.info(
            "Local LLM '%s' initialized successfully on %s.",
            LLM_MODEL_NAME,
            _device,
        )

        return _llm

    except Exception:
        logger.exception(
            "Local LLM initialization failed. Model=%s | device=%s",
            LLM_MODEL_NAME,
            _device,
        )
        raise
