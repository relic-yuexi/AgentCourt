# api_client/zhipuai_client.py
import requests
import json
from .base_client import BaseClient
from typing import List, Dict, Optional, Union


class ZhipuAIClient(BaseClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def send_request(
        self,
        messages: List[Dict[str, str]],
        request_id: Optional[str] = None,
        do_sample: bool = True,
        stream: bool = False,
        temperature: float = 0.95,
        top_p: float = 0.7,
        max_tokens: int = 1024,
        stop: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        tool_choice: Union[str, Dict] = "auto",
        user_id: Optional[str] = None,
        *args,
        **kwargs,
    ) -> str:
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "request_id": request_id,
            "do_sample": do_sample,
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stop": stop,
            "tools": tools,
            "tool_choice": tool_choice,
            "user_id": user_id,
        }
        # 移除值为 None 的参数
        payload = {k: v for k, v in payload.items() if v is not None}

        # 参数类型检查
        assert isinstance(self.model, str), "model must be a string"
        assert isinstance(messages, list), "messages must be a list"
        assert all(
            isinstance(msg, dict) for msg in messages
        ), "each message must be a dictionary"
        assert all(
            "role" in msg and "content" in msg for msg in messages
        ), "each message must have 'role' and 'content' keys"
        assert request_id is None or isinstance(
            request_id, str
        ), "request_id must be a string or None"
        assert isinstance(do_sample, bool), "do_sample must be a boolean"
        assert isinstance(stream, bool), "stream must be a boolean"
        assert isinstance(temperature, (int, float)), "temperature must be a number"
        assert 0 < temperature < 1, "temperature must be between 0 and 1"
        assert isinstance(top_p, (int, float)), "top_p must be a number"
        assert 0 < top_p < 1, "top_p must be between 0 and 1"
        assert isinstance(max_tokens, int), "max_tokens must be an integer"
        assert max_tokens > 0, "max_tokens must be positive"
        assert stop is None or isinstance(stop, list), "stop must be a list or None"
        assert tools is None or isinstance(tools, list), "tools must be a list or None"
        assert isinstance(
            tool_choice, (str, dict)
        ), "tool_choice must be a string or dictionary"
        assert user_id is None or isinstance(
            user_id, str
        ), "user_id must be a string or None"

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        text = json.loads(response.text)
        return text.get("choices")[0].get("message").get("content")
