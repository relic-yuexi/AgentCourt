from .llm import LLM
from .openai_client import OpenAIClient
from .wenxin_client import WenxinClient
from .zhipuai_client import ZhipuAIClient


class APILLM(LLM):
    def __init__(self, api_key, api_secret=None, platform="wenxin", model="gpt-4"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.platform = platform
        self.model = model
        self.client = self._initialize_client()

    def _initialize_client(self):
        if self.platform == "openai":
            return OpenAIClient(self.api_key, self.model)
        elif self.platform == "wenxin":
            return WenxinClient(self.api_key, self.api_secret, self.model)
        elif self.platform == "zhipuai":
            return ZhipuAIClient(self.api_key, self.model)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")

    def generate(self, instruction, prompt, *args, **kwargs):
        if instruction is None:
            instruction = "You are a helpful assistant."

        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ]
        return self.client.send_request(messages, *args, **kwargs)
