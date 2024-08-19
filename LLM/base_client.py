# LLM/base_client.py
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseClient(ABC):
    @abstractmethod
    def send_request(self, messages: List[Dict[str, str]], *args, **kwargs):
        pass
