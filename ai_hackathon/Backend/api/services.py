"""Service helpers that bridge the API layer and the orchestration pipeline."""

import json
import logging
import tempfile
from functools import lru_cache
from pathlib import Path

from config import KNOWLEDGE_PROMOTION_MODEL, RAG_CONFIG, resolve_backend_path
from modules.llm import call_llm
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


def _extract_json_object(text):
    """Parse a JSON object from raw model output, with code-fence tolerance."""
    if not text:
        raise ValueError("Formatter returned empty output.")

    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
        if candidate.lower().startswith("json"):
            candidate = candidate[4:].strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(candidate[start : end + 1])
        raise


def _format_promoted_output(entry):
    """Convert an approved RCA-style output into the compact knowledge schema."""
    prompt = (
        "Convert the approved incident analysis into a compact knowledge record.\n\n"
        "Return only valid JSON using exactly this schema:\n"
        "{\n"
        '  "title": "...",\n'
        '  "summary": "...",\n'
        '  "description": "...",\n'
        '  "category": "...",\n'
        '  "notes": "..."\n'
        "}\n\n"
        "Rules:\n"
        "- title: short incident label\n"
        "- summary: one concise sentence\n"
        "- description: compact root cause, evidence, and recommended actions\n"
        "- category: one of CPU, Memory, I/O, Network, Others\n"
        "- notes: short retrieval hints or reviewer notes\n"
        "- keep it compact and retrieval-friendly\n"
        "- do not include markdown or extra commentary\n\n"
        f"Original problem statement:\n{entry.get('original_input', '').strip()}\n\n"
        f"Classification:\n{entry.get('classification', '').strip()}\n\n"
        f"Technical analysis:\n{entry.get('analysis', '').strip()}\n\n"
        f"Approved final output:\n{entry.get('final_output', '').strip()}\n\n"
        f"Reviewer notes:\n{entry.get('notes', '').strip()}\n"
    )

    response = call_llm(
        model=KNOWLEDGE_PROMOTION_MODEL,
        system_prompt=(
            "You convert reviewed AI outputs into normalized retrieval knowledge entries. "
            "Return only valid JSON."
        ),
        user_prompt=prompt,
        temperature=0.1,
    )
    formatted = _extract_json_object(response)

    if not isinstance(formatted, dict):
        raise ValueError("Formatter did not return a JSON object.")

    classification = (entry.get("classification") or "").strip()
    category = (formatted.get("category") or classification or "Others").strip()
    if category not in {"CPU", "Memory", "I/O", "Network", "Others"}:
        category = classification if classification in {"CPU", "Memory", "I/O", "Network", "Others"} else "Others"

    notes = (formatted.get("notes") or "").strip()
    reviewer_notes = entry.get("notes", "").strip()
    if reviewer_notes and reviewer_notes not in notes:
        notes = f"{notes}\n\nReviewer notes: {reviewer_notes}".strip() if notes else reviewer_notes

    return {
        "title": str(formatted.get("title", "")).strip(),
        "summary": str(formatted.get("summary", "")).strip(),
        "description": str(formatted.get("description", "")).strip(),
        "category": category,
        "notes": notes,
        "source": entry.get("source", "promoted_output"),
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
    has_manual_fields = all(entry.get(field, "").strip() for field in ("title", "summary", "description"))
    if has_manual_fields:
        normalized_entry = _normalize_knowledge_entry(entry, default_source="promoted_output")
    elif entry.get("auto_format"):
        normalized_entry = _normalize_knowledge_entry(
            _format_promoted_output(entry),
            default_source="promoted_output",
        )
    else:
        raise ValueError(
            "Provide title, summary, and description for manual promotion, "
            "or set auto_format=true with the reviewed output fields."
        )

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
