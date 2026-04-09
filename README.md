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

- [`ai_hackathon/Backend/`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Backend)

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

- [`Backend/README.md`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Backend/README.md)

### Frontend

Location:

- [`ai_hackathon/Frontend/`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend)

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

- [`Frontend/README.md`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend/README.md)

### Frontend2

Location:

- [`ai_hackathon/Frontend2/`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend2)

Purpose:

- alternate frontend implementation

## Recommended Setup Order

1. Set up and run the backend first
2. Start the frontend you want to use
3. Open the frontend in the browser and connect it to the local backend

## Quick Start

### Backend

```bash
cd ai_hackathon/Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py runserver
```

### Frontend

In a new terminal:

```bash
cd ai_hackathon/Frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The frontend expects the backend API to be available locally unless you change the configured base URL in the frontend app.
- The backend depends on valid API credentials and model configuration in its `.env` file.
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
