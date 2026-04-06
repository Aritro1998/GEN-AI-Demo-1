# repository/ai_utils/token_counter.py
"""
Token counting utilities.
"""

from typing import List, Dict


class TokenCounter:
    """Utility for counting and managing tokens"""
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text.
        Rough approximation: 1 token ≈ 4 characters
        """
        return len(text) // 4
    
    @staticmethod
    def estimate_message_tokens(messages: List[Dict]) -> int:
        """Estimate tokens for message list"""
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, str):
                total += TokenCounter.estimate_tokens(content)
            elif isinstance(content, list):
                for item in content:
                    if item.get('type') == 'text':
                        total += TokenCounter.estimate_tokens(item['text'])
        return total + len(messages) * 4  # Message overhead
