from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "LFM2.5-1.2B-Instruct"
)


print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("CUDA version:", torch.version.cuda)
else:
    print("GPU: None")


print("\nLoading tokenizer...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
)


print("Loading model...")

device = "cuda" if torch.cuda.is_available() else "cpu"

if device == "cuda":
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
    model.to(device)

model.eval()

print("\nModel loaded!")
print("Model device:", model.device)

if torch.cuda.is_available():
    print(
        "GPU memory allocated:",
        round(torch.cuda.memory_allocated() / 1024**3, 2),
        "GB",
    )


messages = [
    {
        "role": "user",
        "content": "What is Artificial Intelligence? Explain in two sentences.",
    }
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
)

inputs = {
    key: value.to(model.device)
    for key, value in inputs.items()
}


print("\nGenerating answer...")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=False,
        repetition_penalty=1.05,
    )


input_length = inputs["input_ids"].shape[-1]

answer = tokenizer.decode(
    outputs[0][input_length:],
    skip_special_tokens=True,
)


print("\n--- LFM ANSWER ---")
print(answer)

if torch.cuda.is_available():
    print(
        "\nGPU memory after generation:",
        round(torch.cuda.memory_allocated() / 1024**3, 2),
        "GB",
    )