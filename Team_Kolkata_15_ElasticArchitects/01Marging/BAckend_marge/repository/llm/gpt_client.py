# repository/llm/gpt_client.py
"""
Custom OpenAI-compatible LLM client using LangChain.
Supports custom base_url and SSL bypass.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from langchain_openai import ChatOpenAI
    import httpx
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    raise ImportError("Required packages not installed. Run: pip install langchain-openai httpx")


class AzureAIClient:
    """
    Custom LLM client using LangChain ChatOpenAI.
    Works with OpenAI-compatible endpoints.
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: str = "2024-02-15-preview"
    ):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("langchain-openai and httpx required. Run: pip install langchain-openai httpx")
        
        # Load configuration
        self.base_url = endpoint or os.getenv("api_endpoint")
        self.api_key = api_key or os.getenv("api_key")
        self.model = model
        
        # Validate configuration
        if not self.base_url:
            raise ValueError("api_endpoint not found. Set it in .env file.")
        
        if not self.api_key:
            raise ValueError("api_key not found. Set it in .env file.")
        
        # Create HTTP client with SSL verification disabled
        self.http_client = httpx.Client(verify=False)
        
        # Initialize LangChain ChatOpenAI
        try:
            self.llm = ChatOpenAI(
                base_url=self.base_url,
                model=self.model,
                api_key=self.api_key,
                http_client=self.http_client,
                temperature=0.7
            )
            print(f"✓ LLM client initialized")
            print(f"  - Endpoint: {self.base_url}")
            print(f"  - Model: {self.model}")
        except Exception as e:
            raise ValueError(f"Failed to initialize LLM client: {str(e)}")
    
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """
        Generate chat completion using LangChain ChatOpenAI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            response_format: Optional format specification
        
        Returns:
            Response object compatible with OpenAI format
        """
        try:
            # Update temperature if different
            if temperature != 0.7:
                self.llm.temperature = temperature
            
            if max_tokens:
                self.llm.max_tokens = max_tokens
            
            print(f"[LLM] Calling {self.model}...")
            
            # Convert messages to LangChain format
            if len(messages) == 1 and messages[0].get('role') == 'user':
                # Simple prompt
                prompt = messages[0].get('content')
                if isinstance(prompt, list):
                    # Extract text from multimodal content
                    prompt = ' '.join([
                        item.get('text', '') 
                        for item in prompt 
                        if item.get('type') == 'text'
                    ])
            else:
                # Multiple messages - concatenate
                prompt = '\n'.join([
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in messages
                ])
            
            # Call LLM
            response = self.llm.invoke(prompt)
            
            print(f"[LLM] ✓ Response received")
            
            # Convert LangChain response to OpenAI-compatible format
            return self._convert_to_openai_format(response)
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            print(f"[LLM] ✗ Call failed: {error_type}")
            print(f"[LLM] Error: {error_msg}")
            
            raise Exception(f"LLM call failed: {error_msg}")
    
    def _convert_to_openai_format(self, langchain_response) -> Any:
        """Convert LangChain response to OpenAI format"""
        
        # Extract content from LangChain response
        if hasattr(langchain_response, 'content'):
            content = langchain_response.content
        else:
            content = str(langchain_response)
        
        # Create OpenAI-compatible response object
        class OpenAIResponse:
            def __init__(self, content):
                self.choices = [OpenAIChoice(content)]
                self.usage = {"total_tokens": 0}
        
        class OpenAIChoice:
            def __init__(self, content):
                self.message = OpenAIMessage(content)
                self.finish_reason = "stop"
        
        class OpenAIMessage:
            def __init__(self, content):
                self.content = content
                self.role = "assistant"
        
        return OpenAIResponse(content)
    
    async def embedding(self, text: str) -> List[float]:
        """Generate embeddings (if supported by your endpoint)"""
        raise NotImplementedError("Embedding not implemented for custom endpoint")
    
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'http_client'):
            self.http_client.close()


class GPTClient(AzureAIClient):
    """Alias for backward compatibility"""
    pass


def create_llm_client(
    model: str,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None
) -> AzureAIClient:
    """Create LLM client"""
    return AzureAIClient(model=model, api_key=api_key, endpoint=endpoint)
