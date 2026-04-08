"""Service helpers that bridge the API layer and the orchestration pipeline."""

import json
import logging
import tempfile
from functools import lru_cache
from pathlib import Path

from config import RAG_CONFIG, resolve_backend_path
from orchestrator import Orchestrator

logger = logging.getLogger(__name__)


def _save_uploaded_file(uploaded_file):
    """Persist an uploaded file temporarily so the orchestrator can read it."""
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        return temp_file.name


def _cleanup_temp_files(file_paths):
    """Remove temporary uploads after the pipeline finishes."""
    for file_path in file_paths:
        try:
            Path(file_path).unlink(missing_ok=True)
        except OSError:
            logger.exception("Failed to remove temporary upload: %s", file_path)


def _knowledge_path():
    """Resolve the configured knowledge file path inside the backend workspace."""
    return resolve_backend_path(RAG_CONFIG["data_path"])


def _load_knowledge_entries():
    """Read the current knowledge base entries from disk."""
    path = _knowledge_path()
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    return data if isinstance(data, list) else []


def _write_knowledge_entries(entries):
    """Write the full knowledge base back to disk using an atomic replace."""
    path = _knowledge_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(entries, handle, indent=2)
        handle.write("\n")

    temp_path.replace(path)


def _normalize_knowledge_entry(entry, default_source):
    """Shape incoming knowledge payloads to match the existing JSON schema."""
    return {
        "title": entry["title"].strip(),
        "summary": entry["summary"].strip(),
        "description": entry["description"].strip(),
        "category": entry.get("category", "Others").strip() or "Others",
        "notes": entry.get("notes", "").strip(),
        "source": entry.get("source", default_source).strip() or default_source,
    }


def _entry_signature(entry):
    """Build a lightweight signature for duplicate detection."""
    return (
        entry["title"].strip().lower(),
        entry["summary"].strip().lower(),
    )


def _append_unique_knowledge_entry(entry):
    """Append a new knowledge entry unless an equivalent one already exists."""
    entries = _load_knowledge_entries()
    signature = _entry_signature(entry)
    if any(_entry_signature(existing) == signature for existing in entries):
        logger.warning(
            "Potential issue detected: duplicate knowledge entry skipped title=%s",
            entry["title"],
        )
        return entry, False

    entries.append(entry)
    _write_knowledge_entries(entries)
    refresh_orchestrator_cache()
    return entry, True


def add_manual_knowledge_entry(entry):
    """Append a reviewed manual entry to the knowledge base."""
    normalized_entry = _normalize_knowledge_entry(entry, default_source="manual")
    return _append_unique_knowledge_entry(normalized_entry)


def promote_output_to_knowledge(entry):
    """Append a reviewed model output summary as a knowledge entry."""
    normalized_entry = _normalize_knowledge_entry(entry, default_source="promoted_output")

    final_output = entry.get("final_output", "").strip()
    if final_output:
        notes = normalized_entry["notes"]
        normalized_entry["notes"] = (
            f"{notes}\n\nPromoted from reviewed output:\n{final_output}".strip()
            if notes
            else f"Promoted from reviewed output:\n{final_output}"
        )

    return _append_unique_knowledge_entry(normalized_entry)


@lru_cache(maxsize=1)
def get_orchestrator():
    """Reuse one orchestrator instance so embeddings are not rebuilt per request."""
    # Caching the orchestrator avoids rebuilding the RAG index and embeddings on
    # every API call, which would slow down the hackathon demo noticeably.
    return Orchestrator()


def refresh_orchestrator_cache():
    """Clear the cached orchestrator so later requests see updated knowledge."""
    get_orchestrator.cache_clear()


def run_orchestration_request(text_input="", audio_file=None, image_files=None):
    """Store uploaded media, invoke the multimodal orchestrator, and clean up."""
    temp_files = []
    audio_path = None
    image_paths = []
    image_files = image_files or []

    try:
        if audio_file:
            audio_path = _save_uploaded_file(audio_file)
            temp_files.append(audio_path)

        for image_file in image_files:
            image_path = _save_uploaded_file(image_file)
            image_paths.append(image_path)
            temp_files.append(image_path)

        # The orchestrator owns the actual model-routing logic:
        # text steps call text LLMs, screenshot preprocessing calls the vision
        # model, and audio preprocessing calls the transcription model.
        result = get_orchestrator().run(
            input_text=text_input,
            audio_path=audio_path,
            image_paths=image_paths,
        )

        return {
            "message": "Processed successfully.",
            "input": {
                "text": text_input,
                "audio_supplied": bool(audio_file),
                "image_count": len(image_paths),
            },
            "output": result,
        }
    finally:
        _cleanup_temp_files(temp_files)
