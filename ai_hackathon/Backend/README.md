# Backend Setup Guide

This backend is a configurable Python service for running a multi-step AI analysis pipeline.

It supports:

- text input
- optional image input
- optional audio input
- retrieval-augmented generation over a local knowledge file
- API-based execution through Django and Django REST Framework
- direct local execution through a small runner script

## Tech Stack

- Python
- Django
- Django REST Framework
- OpenAI-compatible API client
- NumPy
- `python-dotenv`

## Project Structure

```text
Backend/
├── api/
├── core/
├── data/
├── modules/
├── utils/
├── app.py
├── config.py
├── manage.py
├── orchestrator.py
└── requirements.txt
```

Main files:

- [`app.py`](app.py): local runner for testing without the API
- [`config.py`](config.py): pipeline and model configuration
- [`orchestrator.py`](orchestrator.py): main execution flow
- [`api/`](api): REST API layer
- [`modules/`](modules): pipeline modules and shared LLM/RAG helpers
- [`data/knowledge.json`](data/knowledge.json): local RAG knowledge store

## Setup

Use one shared environment for the whole project.

From the repository root:

```bash
cd ai_hackathon
python3 -m venv .venv
```

Activate it with the command for your OS:

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Install the shared dependencies:

```bash
pip install -r requirements.txt
```

Then go to the backend folder:

```bash
cd Backend
```

Create your environment file:

```bash
cp .env.example .env
```

At minimum, configure:

- `OPENAI_API_KEY`
- `BASE_URL`

Common optional variables:

- `DEFAULT_MODEL`
- `CLASSIFIER_MODEL`
- `REASONING_MODEL`
- `GENERATOR_MODEL`
- `EMBEDDING_MODEL`
- `VISION_MODEL`
- `TRANSCRIPTION_MODEL`
- `KNOWLEDGE_DATA_PATH`
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

## Running Locally

To test the backend without starting the API server:

```bash
python3 app.py
```

Update the sample inputs inside [`app.py`](app.py) as needed:

- `input_text`
- `audio_path`
- `image_paths`

## Running the API

Apply migrations and start the Django development server:

```bash
python3 manage.py migrate
python3 manage.py runserver
```

Default local URL:

```text
http://127.0.0.1:8000
```

## API Endpoints

Base API path:

```text
http://127.0.0.1:8000/api
```

Main endpoints:

- `GET /api/health/`
- `POST /api/process/`
- `POST /api/knowledge/`
- `POST /api/knowledge/promote/`

## Processing Flow

The backend follows a configurable pipeline model:

1. collect typed input
2. optionally transcribe audio
3. optionally analyze images
4. merge the available context
5. run the configured LLM pipeline steps
6. optionally use RAG during the configured step
7. return structured output

## Configuration Notes

The main configuration surface is [`config.py`](config.py).

Prompt templates can reference values such as:

- `{input}`
- `{original_input}`
- `{typed_input}`
- `{speech_transcript}`
- `{image_findings}`
- `{multimodal_context}`
- `{previous_output}`
- `{retrieved_context}`
- `{step_outputs_json}`
- outputs from previous step IDs

## Knowledge Base

The backend can use a local JSON knowledge file for retrieval and promoted knowledge entries.

Default path:

```text
data/knowledge.json
```

You can keep it small and update it based on the problem statement or demo scenario you are working on.

## Notes

- This backend is optimized for flexibility and quick iteration.
- The local runner is useful for testing prompts and pipeline behavior before wiring up the frontend.
- If the configured API endpoint or model IDs are invalid, the backend will fail at runtime even if setup is otherwise correct.
- The project uses the shared dependency file at [`../requirements.txt`](../requirements.txt) for both backend and frontend.
