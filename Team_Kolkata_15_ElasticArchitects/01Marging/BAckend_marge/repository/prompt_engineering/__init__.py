# repository/prompt_engineering/__init__.py
"""
Prompt engineering module initialization.
"""

from repository.prompt_engineering.templates import (
    DiseaseDetectionPrompts,
    PromptChain
)

# Remove these for now to avoid circular import issues
# from repository.prompt_engineering.few_shot import FewShotExamples
# from repository.prompt_engineering.chain import PromptChainExecutor

__all__ = [
    'DiseaseDetectionPrompts',
    'PromptChain'
]
