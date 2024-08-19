# api_client/openai_client.py
import requests
import json
from .base_client import BaseClient


class OpenAIClient(BaseClient):
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def send_request(self, messages):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        text = json.loads(response.text)
        return text.get("choices")[0].get("message").get("content")
