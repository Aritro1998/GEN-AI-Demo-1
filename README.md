# Project Overview

This repository contains a small AI application stack with separate backend and frontend components.

It is organized for rapid iteration and demo-oriented workflows, with a configurable backend pipeline and lightweight Streamlit frontends.

## Project Structure

```text
GEN-AI-Demo-1/
├── ai_hackathon/
│   ├── Backend/
│   ├── Frontend/
│   ├── Frontend2/
│   └── requirements.txt
└── README.md
```

## Components

### Backend

Location:

- [`ai_hackathon/Backend/`](ai_hackathon/Backend/)

Purpose:

- handles the AI pipeline
- exposes API endpoints
- supports local testing without the frontend
- manages retrieval knowledge and promoted outputs

Tech stack:

- Python
- Django
- Django REST Framework
- OpenAI-compatible API client
- NumPy

Backend guide:

- [`Backend/README.md`](ai_hackathon/Backend/README.md)

### Frontend

Location:

- [`ai_hackathon/Frontend/`](ai_hackathon/Frontend/)

Purpose:

- provides a browser-based UI for interacting with the backend
- supports text, image, and audio-driven input flows
- displays results returned by the backend APIs

Tech stack:

- Python
- Streamlit
- Requests
- Streamlit mic recorder

Frontend guide:

- [`Frontend/README.md`](ai_hackathon/Frontend/README.md)

### Frontend2

Location:

- `ai_hackathon/Frontend2/`

Purpose:

- alternate frontend implementation

## Recommended Setup Order

1. Set up and run the backend first
2. Start the frontend you want to use
3. Open the frontend in the browser and connect it to the local backend

## Quick Start

Create one shared virtual environment for both backend and frontend:

```bash
cd ai_hackathon
python -m venv .venv
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

### Backend

```bash
cd ai_hackathon/Backend
cp .env.example .env
python3 manage.py migrate
python3 manage.py runserver
```

### Frontend

In a new terminal:

```bash
cd ai_hackathon/Frontend
streamlit run app.py
```

## Notes

- The frontend expects the backend API to be available locally unless you change the configured base URL in the frontend app.
- The backend depends on valid API credentials and model configuration in its `.env` file.
- The shared environment dependencies are installed from [`ai_hackathon/requirements.txt`](ai_hackathon/requirements.txt).
- For detailed setup instructions, use the component-specific README files.

## Presentation Note

One of the key architectural strengths of this project is the configurable backend pipeline.

Instead of hardcoding a single flow, the backend is designed so the pipeline can be changed through configuration by adjusting:

- step order
- prompts
- model selection
- retrieval usage

This makes the system easier to adapt to different problem statements without rewriting the core orchestration code.

For demos or presentations, this can be described as a reusable AI workflow framework rather than a one-off implementation.
