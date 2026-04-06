# repository/prompt_engineering/chain.py
"""
Prompt chaining utilities for multi-step reasoning.
"""

from typing import List, Dict, Any


class PromptChainExecutor:
    """Execute a chain of prompts sequentially"""
    
    def __init__(self, llm_client=None):
        """
        Initialize chain executor.
        
        Args:
            llm_client: LLM client instance (optional, can be set later)
        """
        self.client = llm_client
        self.results = []
    
    async def execute_chain(
        self,
        chain: List[Dict],
        context: Dict = None
    ) -> List[Dict]:
        """
        Execute a chain of prompts with context passing.
        
        Args:
            chain: List of prompt steps with 'step' and 'prompt' keys
            context: Optional initial context
        
        Returns:
            List of results from each step
        """
        if not self.client:
            raise ValueError("LLM client not set. Initialize with client or set self.client")
        
        context = context or {}
        results = []
        
        for step_config in chain:
            step_name = step_config.get('step', 'unknown')
            prompt = step_config.get('prompt', '')
            
            # Inject context into prompt if needed
            if context:
                prompt = self._inject_context(prompt, context)
            
            # Execute step
            response = await self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = {
                "step": step_name,
                "response": response.choices[0].message.content
            }
            
            results.append(result)
            
            # Update context for next step
            context[step_name] = result['response']
        
        return results
    
    def _inject_context(self, prompt: str, context: Dict) -> str:
        """Inject context variables into prompt"""
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        return prompt
