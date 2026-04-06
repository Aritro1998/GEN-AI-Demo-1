# repository/llm/base.py
"""
Base class for LLM clients with common interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    async def embedding(self, text: str) -> List[float]:
        """Generate text embeddings"""
        pass


class LLMResponse:
    """Standardized LLM response wrapper"""
    
    def __init__(self, content: str, model: str, usage: Optional[Dict] = None):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.choices = [type('obj', (object,), {
            'message': type('obj', (object,), {'content': content})()
        })()]
