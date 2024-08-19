from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from .llm import LLM
import torch


class OfflineLLM(LLM):
    def __init__(self, model_path, device="cuda"):
        self.pipe = pipeline(
            "text-generation",
            model=model_path,
            torch_dtype=torch.float16,
            device_map=device,
        )

    def generate(self, instruction, prompt, max_new_tokens=500):

        if instruction is None:
            instruction = "You are a helpful assistant."

        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ]

        response = self.pipe(messages, max_new_tokens=max_new_tokens)
        return response[0]["generated_text"][-1]["content"]
