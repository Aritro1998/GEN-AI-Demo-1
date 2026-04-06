# repository/llm/utils.py
"""
Utility functions for LLM operations.
"""

import tiktoken
from typing import List, Dict
import re


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text for given model.
    
    Args:
        text: Text to count tokens for
        model: Model name for tokenizer
    
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to approximate counting
        return len(text.split()) * 1.3


def count_messages_tokens(messages: List[Dict], model: str = "gpt-4") -> int:
    """
    Count tokens in message list.
    
    Args:
        messages: List of message dicts
        model: Model name
    
    Returns:
        Total token count
    """
    total = 0
    for message in messages:
        total += count_tokens(str(message.get('content', '')), model)
        total += 4  # Message overhead
    return total + 2  # Conversation overhead


def truncate_text(text: str, max_tokens: int, model: str = "gpt-4") -> str:
    """
    Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed
        model: Model name
    
    Returns:
        Truncated text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return encoding.decode(tokens[:max_tokens])
    except Exception:
        # Fallback to character-based truncation
        estimated_chars = int(max_tokens * 4)  # ~4 chars per token
        return text[:estimated_chars]


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON object from text that may contain markdown or other content.
    
    Args:
        text: Text potentially containing JSON
    
    Returns:
        Extracted JSON string
    """
    # Try to find JSON between ``````
    json_match = re.search(r'``````', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find JSON between { and }
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return text


def clean_llm_response(text: str) -> str:
    """
    Clean LLM response by removing markdown artifacts.
    
    Args:
        text: Raw LLM response
    
    Returns:
        Cleaned text
    """
    # Remove markdown code blocks
    text = re.sub(r'```', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text
