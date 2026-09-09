from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from common.logger import logger
from configuration.config import (
    LLM_MAX_NEW_TOKENS,
    LLM_REPETITION_PENALTY,
)

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "LFM2.5-1.2B-Instruct"
)

_llm = None
_tokenizer = None
_device = None


class LocalLFM:
    def __init__(self, model, tokenizer, device):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def invoke(self, prompt: str):
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

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=LLM_MAX_NEW_TOKENS,
                do_sample=False,
                repetition_penalty=LLM_REPETITION_PENALTY,
            )

        input_length = inputs["input_ids"].shape[-1]

        answer = self.tokenizer.decode(
            outputs[0][input_length:],
            skip_special_tokens=True,
        )

        response = type("LLMResponse", (), {})()
        response.content = answer.strip()

        return response


def get_llm():
    global _llm, _tokenizer, _device

    if _llm is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"

        if not MODEL_PATH.exists():
            logger.error(
                "Local LFM model not found: %s",
                MODEL_PATH,
            )
            raise FileNotFoundError(
                f"Local LFM model not found: {MODEL_PATH}"
            )

        logger.info(
            "Loading local LFM model on %s.",
            _device,
        )

        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            local_files_only=True,
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

        model.eval()

        _llm = LocalLFM(
            model=model,
            tokenizer=_tokenizer,
            device=_device,
        )

        logger.info(
            "Local LFM model loaded successfully on %s.",
            _device,
        )

    return _llm