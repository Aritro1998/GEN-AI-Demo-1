"""Central configuration for models, retrieval, and pipeline behavior."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

API_CONFIG = {
    "api_key_env": "OPENAI_API_KEY",
    "base_url_env": "BASE_URL",
}


def resolve_backend_path(path_value):
    """Resolve relative backend paths while still allowing absolute overrides."""
    candidate = Path(path_value)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


MODELS = {
    "default_text": os.getenv("DEFAULT_MODEL", "genailab-maas-gpt-4o"),
    "classifier_text": os.getenv(
        "CLASSIFIER_MODEL",
        os.getenv("DEFAULT_MODEL", "genailab-maas-gpt-4o"),
    ),
    "reasoner_text": os.getenv(
        "REASONING_MODEL",
        os.getenv("DEFAULT_MODEL", "genailab-maas-gpt-4o"),
    ),
    "generator_text": os.getenv(
        "GENERATOR_MODEL",
        os.getenv("DEFAULT_MODEL", "genailab-maas-gpt-4o"),
    ),
    "embedding": os.getenv(
        "EMBEDDING_MODEL",
        "azure/genailab-maas-text-embedding-3-large",
    ),
    "vision": os.getenv(
        "VISION_MODEL",
        "azure_ai/genailab-maas-Llama-3.2-90B-Vision-Instruct",
    ),
    "transcription": os.getenv(
        "TRANSCRIPTION_MODEL",
        "azure/genailab-maas-whisper",
    ),
}

DEFAULT_MODEL = MODELS["default_text"]
CLASSIFIER_MODEL = MODELS["classifier_text"]
REASONING_MODEL = MODELS["reasoner_text"]
GENERATOR_MODEL = MODELS["generator_text"]
EMBEDDING_MODEL = MODELS["embedding"]
VISION_MODEL = MODELS["vision"]
TRANSCRIPTION_MODEL = MODELS["transcription"]

KNOWLEDGE_DATA_PATH = os.getenv("KNOWLEDGE_DATA_PATH", "data/knowledge.json")


RAG_CONFIG = {
    "enabled": True,
    # This path is configurable through KNOWLEDGE_DATA_PATH so the knowledge
    # base can live elsewhere without changing the source code.
    "data_path": KNOWLEDGE_DATA_PATH,
    "embedding_model": EMBEDDING_MODEL,
    "text_fields": ["text", "title", "summary", "description", "notes"],
}


PREPROCESSING_PIPELINE = [
    {
        "name": "speech_to_text",
        "id": "speech_transcript",
        "capability": "transcription",
        "model": TRANSCRIPTION_MODEL,
        "input_key": "audio_path",
        "prompt": (
            "Transcribe the user's infrastructure issue faithfully. Preserve exact "
            "error codes, service names, environment names, timestamps, and any "
            "spoken troubleshooting details when they are audible."
        ),
    },
    {
        "name": "screenshot_analyzer",
        "id": "image_findings",
        "capability": "vision",
        "model": VISION_MODEL,
        "input_key": "image_paths",
        "system_prompt": """
            You analyze screenshots shared during infrastructure incident reporting.

            Focus on:
            - visible error messages or banners
            - stack traces, codes, and failing components
            - UI clues that indicate the affected system or workflow
            - signs of timeouts, resource issues, or connectivity failures

            Keep the response concise, factual, and useful for troubleshooting.
        """,
        "prompt": (
            "User-provided typed context:\n{typed_input}\n\n"
            "Analyze the attached screenshot(s) and return:\n"
            "1. Visible errors or warnings\n"
            "2. Important technical clues\n"
            "3. What the screenshot suggests about likely failure area\n"
            "4. Any exact text that should be preserved for downstream analysis\n"
        ),
        "temperature": 0.1,
    },
]


PIPELINE = [
    {
        "name": "classifier",
        "id": "classification",
        "capability": "text",
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
            - Base your decision on logs, metrics, screenshots, and issue context
            - If multiple signals exist, pick the primary cause
            - If unclear or mixed, return "Others"

            Output format:
            - Return ONLY one word from the list above
            - Do not explain
            - Do not add extra text
        """,
        "prompt": (
            "Combined incident input:\n{original_input}\n\n"
            "Additional multimodal evidence:\n{multimodal_context}\n\n"
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
        "capability": "text",
        "model": REASONING_MODEL,
        "rag": True,
        "system_prompt": """
            You are an experienced SRE / IT infrastructure engineer.

            Your job is to analyze infrastructure issues using logs, metrics,
            screenshot evidence, speech transcripts, and retrieved context.
            Be practical, concise, and action-oriented.

            Always:
            - Focus on root cause, not generic explanations
            - Use evidence from logs, metrics, screenshots, or transcripts
            - Suggest concrete next steps (commands, configs, checks)
            - Prioritize actions (what to do first vs later)
        """,
        "prompt": (
            "Problem statement:\n{original_input}\n\n"
            "Speech transcript (if any):\n{speech_transcript}\n\n"
            "Screenshot analysis (if any):\n{image_findings}\n\n"
            "Classified category (one of CPU, Memory, I/O, Network, Others):\n"
            "{classification}\n\n"
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
        "capability": "text",
        "model": GENERATOR_MODEL,
        "system_prompt": """
            You are a senior Site Reliability Engineer (SRE) writing a corporate
            Root Cause Analysis (RCA) report.

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
            "Speech transcript (if any):\n{speech_transcript}\n\n"
            "Screenshot analysis (if any):\n{image_findings}\n\n"
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
            "- Key logs, metrics, screenshots, or observations\n"
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
