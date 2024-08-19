# api_client/wenxin_client.py
import requests
import json
from .base_client import BaseClient
import time


class WenxinClient(BaseClient):
    def __init__(self, api_key, api_secret, model):
        self.api_key = api_key
        self.api_secret = api_secret
        self.model = model

    def get_access_token(self):
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(url, headers=headers)
        return response.json().get("access_token")

    def send_request(
        self,
        messages,
        temperature=0.8,
        top_p=0.8,
        penalty_score=1.0,
        stream=False,
        enable_system_memory=False,
        system_memory_id=None,
        stop=None,
        disable_search=False,
        enable_citation=False,
        enable_trace=False,
        max_output_tokens: int = None,
        response_format=None,
        user_id=None,
        tool_choice=None,
        *args,
        **kwargs,
    ):

        access_token = self.get_access_token()
        if self.model == "ERNIE-4.0-8K":
            endpoint = "completions_pro"
        elif self.model == "ERNIE-Speed-128K":
            endpoint = "ernie-speed-128k"
        elif self.model == "ERNIE-3.5-8K":
            endpoint = "completions"
        else:
            raise ValueError("Invalid model name")

        base_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{endpoint}?access_token={access_token}"
        headers = {"Content-Type": "application/json"}

        system_messages = [msg for msg in messages if msg["role"] == "system"]
        if system_messages:
            system = system_messages[0]["content"]
            messages = [msg for msg in messages if msg["role"] != "system"]
        else:
            system = None

        payload = {
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "penalty_score": penalty_score,
            "stream": stream,
            "enable_system_memory": enable_system_memory,
            "disable_search": disable_search,
            "enable_citation": enable_citation,
            "enable_trace": enable_trace,
            "response_format": response_format,
        }

        if system:
            payload["system"] = system
        if system_memory_id:
            payload["system_memory_id"] = system_memory_id
        if stop:
            payload["stop"] = stop
        if max_output_tokens:
            payload["max_output_tokens"] = max_output_tokens
        if user_id:
            payload["user_id"] = user_id
        if tool_choice:
            payload["tool_choice"] = tool_choice

        response = requests.post(base_url, headers=headers, data=json.dumps(payload))

        # 处理速率限制
        if response.status_code == 429:
            print("警告:请求速率超过限制!")
            remaining_requests = int(
                response.headers.get("X-Ratelimit-Remaining-Requests", 0)
            )
            remaining_tokens = int(
                response.headers.get("X-Ratelimit-Remaining-Tokens", 0)
            )
            if remaining_requests == 0 or remaining_tokens == 0:
                sleep_time = 60  # 休眠60秒再重试
                print(f"配额已用尽,{sleep_time}秒后重试...")
                time.sleep(sleep_time)
                return self.send_request(
                    messages,
                    temperature,
                    top_p,
                    penalty_score,
                    stream,
                    enable_system_memory,
                    system_memory_id,
                    stop,
                    disable_search,
                    enable_citation,
                    enable_trace,
                    max_output_tokens,
                    response_format,
                    user_id,
                    tool_choice,
                )

        text = json.loads(response.text)
        print(text)

        if "result" not in text:
            print("警告:响应中未找到result字段!")
            return ""

        result = text["result"]

        if text.get("is_truncated"):
            print("注意:输出结果被截断!")

        if text.get("function_call"):
            print("模型生成了函数调用:")
            print(text["function_call"])

        return result
