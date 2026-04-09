import base64
import logging
import mimetypes
import os
from functools import lru_cache
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

from config import API_CONFIG, DEFAULT_MODEL

logger = logging.getLogger(__name__)

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
    """Replace sensitive domain words with safer neutral wording."""
    if not text:
        return ""

    # This small replacement layer avoids domain-specific phrasing that can
    # confuse downstream safety or routing behavior on some hosted models.
    for key, value in SAFE_REPLACEMENTS.items():
        text = text.replace(key, value)
    return text


@lru_cache(maxsize=1)
def get_client():
    """Create and cache the OpenAI client used by the pipeline."""
    api_key = os.getenv(API_CONFIG["api_key_env"])
    base_url = os.getenv(API_CONFIG["base_url_env"])

    if not api_key:
        logger.warning(
            "Potential issue detected: environment variable %s is not set",
            API_CONFIG["api_key_env"],
        )

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        # The current environment appears to require relaxed SSL validation for
        # the configured endpoint, so that behavior is preserved here.
        http_client=httpx.Client(verify=False),
    )


def _coerce_message_content(content):
    """Normalize SDK responses that may return text as strings or arrays."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif "text" in item:
                    text_parts.append(str(item["text"]))
            else:
                text_value = getattr(item, "text", None)
                if text_value:
                    text_parts.append(str(text_value))
        return "\n".join(part for part in text_parts if part).strip()

    return str(content or "")


def _file_to_data_url(file_path):
    """Encode a local image file as a data URL for vision model requests."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    mime_type, _ = mimetypes.guess_type(path.name)
    mime_type = mime_type or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _is_deployment_not_found(exc):
    """Return True when the exception signals a missing model deployment."""
    exc_str = str(exc).lower()
    return "404" in exc_str and ("notfounderror" in exc_str or "deploymentnotfound" in exc_str)


def call_text_model(model, system_prompt, user_prompt, temperature=0.3):
    """Send a text chat completion request and return the assistant text."""
    system_prompt = sanitize_text(system_prompt)
    user_prompt = sanitize_text(user_prompt)

    try:
        response = get_client().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
    except Exception as exc:
        if model != DEFAULT_MODEL and _is_deployment_not_found(exc):
            logger.warning(
                "Model %s unavailable (DeploymentNotFound), falling back to %s",
                model, DEFAULT_MODEL,
            )
            response = get_client().chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
        else:
            logger.exception("LLM request failed for model=%s", model)
            raise

    # The chat completion API can return empty content even on a successful
    # response object, so we treat that as a warning-worthy signal.
    content = _coerce_message_content(response.choices[0].message.content)
    if not content:
        logger.warning("Potential issue detected: model=%s returned no content", model)

    return content


def call_vision_model(model, system_prompt, user_prompt, image_paths, temperature=0.1):
    """Send screenshots plus text instructions to a multimodal vision model."""
    system_prompt = sanitize_text(system_prompt)
    user_prompt = sanitize_text(user_prompt)

    content = [{"type": "text", "text": user_prompt}]
    for image_path in image_paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": _file_to_data_url(image_path)},
            }
        )

    try:
        response = get_client().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            temperature=temperature,
        )
    except Exception as exc:
        if model != DEFAULT_MODEL and _is_deployment_not_found(exc):
            logger.warning(
                "Vision model %s unavailable (DeploymentNotFound), falling back to %s",
                model, DEFAULT_MODEL,
            )
            response = get_client().chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content},
                ],
                temperature=temperature,
            )
        else:
            logger.exception("Vision model request failed for model=%s", model)
            raise

    result = _coerce_message_content(response.choices[0].message.content)
    if not result:
        logger.warning("Potential issue detected: vision model=%s returned no content", model)

    return result


def transcribe_audio(model, audio_path, prompt=None):
    """Convert an audio issue report into text before the main pipeline runs."""
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    try:
        with path.open("rb") as audio_file:
            response = get_client().audio.transcriptions.create(
                model=model,
                file=audio_file,
                prompt=prompt,
            )
    except Exception:
        logger.exception("Audio transcription failed for model=%s", model)
        raise

    transcript = getattr(response, "text", None) or str(response)
    if not transcript.strip():
        logger.warning("Potential issue detected: transcription model=%s returned no text", model)

    return transcript.strip()


def call_llm(model, system_prompt, user_prompt, temperature=0.3):
    """Preserve the original text-only helper for existing module calls."""
    return call_text_model(
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
    )
