# Lean AI Hackathon Starter

This project is a small, configurable starter for AI hackathons.

The idea is simple:

- keep the framework code minimal
- customize only the pipeline and prompts
- optionally add a small RAG knowledge file for the specific problem you get

You should not need to create multiple workflows or manage a large config during the hackathon.

## What to edit during the hackathon

In most cases, you only need to touch:

1. `config.py`
2. `app.py`
3. `data/knowledge.json`

## How it works

The pipeline is defined in `config.py` as a list of text steps, and optional
multimodal preprocessing is also defined there.

Each step has:

- `name`: module type such as `classifier`, `reasoner`, or `generator`
- `id`: step output name
- `capability`: `text`, `vision`, or `transcription`
- `prompt`: prompt template
- optional `model`
- optional `system_prompt`
- optional `temperature`
- optional `rag`

Example:

```python
PIPELINE = [
    {
        "name": "classifier",
        "id": "classification",
        "prompt": "Input:\n{original_input}\n\nReturn only a short category label.",
        "temperature": 0.0,
    },
    {
        "name": "reasoner",
        "id": "analysis",
        "rag": True,
        "prompt": "Input:\n{original_input}\n\nCategory:\n{classification}\n\nContext:\n{retrieved_context}",
    },
    {
        "name": "generator",
        "id": "final_output",
        "prompt": "Input:\n{original_input}\n\nAnalysis:\n{analysis}\n\nWrite the final answer.",
    },
]
```

Optional preprocessing steps let you normalize speech and screenshots before the
main text pipeline starts:

```python
PREPROCESSING_PIPELINE = [
    {
        "name": "speech_to_text",
        "id": "speech_transcript",
        "capability": "transcription",
        "model": MODELS["transcription"],
        "input_key": "audio_path",
    },
    {
        "name": "screenshot_analyzer",
        "id": "image_findings",
        "capability": "vision",
        "model": MODELS["vision"],
        "input_key": "image_paths",
        "prompt": "Analyze the screenshot for errors and technical clues.",
    },
]
```

## Available prompt variables

Inside prompts you can use:

- `{input}`
- `{original_input}`
- `{typed_input}`
- `{speech_transcript}`
- `{image_findings}`
- `{multimodal_context}`
- `{previous_output}`
- `{retrieved_context}`
- `{step_outputs_json}`
- `{<step_id>}` from any previous step

Example:

```python
"prompt": "Problem:\n{original_input}\n\nReasoning:\n{analysis}\n\nGenerate final output."
```

## Setup

1. Create a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create `.env`.

```bash
cp .env.example .env
```

4. Fill in:

- `OPENAI_API_KEY`
- `BASE_URL`

Optional:

- `DEFAULT_MODEL`
- `CLASSIFIER_MODEL`
- `GENERATOR_MODEL`
- `REASONING_MODEL`
- `EMBEDDING_MODEL`
- `VISION_MODEL`
- `TRANSCRIPTION_MODEL`
- `KNOWLEDGE_DATA_PATH`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

## Running the project

Edit the `input_text` variable in `app.py`, and optionally set `audio_path` and
`image_paths`, then run:

```bash
python3 app.py
```

Example multimodal run:

```python
result = orchestrator.run(
    input_text="API checkout requests are failing after deployment.",
    audio_path="inputs/issue-note.wav",
    image_paths=["inputs/error-screen.png"],
)
```

## Running The Django API

Install dependencies, then start the server:

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Available endpoints:

- `GET /api/health/`
- `POST /api/process/`
- `POST /api/knowledge/`
- `POST /api/knowledge/promote/`

`POST /api/process/` accepts multipart form data with:

- `text` or `input_text`: optional typed input
- `audio`: optional single audio file
- `images`: optional repeated image files

Example using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/process/ \
  -F "text=Users report payment failures after the last deploy" \
  -F "audio=@inputs/issue-note.wav" \
  -F "images=@inputs/error-screen.png"
```

Manual knowledge entry example:

```bash
curl -X POST http://127.0.0.1:8000/api/knowledge/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Checkout 502 after deploy",
    "summary": "Users hit 502 errors after a new release.",
    "description": "Ingress pointed to a missing service port after deployment. Rolling back and correcting the service mapping resolved it.",
    "category": "Network",
    "notes": "Reviewed by the team during the demo.",
    "source": "manual"
  }'
```

Promote reviewed output example:

```bash
curl -X POST http://127.0.0.1:8000/api/knowledge/promote/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Worker memory growth after queue spike",
    "summary": "Background workers exhausted memory after a burst of jobs.",
    "description": "The most likely cause was unbounded in-memory batching combined with delayed worker recycling.",
    "category": "Memory",
    "notes": "Promoted from a reviewed successful run.",
    "final_output": "Mitigation: reduced batch size, restarted workers, and added memory alerts."
  }'
```

Directory notes:

- `core/`: Django project configuration
- `api/views.py`: DRF endpoints
- `api/services.py`: upload handling plus orchestrator handoff
- `api/serializers.py`: DRF validation for API payloads
- `orchestrator.py`: pipeline entrypoint that routes text, vision, and audio model calls

Knowledge notes:

- The knowledge base defaults to `data/knowledge.json`
- You can override it with `KNOWLEDGE_DATA_PATH=/absolute/or/relative/path.json`
- When a knowledge entry is added or promoted, the API refreshes the cached
  orchestrator so later requests use the updated knowledge file

## Fast customization flow

When you get the actual problem statement:

1. Paste the real problem statement into `app.py`
2. Update the prompts in `config.py`
3. Add 3-10 relevant knowledge entries in `data/knowledge.json`
4. Run `python3 app.py`

That is the intended workflow.

## When to change the pipeline

Use a short 3-step pipeline if you want to move fast:

- classify
- reason
- generate

Use a 4-step pipeline if you need an intermediate draft:

- classifier
- generator
- reasoner
- generator

If the task is simple, you can even remove the classifier step and just keep:

- reasoner
- generator

## RAG guidance

RAG is optional and controlled by `RAG_CONFIG` in `config.py`.

If the problem needs grounding, keep it enabled and add compact entries to `data/knowledge.json`.

If the problem does not need retrieval, set:

```python
RAG_CONFIG = {
    "enabled": False,
    ...
}
```

## Files in the project

- `app.py`: small entry point
- `config.py`: main place to customize the pipeline
- `orchestrator.py`: runs the pipeline
- `modules/llm.py`: text, vision, and transcription model gateway
- `modules/`: minimal module framework
- `data/knowledge.json`: optional RAG context

## Notes

- RAG embeddings are created when the orchestrator starts, so retrieval needs a working embedding model and endpoint.
- The API caches the orchestrator instance to avoid rebuilding embeddings on every request.
- The framework is intentionally small. Most of the customization should happen through prompts.

## Hackathon Suggestions

- Keep the first version of the frontend simple: one text box, optional audio upload, optional image upload, and one result panel.
- Use the `/api/process/` response directly in Streamlit first before adding extra UI polish.
- Treat `/api/knowledge/promote/` as a reviewed action, not an automatic save.
- If the problem statement changes domain, update the prompts in `config.py` first before changing code.
