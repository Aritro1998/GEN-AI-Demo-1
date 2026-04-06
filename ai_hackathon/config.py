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
        "system_prompt": "You classify the problem into a short category useful for downstream reasoning.",
        "prompt": (
            "Input:\n{original_input}\n\n"
            "Return only a short category label for this problem."
        ),
        "temperature": 0.0,
    },
    {
        "name": "reasoner",
        "id": "analysis",
        "rag": True,
        "system_prompt": "You design a practical AI solution approach for the given problem.",
        "prompt": (
            "Problem statement:\n{original_input}\n\n"
            "Problem category:\n{classification}\n\n"
            "Retrieved context:\n{retrieved_context}\n\n"
            "Explain the recommended pipeline, data flow, and key design choices."
        ),
        "temperature": 0.2,
    },
    {
        "name": "generator",
        "id": "final_output",
        "system_prompt": "You generate a clear final solution proposal for a hackathon demo.",
        "prompt": (
            "Problem statement:\n{original_input}\n\n"
            "Analysis:\n{analysis}\n\n"
            "Write the final answer with:\n"
            "1. Proposed architecture\n"
            "2. Recommended pipeline steps\n"
            "3. Demo data needed\n"
            "4. Expected output"
        ),
        "temperature": 0.4,
    },
]
