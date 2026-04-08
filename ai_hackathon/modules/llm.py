import os
from openai import OpenAI
from dotenv import load_dotenv
from config import API_CONFIG
import httpx

load_dotenv()

SAFE_REPLACEMENTS = {
    "symptoms": "signals",
    "condition": "state",
    "diagnosis": "analysis",
    "diagnose": "analyze",
    "treatment": "mitigation",
    "patient": "system",
}

def sanitize_text(text: str) -> str:
    for k, v in SAFE_REPLACEMENTS.items():
        text = text.replace(k, v)
    return text

def get_client():
    return OpenAI(
        api_key=os.getenv(API_CONFIG["api_key_env"]),
        base_url=os.getenv(API_CONFIG["base_url_env"]),
        http_client=httpx.Client(verify=False)
    )

def call_llm(model, system_prompt, user_prompt, temperature=0.3):
    system_prompt = sanitize_text(system_prompt)
    user_prompt = sanitize_text(user_prompt)
    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content
