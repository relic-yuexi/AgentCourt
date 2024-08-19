# LLM/llm.py:
from abc import ABC, abstractmethod
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer


class LLM(ABC):
    @abstractmethod
    def generate(self, prompt,*args, **kwargs):
        pass
