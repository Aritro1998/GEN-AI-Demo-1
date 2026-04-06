# repository/prompt_engineering/few_shot.py
"""
Few-shot examples for improving LLM accuracy.
"""

from typing import List, Dict


class FewShotExamples:
    """Few-shot examples for disease detection"""
    
    @staticmethod
    def get_disease_detection_examples() -> List[Dict]:
        """Get example disease detections for few-shot learning"""
        return [
            {
                "input": "Image shows tomato leaf with brown spots surrounded by yellow halos",
                "output": {
                    "disease": "Early Blight",
                    "disease_category": "blight",
                    "confidence": 0.92,
                    "severity_level": 2,
                    "severity_description": "Moderate",
                    "infection_percentage": 25,
                    "visual_symptoms": [
                        "Brown concentric rings on leaves",
                        "Yellow halo around lesions",
                        "Lower leaves affected first"
                    ],
                    "affected_areas": "Lower and middle leaves, approximately 25% coverage",
                    "disease_stage": "mid"
                }
            },
            {
                "input": "Image shows wheat leaf with orange pustules",
                "output": {
                    "disease": "Wheat Rust",
                    "disease_category": "rust",
                    "confidence": 0.95,
                    "severity_level": 3,
                    "severity_description": "Severe",
                    "infection_percentage": 45,
                    "visual_symptoms": [
                        "Orange-brown pustules on leaf surface",
                        "Pustules releasing spores",
                        "Leaf tissue yellowing"
                    ],
                    "affected_areas": "Both leaf surfaces, scattered throughout, 45% coverage",
                    "disease_stage": "advanced"
                }
            },
            {
                "input": "Image shows healthy green rice leaf",
                "output": {
                    "disease": "Healthy",
                    "disease_category": "healthy",
                    "confidence": 0.98,
                    "severity_level": 0,
                    "severity_description": "None",
                    "infection_percentage": 0,
                    "visual_symptoms": [],
                    "affected_areas": "No affected areas observed",
                    "disease_stage": "early"
                }
            }
        ]
    
    @staticmethod
    def format_few_shot_prompt(base_prompt: str, examples: List[Dict]) -> str:
        """Format prompt with few-shot examples"""
        examples_text = "\n\n**Examples:**\n"
        for i, example in enumerate(examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Input: {example['input']}\n"
            examples_text += f"Output: {example['output']}\n"
        
        return base_prompt + examples_text
