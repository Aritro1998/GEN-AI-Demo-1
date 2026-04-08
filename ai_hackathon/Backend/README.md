# Multimodal AI Analysis Backend

This repository contains a configurable multimodal backend built for hackathon-style problem solving. It accepts typed input, optional screenshots, and optional audio, converts them into a unified context, runs an LLM pipeline, and returns structured output through both a local runner and REST API endpoints.

## Features

- Text, image, and audio input support
- Config-driven LLM pipeline
- Optional RAG over a local knowledge base
- Django + DRF API endpoints
- Manual knowledge entry creation
- Promotion of reviewed outputs into the knowledge base
- Local runner for direct testing without calling the API

## Architecture

The backend is organized into four layers:

1. `core/`
   Django project configuration, settings, and root URLs.

2. `api/`
   DRF endpoints, request validation, and service helpers for file handling and orchestration.

3. `orchestrator.py`
   Coordinates preprocessing and the main pipeline.

4. `modules/`
   Shared model gateway and text pipeline modules.

### Processing Flow

1. User submits typed text, optional audio, and optional screenshots.
2. Audio is transcribed with the configured transcription model.
3. Screenshots are analyzed with the configured vision model.
4. All available inputs are merged into one combined context.
5. The text pipeline runs through:
   - `classifier`
   - `reasoner`
   - `generator`
6. The result is returned to the caller.

If RAG is enabled, the reasoning step can also retrieve supporting context from the configured knowledge base.

## Project Structure

```text
Backend/
├── api/
│   ├── apps.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── core/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── data/
│   └── knowledge.json
├── modules/
│   ├── base_module.py
│   ├── classifier.py
│   ├── generator.py
│   ├── llm.py
│   ├── module_factory.py
│   ├── rag.py
│   └── reasoner.py
├── utils/
│   └── similarity.py
├── app.py
├── config.py
├── manage.py
├── orchestrator.py
└── requirements.txt
```

## Configuration

The main runtime configuration lives in `config.py`.

### Model Configuration

The following model slots are supported:

- `DEFAULT_MODEL`
- `CLASSIFIER_MODEL`
- `REASONING_MODEL`
- `GENERATOR_MODEL`
- `EMBEDDING_MODEL`
- `VISION_MODEL`
- `TRANSCRIPTION_MODEL`

### Knowledge Base Configuration

The knowledge file path is configurable through:

- `KNOWLEDGE_DATA_PATH`

If not provided, it defaults to:

```text
data/knowledge.json
```

### Django Configuration

Optional environment variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

## Prompt Variables

Prompt templates in `config.py` can use:

- `{input}`
- `{original_input}`
- `{typed_input}`
- `{speech_transcript}`
- `{image_findings}`
- `{multimodal_context}`
- `{previous_output}`
- `{retrieved_context}`
- `{step_outputs_json}`
- `{<step_id>}` from previous steps

## Setup

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create the environment file.

```bash
cp .env.example .env
```

4. Configure at least:

- `OPENAI_API_KEY`
- `BASE_URL`

## Running Locally Without API

The file `app.py` can be used to test the pipeline directly.

```bash
python3 app.py
```

Edit the following variables in `app.py` as needed:

- `input_text`
- `audio_path`
- `image_paths`

## Running The API

Start the Django development server:

```bash
python3 manage.py migrate
python3 manage.py runserver
```

Default local base URL:

```text
http://127.0.0.1:8000
```

## API Endpoints

### `GET /api/health/`

Returns a simple health response.

Example response:

```json
{
  "status": "ok"
}
```

### `POST /api/process/`

Accepts multipart form data and runs the multimodal pipeline.

Supported fields:

- `text` or `input_text`
- `audio`
- `images` (repeatable)

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/process/ \
  -F "text=Users report payment failures after the latest deploy" \
  -F "audio=@inputs/issue-note.wav" \
  -F "images=@inputs/error-screen.png"
```

### `POST /api/knowledge/`

Adds a reviewed manual knowledge entry to the knowledge base.

Example payload:

```json
{
  "title": "Checkout 502 after deploy",
  "summary": "Users hit 502 errors after a new release.",
  "description": "Ingress pointed to a missing service port after deployment. Rolling back and correcting the service mapping resolved it.",
  "category": "Network",
  "notes": "Reviewed manually.",
  "source": "manual"
}
```

### `POST /api/knowledge/promote/`

Promotes a reviewed output into the knowledge base.

Example payload:

```json
{
  "title": "Worker memory growth after queue spike",
  "summary": "Background workers exhausted memory after a burst of jobs.",
  "description": "The most likely cause was unbounded in-memory batching combined with delayed worker recycling.",
  "category": "Memory",
  "notes": "Promoted from a reviewed successful run.",
  "final_output": "Mitigation: reduced batch size, restarted workers, and added memory alerts.",
  "source": "promoted_output"
}
```

## Knowledge Base

The backend uses a JSON knowledge store for retrieval and approved knowledge capture.

- Default file: `data/knowledge.json`
- Path can be overridden with `KNOWLEDGE_DATA_PATH`
- New entries are written through the API service layer
- Duplicate entries are skipped using a lightweight title + summary match
- When knowledge changes, the cached orchestrator is refreshed so later requests use the updated data

## Notes

- The API uses DRF `APIView` classes with multipart parsing for file uploads.
- The orchestrator instance is cached to avoid rebuilding embeddings on every API request.
- The RAG layer expects a working embedding endpoint when retrieval is enabled.
- `app.py` is intentionally kept for non-endpoint testing and debugging.

## Submission Summary

This backend provides:

- multimodal input ingestion
- configurable LLM orchestration
- API-based execution
- persistent reviewed knowledge capture
- a lightweight structure suitable for rapid adaptation to changing problem statements
