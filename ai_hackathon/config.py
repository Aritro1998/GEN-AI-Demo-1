import os


API_CONFIG = {
    "api_key_env": "OPENAI_API_KEY",
    "base_url_env": "BASE_URL",
}

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "genailab-maas-gpt-4o")
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", DEFAULT_MODEL)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "azure/genailab-maas-text-embedding-3-large",
)
REASONING_MODEL = os.getenv("REASONING_MODEL", DEFAULT_MODEL)


RAG_CONFIG = {
    "enabled": True,
    "data_path": "data/knowledge.json",
    "embedding_model": EMBEDDING_MODEL,
    "text_fields": ["text", "title", "summary", "description", "notes"],
}

PIPELINE = [
    {
        "name": "classifier",
        "id": "classification",
        "model": CLASSIFIER_MODEL,
        "system_prompt": """
            You are an infrastructure issue classifier.

            Your task is to classify the problem into ONE of the following categories:
            - CPU
            - Memory
            - I/O
            - Network
            - Others

            Rules:
            - Choose the most dominant bottleneck signal
            - Base your decision on logs, metrics, and issue context
            - If multiple signals exist, pick the primary cause
            - If unclear or mixed, return "Others"

            Output format:
            - Return ONLY one word from the list above
            - Do not explain
            - Do not add extra text

        """,
        "prompt": (
            "Input:\n{original_input}\n\n"
    
            "Classify the issue based on issue such as:\n"
            "- CPU: high CPU usage, throttling, load spikes\n"
            "- Memory: OOM, memory leak, GC issues\n"
            "- I/O: disk latency, slow reads/writes, DB bottlenecks\n"
            "- Network: timeouts, high latency, connection issues\n"
            "- Others: unclear or mixed signals\n\n"
            
            "Answer:"
        ),
        "temperature": 0.0,
    },
    {
        "name": "reasoner",
        "id": "analysis",
        "model": REASONING_MODEL,
        "rag": True,
        "system_prompt":"""
            You are an experienced SRE / IT infrastructure engineer.

            Your job is to analyze infrastructure issues using logs, metrics, and context.
            Be practical, concise, and action-oriented.

            Always:
            - Focus on root cause, not generic explanations
            - Use evidence from logs/metrics
            - Suggest concrete next steps (commands, configs, checks)
            - Prioritize actions (what to do first vs later)
            """,
        "prompt": (
            "Problem statement:\n{original_input}\n\n"
    
            "Classified category (one of CPU, Memory, I/O, Network, Others):\n{classification}\n\n"
            
            "Relevant past incidents / context:\n{retrieved_context}\n\n"
            
            "Your task:\n"
            "1. Summarize the issue in 1-2 lines\n"
            "2. Identify the most likely root cause\n"
            "3. Provide supporting evidence (from logs/metrics/context)\n"
            "4. List immediate troubleshooting steps (step-by-step, actionable)\n"
            "5. Suggest long-term fixes / improvements\n"
            "6. Mention what to monitor next to confirm the fix\n\n"
            
            "Constraints:\n"
            "- Do NOT give generic advice\n"
            "- Be specific (e.g., commands, configs, tools)\n"
            "- Keep response structured and concise\n"
        ),
        "temperature": 0.2,
    },
    {
        "name": "generator",
        "id": "final_output",
        "system_prompt": """
            You are a senior Site Reliability Engineer (SRE) writing a corporate Root Cause Analysis (RCA) report.

            Your goal is to clearly communicate:
            - What happened
            - Why it happened
            - Impact
            - Actions taken
            - Preventive measures

            Tone:
            - Professional and concise
            - No speculation without evidence
            - Structured and easy to scan
        """,
        "prompt": (
           "Problem statement:\n{original_input}\n\n"
    
            "Technical analysis (from investigation):\n{analysis}\n\n"
            
            "Generate a structured RCA report with the following sections:\n\n"
            
            "1. Incident Summary\n"
            "- Brief description of the issue\n"
            "- Start time / detection context (if available)\n\n"
            
            "2. Impact\n"
            "- Affected systems/services\n"
            "- User/business impact\n\n"
            
            "3. Root Cause\n"
            "- Clear and specific root cause\n"
            "- Avoid vague statements\n\n"
            
            "4. Contributing Factors\n"
            "- Secondary issues that worsened the incident\n\n"
            
            "5. Investigation & Evidence\n"
            "- Key logs, metrics, or observations\n"
            "- Why this root cause was concluded\n\n"
            
            "6. Mitigation / Immediate Actions Taken\n"
            "- What was done to resolve the issue\n\n"
            
            "7. Preventive Actions (Short-term & Long-term)\n"
            "- Concrete steps to avoid recurrence\n\n"
            
            "8. Monitoring & Follow-up\n"
            "- What should be monitored going forward\n\n"
            
            "Constraints:\n"
            "- Keep it concise but complete\n"
            "- Use bullet points where appropriate\n"
            "- Do not invent data not present in the analysis\n"
        ),
        "temperature": 0.4,
    },
]
