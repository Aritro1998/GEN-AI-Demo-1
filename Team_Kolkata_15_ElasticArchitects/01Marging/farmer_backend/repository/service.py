# repository/service.py
"""
Main service orchestrator for plant disease detection system.
Coordinates LLM calls, image analysis, and recommendation generation.
Uses LangChain ChatOpenAI with custom endpoint.
NO FALLBACK RESPONSES - LLM ONLY.
"""

from repository.llm.gpt_client import AzureAIClient
from repository.prompt_engineering.templates import DiseaseDetectionPrompts
from repository.ai_utils.logger import AILogger
from repository.ai_utils.rate_limiter import RateLimiter
import json
import os
import re
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load model configurations from environment
MODEL_REASONING = os.getenv("MODEL_REASONING", "gpt-4-turbo-preview")
MODEL_HIGH_PERF = os.getenv("MODEL_HIGH_PERF", "gpt-4-turbo-preview")
MODEL_CHAT_MOD = os.getenv("MODEL_CHAT_MOD", "gpt-4o")


def extract_json_from_response(content: str) -> str:
    """
    Extract JSON from LLM response, handling reasoning model thinking tags and code blocks.
    """
    if not content:
        raise ValueError("Empty content received from LLM")
    print(f"[DEBUG] Raw content length: {len(content)}")
    # For reasoning models (DeepSeek-R1), look for content AFTER </think>
    if '</think>' in content:
        parts = content.split('</think>')
        if len(parts) > 1:
            content = parts[-1].strip()
            print(f"[DEBUG] Found </think> tag, content after: {len(content)} chars")
        else:
            print("[DEBUG] Found </think> but no content after it")
    # If still has incomplete <think> tag, the model didn't finish
    if '<think>' in content and '</think>' not in content:
        raise ValueError("Response cut off during thinking phase - increase max_tokens or switch to non-reasoning model")
    # Remove any remaining thinking tags
    think_pattern = r'<think>.*?</think>'
    content = re.sub(think_pattern, '', content, flags=re.DOTALL).strip()
    if not content:
        raise ValueError("No content found after removing thinking tags - model only provided reasoning, no answer")
    print(f"[DEBUG] Content after think tag removal: {content[:200]}")
    # Remove markdown code blocks (robust)
    if content.startswith('```'):
        # Remove all code block markers and leading/trailing whitespace
        content = re.sub(r'^```[a-zA-Z]*\n?', '', content)
        content = re.sub(r'```$', '', content)
        content = content.strip()
    # If content is already valid JSON, return it directly
    if content.startswith('{') and content.endswith('}'):
        return content
    # Find JSON object
    json_obj_pattern = r'\{.*\}'
    match = re.search(json_obj_pattern, content, re.DOTALL)
    if match:
        return match.group(0).strip()
    raise ValueError(f"No valid JSON found after thinking tags. Content: {content[:300]}")


class PlantDiseaseService:
    """
    Main service for plant disease detection and advisory.
    Orchestrates LLM calls for analysis, risk assessment, and treatment recommendations.
    """
    
    def __init__(self):
        print("\n" + "="*60)
        print("Initializing Plant Disease Service")
        print("="*60)
        
        # Initialize LLM clients
        self.reasoning_client = AzureAIClient(model=MODEL_REASONING)
        print("✓ Reasoning client ready")
        
        self.performance_client = AzureAIClient(model=MODEL_HIGH_PERF)
        print("✓ Performance client ready")
        
        self.chat_client = AzureAIClient(model=MODEL_CHAT_MOD)
        print("✓ Chat client ready")
        
        # Initialize utilities
        self.prompts = DiseaseDetectionPrompts()
        self.logger = AILogger()
        self.rate_limiter = RateLimiter(max_calls=100, time_window=60)
        
        print("="*60)
        print("✓ PlantDiseaseService initialized successfully")
        print("="*60 + "\n")
        
        self.logger.info("PlantDiseaseService initialized")
    
    async def analyze_plant_image(
        self, 
        image_data: str, 
        crop_type: str,
        environmental_data: Optional[Dict] = None,
        user_description: Optional[str] = None
    ) -> Dict:
        """
        Main orchestration method for complete plant disease analysis pipeline.
        
        Args:
            image_data: Base64 encoded image string (saved but not analyzed by vision model)
            crop_type: Type of crop (e.g., "tomato", "wheat", "rice")
            environmental_data: Optional dict with temperature, humidity, soil_moisture
            user_description: Optional text description of symptoms
        
        Returns:
            Complete diagnosis with severity, risk, and recommendations
        
        Raises:
            Exception: If any LLM call fails
        """
        self.logger.info(f"Starting analysis for {crop_type}")
        
        # Step 1: Disease Detection using reasoning model
        disease_result = await self._detect_disease_reasoning(
            crop_type, user_description, environmental_data
        )
        
        self.logger.info(f"Disease detected: {disease_result.get('disease')}")
        
        # Step 2: Environmental Context & Risk Analysis
        if disease_result['disease'] not in ['Healthy', 'Unknown']:
            risk_assessment = await self._assess_spread_risk(
                disease_result, environmental_data
            )
        else:
            risk_assessment = {
                "risk_level": "low",
                "spread_rate": "none",
                "favorable_conditions": False,
                "timeframe_days": None,
                "neighboring_risk": "low",
                "risk_factors": []
            }
        
        # Step 3: Treatment Recommendations (skip if healthy)
        if disease_result['disease'] not in ['Healthy', 'Unknown']:
            treatment_plan = await self._generate_treatment_plan(
                disease=disease_result['disease'],
                severity=disease_result['severity_level'],
                crop_type=crop_type,
                environmental_data=environmental_data
            )
            
            # Step 4: Generate Farmer-Friendly Action Plan
            action_plan_text = await self._generate_action_plan(
                disease=disease_result['disease'],
                severity=disease_result['severity_level'],
                treatments=treatment_plan.get('chemical_treatments', []),
                organic=treatment_plan.get('organic_alternatives', [])
            )
        else:
            treatment_plan = {
                "immediate_actions": ["Continue regular monitoring"],
                "chemical_treatments": [],
                "organic_alternatives": [],
                "preventive_measures": ["Maintain good irrigation", "Monitor regularly for any changes"],
                "environmental_controls": {},
                "expected_recovery_days": 0,
                "monitoring_schedule": "Weekly visual inspection"
            }
            action_plan_text = "**Plant Appears Healthy!**\n\nContinue with regular care and monitoring practices. Maintain proper irrigation and nutrition."
        
        # Combine all results
        complete_result = {
            **disease_result,
            **risk_assessment,
            **treatment_plan,
            "action_plan_text": action_plan_text,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info("Analysis completed successfully")
        return complete_result
    
    async def _detect_disease_reasoning(
        self, 
        crop_type: str, 
        user_description: Optional[str] = None,
        env_data: Optional[Dict] = None
    ) -> Dict:
        """
        Use reasoning model to analyze disease based on crop type and context.
        
        Args:
            crop_type: Type of crop
            user_description: Optional user description of symptoms
            env_data: Optional environmental data
        
        Returns:
            Dict with disease, severity, confidence, and other details
        
        Raises:
            Exception: If LLM call fails or returns invalid JSON
        """
        self.logger.info(f"Analyzing disease for {crop_type}")
        
        # Build analysis prompt
        env_summary = ""
        if env_data:
            env_summary = f"""
- Temperature: {env_data.get('temperature', 'N/A')}°C
- Humidity: {env_data.get('humidity', 'N/A')}%
- Soil Moisture: {env_data.get('soil_moisture', 'N/A')}%"""
        
        prompt = f"""You are an expert plant pathologist. Based on the following information, provide a disease diagnosis for a {crop_type} plant.

**Available Information:**
- Crop Type: {crop_type}
- User Description: {user_description or "Image uploaded - no text description provided"}
- Environmental Conditions:{env_summary if env_summary else " Not available"}

**Task:**
Analyze the most likely disease affecting this {crop_type} plant based on:
1. Common diseases for {crop_type}
2. Current environmental conditions (if provided)
3. Seasonal patterns
4. Any symptoms mentioned by the user

**Common {crop_type} diseases to consider:**
- Early Blight (fungal, brown spots with concentric rings)
- Late Blight (water-soaked lesions, rapid spread)
- Powdery Mildew (white powdery coating)
- Bacterial Spot (dark spots with yellow halos)
- Leaf Rust (orange/brown pustules)
- Mosaic Virus (mottled yellow-green patterns)
- Septoria Leaf Spot (small circular spots)
- Anthracnose (sunken lesions)

IMPORTANT: Return ONLY a valid JSON object with this structure (no markdown, no code blocks, no extra text):
{{
    "disease": "most likely disease name (e.g., 'Early Blight', 'Powdery Mildew')",
    "disease_category": "rust|mildew|blight|spot|mosaic|anthracnose",
    "confidence": 0.75,
    "severity_level": 2,
    "severity_description": "Moderate",
    "infection_percentage": 25.0,
    "visual_symptoms": ["symptom 1", "symptom 2", "symptom 3"],
    "affected_areas": "description of typical affected areas",
    "disease_stage": "early|mid|advanced",
    "reasoning": "brief explanation of diagnosis based on available data"
}}

**Guidelines:**
- Return ONLY valid JSON, no markdown formatting
- Confidence: 0.6-0.8 without visual confirmation
- The response should be crisp and to the point, do not include unnecessary details.
- Severity levels: 1=Mild (0-10%), 2=Moderate (10-30%), 3=Severe (30-60%), 4=Critical (>60%)
- If insufficient information, suggest most common disease for the crop
- Consider environmental factors in your diagnosis"""

        messages = [{"role": "user", "content": prompt}]
        
        self.logger.info("Calling reasoning model for disease detection...")
        
        response = await self.reasoning_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise Exception("Invalid response structure from LLM - no choices")
        
        content = response.choices[0].message.content
        
        if not content:
            raise Exception("Empty content received from LLM")
        
        # Extract JSON from markdown if needed
        clean_json = extract_json_from_response(content)
        self.logger.info(f"Extracted JSON length: {len(clean_json)}")
        
        result = json.loads(clean_json)
        self.logger.info(f"Disease analysis completed: {result.get('disease')}")
        
        # Validate required fields
        required_fields = ['disease', 'disease_category', 'confidence', 'severity_level', 
                          'severity_description', 'infection_percentage', 'visual_symptoms', 
                          'affected_areas', 'disease_stage', 'reasoning']
        
        for field in required_fields:
            if field not in result:
                raise Exception(f"Missing required field in LLM response: {field}")
        
        # Return validated result
        return {
            "disease": result['disease'],
            "disease_category": result['disease_category'],
            "confidence": float(result['confidence']),
            "severity_level": int(result['severity_level']),
            "severity_description": result['severity_description'],
            "infection_percentage": float(result['infection_percentage']),
            "visual_symptoms": result['visual_symptoms'],
            "affected_areas": result['affected_areas'],
            "disease_stage": result['disease_stage'],
            "reasoning": result['reasoning']
        }
    
    async def _assess_spread_risk(
    self, disease_result: Dict, env_data: Optional[Dict]
) -> Dict:
        """
        Use reasoning model to predict disease spread risk based on environmental conditions.
        """
        self.logger.info("Assessing spread risk...")
        
        prompt = self.prompts.get_risk_assessment_prompt(
            disease=disease_result['disease'],
            severity=disease_result['severity_level'],
            temperature=env_data.get('temperature') if env_data else None,
            humidity=env_data.get('humidity') if env_data else None,
            soil_moisture=env_data.get('soil_moisture') if env_data else None
        )
        
        # Add specific instructions for reasoning models
        prompt += """

    IMPORTANT INSTRUCTIONS:
    1. Do NOT include your thinking process or reasoning steps in the response
    2. Do NOT use <think> tags
    3. Return ONLY the final JSON answer
    4. No markdown code blocks
    5. No extra text or explanation
    6. Just the raw JSON object starting with { and ending with }"""
        
        try:
            response = await self.reasoning_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=3000,  # Increased from 1500
                response_format={"type": "json_object"}
            )
            
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise Exception("Invalid response structure from LLM - no choices")
            
            content = response.choices[0].message.content
            
            print(f"\n{'='*80}")
            print("RISK ASSESSMENT RAW RESPONSE")
            print(f"{'='*80}")
            print(f"Content length: {len(content) if content else 0}")
            print(f"Content preview (first 500 chars):")
            print(content[:500] if content else "NONE")
            print(f"{'='*80}\n")
            
            if not content:
                raise Exception("Empty content received from LLM for risk assessment")
            
            if not content.strip():
                raise Exception("Content from LLM is only whitespace")
            
            # Extract JSON (handles <think> tags)
            try:
                clean_json = extract_json_from_response(content)
                print(f"✓ JSON extraction successful, length: {len(clean_json)}")
            except ValueError as e:
                raise Exception(f"Failed to extract JSON: {str(e)}")
            
            if not clean_json or not clean_json.strip():
                raise Exception(f"Extracted JSON is empty")
            
            # Parse JSON
            try:
                result = json.loads(clean_json)
                print(f"✓ JSON parse successful, keys: {list(result.keys())}")
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse JSON: {str(e)}\nClean JSON:\n{clean_json[:500]}")
            
            self.logger.info(f"Risk assessment completed: {result.get('risk_level')}")
            
            # Validate required fields
            required_fields = ['risk_level', 'spread_rate', 'favorable_conditions', 
                            'neighboring_risk', 'risk_factors']
            
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                raise Exception(f"Missing required fields: {missing_fields}")
            
            return {
                "risk_level": result['risk_level'],
                "spread_rate": result['spread_rate'],
                "favorable_conditions": result['favorable_conditions'],
                "timeframe_days": result.get('timeframe_days'),
                "neighboring_risk": result['neighboring_risk'],
                "risk_factors": result['risk_factors']
            }
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {str(e)}")
            raise

    async def _generate_treatment_plan(
        self, disease: str, severity: int, crop_type: str, 
        environmental_data: Optional[Dict]
    ) -> Dict:
        """
        Generate comprehensive treatment recommendations using high-performance model.
        
        Args:
            disease: Disease name
            severity: Severity level (0-4)
            crop_type: Type of crop
            environmental_data: Environmental conditions
        
        Returns:
            Dict with immediate_actions, chemical_treatments, organic_alternatives, etc.
        
        Raises:
            Exception: If LLM call fails or returns invalid JSON
        """
        self.logger.info("Generating treatment plan...")
        
        prompt = self.prompts.get_treatment_prompt(
            disease=disease,
            severity=severity,
            crop_type=crop_type,
            env_data=environmental_data or {}
        )
        
        # Add instruction for clean JSON
        prompt += "\n\nIMPORTANT: Return ONLY valid JSON without markdown code blocks, formatting, or any extra text."
        
        response = await self.performance_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise Exception("Invalid response structure from LLM - no choices")
        
        content = response.choices[0].message.content
        
        if not content:
            raise Exception("Empty content received from LLM for treatment plan")
        
        # Extract JSON from markdown if needed
        try:
            clean_json = extract_json_from_response(content)
        except ValueError as e:
            raise Exception(f"Failed to extract JSON from treatment plan response: {str(e)}")
        
        if not clean_json or not clean_json.strip():
            raise Exception(f"Extracted JSON is empty. Original content was: {content[:500]}")
        
        result = json.loads(clean_json)
        self.logger.info("Treatment plan generated successfully")
        
        # Validate required fields
        required_fields = ['immediate_actions', 'chemical_treatments', 'organic_alternatives', 
                          'preventive_measures', 'environmental_controls', 
                          'expected_recovery_days', 'monitoring_schedule']
        
        for field in required_fields:
            if field not in result:
                raise Exception(f"Missing required field in treatment plan: {field}")
        
        return {
            "immediate_actions": result['immediate_actions'],
            "chemical_treatments": result['chemical_treatments'],
            "organic_alternatives": result['organic_alternatives'],
            "preventive_measures": result['preventive_measures'],
            "environmental_controls": result['environmental_controls'],
            "expected_recovery_days": result['expected_recovery_days'],
            "monitoring_schedule": result['monitoring_schedule']
        }
    
    async def _generate_action_plan(
        self, disease: str, severity: int, treatments: List[Dict], organic: List[Dict]
    ) -> str:
        """
        Generate simple 3-step action plan text for farmers.
        Uses chat model for clear, concise communication.
        
        Args:
            disease: Disease name
            severity: Severity level
            treatments: List of chemical treatments
            organic: List of organic alternatives
        
        Returns:
            Formatted markdown text with 3 clear steps
        
        Raises:
            Exception: If LLM call fails
        """
        self.logger.info("Generating action plan...")
        
        chemical_names = [t.get('product', 'recommended treatment') for t in treatments[:2]]
        organic_names = [o.get('solution', 'organic remedy') for o in organic[:2]]
        
        prompt = f"""Create a clear, farmer-friendly 3-step action plan for treating {disease} (severity level: {severity}/4).

Available treatments:
- Chemical: {', '.join(chemical_names) if chemical_names else 'Contact local agricultural office'}
- Organic: {', '.join(organic_names) if organic_names else 'Neem oil solution'}

Format your response EXACTLY as:

**Step 1: Immediate Action (Next 24-48 hours)**
[Specific urgent actions the farmer should take RIGHT NOW]

**Step 2: Treatment Application**
[Specific instructions for applying recommended treatments with dosages]

**Step 3: Monitoring & Prevention**
[What to watch for and how to prevent future occurrences]

Keep language simple, direct, and actionable. Use short sentences. Avoid technical jargon.
Do NOT wrap your response in code blocks or markdown formatting."""
        
        response = await self.chat_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=2000
        )
        
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise Exception("Invalid response structure from LLM - no choices")
        
        content = response.choices[0].message.content
        
        if not content:
            raise Exception("Empty content received from LLM for action plan")
        
        self.logger.info("Action plan generated successfully")
        return content
    
    # ==================== ADDITIONAL UTILITY METHODS ====================
    
    async def batch_analyze(
        self, images_data: List[Dict[str, str]], crop_type: str
    ) -> List[Dict]:
        """
        Batch process multiple images (e.g., from drone capture).
        
        Args:
            images_data: List of dicts with 'image' (base64) and optional 'location'
            crop_type: Crop type for all images
        
        Returns:
            List of diagnosis results
        """
        results = []
        
        for idx, img_data in enumerate(images_data):
            try:
                self.logger.info(f"Processing image {idx+1}/{len(images_data)}")
                
                result = await self.analyze_plant_image(
                    image_data=img_data['image'],
                    crop_type=crop_type,
                    environmental_data=img_data.get('environmental_data')
                )
                
                results.append({
                    "image_index": idx,
                    "location": img_data.get('location'),
                    **result
                })
                
                # Rate limiting
                await self.rate_limiter.wait_if_needed()
                
            except Exception as e:
                self.logger.error(f"Error processing image {idx}: {str(e)}")
                raise Exception(f"Failed to process image {idx}: {str(e)}")
        
        return results
    
    async def get_disease_info(self, disease_name: str) -> Dict:
        """
        Get detailed information about a specific disease.
        
        Args:
            disease_name: Name of the disease
        
        Returns:
            Dict with disease information
        
        Raises:
            Exception: If LLM call fails
        """
        prompt = f"""Provide comprehensive information about the plant disease: {disease_name}

Include:
1. Common and scientific names
2. Causal agent (fungus, bacteria, virus, etc.)
3. Typical symptoms and visual appearance
4. Commonly affected crops
5. Transmission methods
6. Favorable environmental conditions
7. Disease cycle
8. Economic impact
9. Prevention strategies
10. Treatment options

Return ONLY valid JSON with these keys: name, scientific_name, causal_agent, symptoms, affected_crops, transmission, favorable_conditions, disease_cycle, economic_impact, prevention, treatments

Do NOT use markdown code blocks."""
        
        response = await self.chat_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise Exception("Invalid response from LLM")
        
        content = response.choices[0].message.content
        
        if not content:
            raise Exception("Empty content from LLM")
        
        clean_json = extract_json_from_response(content)
        return json.loads(clean_json)


# Singleton instance
_service_instance = None

def get_disease_service() -> PlantDiseaseService:
    """Get or create singleton service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = PlantDiseaseService()
    return _service_instance
