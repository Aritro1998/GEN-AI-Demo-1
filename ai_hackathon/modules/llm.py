import os
from openai import OpenAI
from dotenv import load_dotenv
from config import API_CONFIG

load_dotenv()

def get_client():
    return OpenAI(
        api_key=os.getenv(API_CONFIG["api_key_env"]),
        base_url=os.getenv(API_CONFIG["base_url_env"]),
    )

def call_llm(model, system_prompt, user_prompt, temperature=0.3):
    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content
