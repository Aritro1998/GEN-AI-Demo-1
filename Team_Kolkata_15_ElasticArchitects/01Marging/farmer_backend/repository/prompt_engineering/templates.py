# repository/prompt_engineering/templates.py
"""
Prompt templates for plant disease detection system.
Contains all prompts for vision analysis, risk assessment, and treatment recommendations.
"""

from typing import Optional, Dict


class DiseaseDetectionPrompts:
    """Prompt templates for disease detection and analysis"""
    
    @staticmethod
    def get_disease_detection_prompt(crop_type: str) -> str:
        """
        Generate prompt for disease detection from leaf image.
        
        Args:
            crop_type: Type of crop being analyzed
        
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert plant pathologist specializing in {crop_type} diseases. Analyze this leaf image and provide a detailed diagnosis.

**Instructions:**
1. Carefully examine the leaf for any signs of disease, discoloration, spots, lesions, or abnormal growth
2. Identify the specific disease if present, or confirm if the plant is healthy
3. Assess the severity based on the percentage of leaf area affected
4. Provide confidence in your diagnosis

**Return a JSON response with this EXACT structure:**
{{
    "disease": "specific disease name (e.g., 'Late Blight', 'Powdery Mildew') or 'Healthy'",
    "disease_category": "rust|mildew|blight|spot|mosaic|healthy",
    "confidence": 0.0-1.0,
    "severity_level": 0-4,
    "severity_description": "None|Mild|Moderate|Severe|Critical",
    "infection_percentage": 0-100,
    "visual_symptoms": ["symptom1", "symptom2", "symptom3"],
    "affected_areas": "description of which parts of leaf are affected",
    "disease_stage": "early|mid|advanced"
}}

**Severity Level Guidelines:**
- **0 (None)**: Healthy plant, no visible disease signs, vibrant green color
- **1 (Mild)**: Less than 10% leaf area affected, few small spots or early discoloration
- **2 (Moderate)**: 10-30% affected, spreading lesions or spots, some yellowing
- **3 (Severe)**: 30-60% affected, significant damage, multiple lesions, browning
- **4 (Critical)**: More than 60% affected, plant survival threatened, extensive damage

**Disease Categories:**
- rust: Orange, brown, or yellow pustules/spots (fungal)
- mildew: White powdery or downy coating (fungal)
- blight: Rapid browning, wilting, tissue death (bacterial/fungal)
- spot: Distinct circular or irregular spots (bacterial/fungal)
- mosaic: Mottled yellow/green patterns, distorted leaves (viral)
- healthy: No disease signs

Be precise and base your analysis only on what you observe in the image."""

    @staticmethod
    def get_risk_assessment_prompt(
        disease: str,
        severity: int,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        soil_moisture: Optional[float] = None
    ) -> str:
        """
        Generate prompt for disease spread risk assessment.
        
        Args:
            disease: Detected disease name
            severity: Current severity level (0-4)
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            soil_moisture: Soil moisture percentage
        
        Returns:
            Formatted prompt string
        """
        env_info = ""
        if temperature is not None:
            env_info += f"- **Temperature**: {temperature}°C\n"
        if humidity is not None:
            env_info += f"- **Humidity**: {humidity}%\n"
        if soil_moisture is not None:
            env_info += f"- **Soil Moisture**: {soil_moisture}%\n"
        
        if not env_info:
            env_info = "- Environmental data not available\n"
        
        return f"""You are an agricultural disease epidemiologist. Assess the spread risk for **{disease}** with current severity level **{severity}/4**.

**Current Environmental Conditions:**
{env_info}

**Analysis Required:**
1. **Favorability**: Are these conditions favorable for disease spread?
2. **Spread Rate**: How quickly will the disease spread? (slow/moderate/rapid)
3. **Risk to Neighboring Plants**: What is the risk to nearby plants? (low/medium/high)
4. **Timeframe**: In how many days might severity increase?
5. **Risk Factors**: What specific factors contribute to spread risk?

**Return a JSON response with this structure:**
{{
    "risk_level": "low|medium|high",
    "spread_rate": "slow|moderate|rapid",
    "favorable_conditions": true/false,
    "timeframe_days": number (estimated days until severity increases),
    "neighboring_risk": "low|medium|high",
    "risk_factors": ["factor1", "factor2", "factor3"]
}}

**Risk Level Guidelines:**
- **low**: Unfavorable conditions, disease contained, slow spread expected
- **medium**: Moderate conditions, some spread likely, monitoring needed
- **high**: Favorable conditions, rapid spread likely, immediate action required
- **critical**: Optimal disease conditions, outbreak imminent, emergency response needed

Consider factors like:
- Temperature range optimal for pathogen
- Humidity levels (high humidity favors most fungal diseases)
- Season and weather patterns
- Disease-specific transmission mechanisms
- Current severity as baseline

Be specific about which environmental factors are most concerning."""

    @staticmethod
    def get_treatment_prompt(
        disease: str,
        severity: int,
        crop_type: str,
        env_data: Dict
    ) -> str:
        """
        Generate prompt for treatment recommendations.
        
        Args:
            disease: Disease name
            severity: Severity level (0-4)
            crop_type: Type of crop
            env_data: Environmental data dict
        
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert agricultural consultant. Provide comprehensive treatment recommendations for **{disease}** on **{crop_type}** crops with severity level **{severity}/4**.

**Current Situation:**
- Disease: {disease}
- Severity: {severity}/4
- Crop: {crop_type}
- Environmental Data: {env_data if env_data else 'Not available'}

**Provide detailed recommendations in these categories:**

1. **Immediate Actions** (Next 24-48 hours)
   - Urgent steps to take right away
   - Isolation or removal of infected parts
   - Cultural practices to implement immediately

2. **Chemical Treatments**
   - Specific fungicides, bactericides, or pesticides
   - Active ingredients
   - Dosage per hectare or acre
   - Application method (spray, drench, dust, etc.)
   - Safety period before harvest
   - Number of applications needed

3. **Organic Alternatives**
   - Natural/organic solutions
   - Ingredients and preparation methods
   - Application frequency
   - Expected effectiveness

4. **Preventive Measures**
   - Steps to prevent disease recurrence
   - Crop rotation recommendations
   - Sanitation practices
   - Resistant varieties to consider

5. **Environmental Controls**
   - Optimal temperature and humidity ranges
   - Irrigation adjustments
   - Spacing and ventilation improvements

**Return a JSON response with this structure:**
{{
    "immediate_actions": [
        "action 1",
        "action 2",
        "action 3"
    ],
    "chemical_treatments": [
        {{
            "product": "product name",
            "active_ingredient": "chemical name",
            "dosage": "amount per hectare",
            "application_method": "spray/drench/dust",
            "safety_period_days": number,
            "application_frequency": "description",
            "cost_estimate_per_hectare": "low/medium/high"
        }}
    ],
    "organic_alternatives": [
        {{
            "solution": "solution name",
            "ingredients": ["ingredient1", "ingredient2"],
            "preparation": "step-by-step preparation",
            "application_frequency": "how often to apply",
            "effectiveness": "high/medium/low"
        }}
    ],
    "preventive_measures": [
        "preventive measure 1",
        "preventive measure 2",
        "preventive measure 3"
    ],
    "environmental_controls": {{
        "temperature": "optimal range in °C",
        "humidity": "optimal range in %",
        "irrigation": "recommendations",
        "spacing": "recommendations"
    }},
    "expected_recovery_days": number,
    "monitoring_schedule": "description of monitoring frequency and what to look for"
}}

Be practical, specific, and farmer-friendly. Prioritize treatments that are:
- Readily available in agricultural markets
- Cost-effective for small to medium farmers
- Safe for environment and beneficial insects
- Proven effective for this specific disease"""

    @staticmethod
    def get_knowledge_base_prompt(disease_name: str) -> str:
        """
        Generate prompt for disease knowledge base information.
        
        Args:
            disease_name: Name of disease to get info about
        
        Returns:
            Formatted prompt string
        """
        return f"""Provide comprehensive educational information about the plant disease: **{disease_name}**

Include the following details:

1. **Common and Scientific Names**
2. **Causal Agent** (fungus, bacteria, virus, nematode, etc.)
3. **Symptoms and Visual Appearance**
4. **Commonly Affected Crops**
5. **Transmission Methods**
6. **Favorable Environmental Conditions**
7. **Disease Cycle and Life Stages**
8. **Economic Impact**
9. **Prevention Strategies**
10. **Treatment Options**

Return as JSON with this structure:
{{
    "name": "common name",
    "scientific_name": "scientific name",
    "causal_agent": "type and species",
    "symptoms": ["symptom1", "symptom2"],
    "affected_crops": ["crop1", "crop2"],
    "transmission": ["method1", "method2"],
    "favorable_conditions": {{
        "temperature": "range",
        "humidity": "range",
        "other_factors": ["factor1", "factor2"]
    }},
    "disease_cycle": "description",
    "economic_impact": "description",
    "prevention": ["strategy1", "strategy2"],
    "treatments": ["treatment1", "treatment2"]
}}"""

    @staticmethod
    def get_preventive_measures_prompt(
        crop_type: str,
        region: str,
        season: str
    ) -> str:
        """
        Generate prompt for preventive measures recommendations.
        
        Args:
            crop_type: Type of crop
            region: Geographic region
            season: Current season
        
        Returns:
            Formatted prompt string
        """
        return f"""As an agricultural expert, suggest comprehensive preventive measures for **{crop_type}** cultivation in **{region}** during **{season}** season.

Focus on disease prevention and crop health optimization.

**Provide recommendations for:**

1. **General Cultural Practices**
   - Soil preparation and management
   - Planting practices (spacing, depth, timing)
   - Crop rotation strategies
   - Sanitation and hygiene

2. **Environmental Management**
   - Optimal temperature and humidity control
   - Irrigation scheduling and methods
   - Drainage management
   - Mulching practices

3. **Early Detection Signs**
   - Visual symptoms to watch for
   - Inspection frequency and methods
   - When to take action

4. **Organic Prevention Methods**
   - Companion planting
   - Natural pest deterrents
   - Beneficial insects to encourage
   - Organic soil amendments

5. **Monitoring Frequency**
   - How often to inspect crops
   - What to look for during inspections
   - Record-keeping recommendations

Return as JSON:
{{
    "general_practices": ["practice1", "practice2"],
    "environmental_management": {{
        "temperature": "recommendations",
        "humidity": "recommendations",
        "irrigation": "recommendations",
        "drainage": "recommendations"
    }},
    "early_detection_signs": ["sign1", "sign2"],
    "organic_methods": ["method1", "method2"],
    "monitoring_frequency": "description",
    "seasonal_considerations": ["consideration1", "consideration2"]
}}"""


class PromptChain:
    """Chain multiple prompts for complex analysis"""
    
    def __init__(self):
        self.prompts = DiseaseDetectionPrompts()
    
    def create_diagnosis_chain(self, crop_type: str) -> list:
        """Create a chain of prompts for full diagnosis"""
        return [
            {
                "step": "detection",
                "prompt": self.prompts.get_disease_detection_prompt(crop_type)
            }
        ]
    
    def create_advisory_chain(
        self,
        disease: str,
        severity: int,
        crop_type: str,
        env_data: Dict
    ) -> list:
        """Create a chain for treatment advisory"""
        return [
            {
                "step": "risk_assessment",
                "prompt": self.prompts.get_risk_assessment_prompt(
                    disease, severity,
                    env_data.get('temperature'),
                    env_data.get('humidity'),
                    env_data.get('soil_moisture')
                )
            },
            {
                "step": "treatment",
                "prompt": self.prompts.get_treatment_prompt(
                    disease, severity, crop_type, env_data
                )
            }
        ]
