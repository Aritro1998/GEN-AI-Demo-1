# PolicyHub — Frontend

Streamlit-based UI for the insurance policy platform.

## Features

- **Login** — token-based auth with session persistence
- **Dashboard** — policy cards, metrics, recommendation summary
- **My Policies** — expandable detail view per policy
- **Ask a Question** — chat interface with policy scoping and conversation history
- **Recommendations** — LLM-generated upgrade and loan suggestions

## Tech Stack

- **Streamlit** — UI framework
- **requests** — API calls to Django backend

## Quick Start

```bash
# From ai_hackathon/ directory (with venv active)
cd Frontend
streamlit run app.py
```

Opens at `http://localhost:8501`. Backend must be running on port 8000.

## Demo Accounts

| Username | Password | Policies |
|----------|----------|----------|
| alice | alice123 | Car Gold, Health Silver |
| bob | bob123 | Car Silver, Home Gold |

## Configuration

Edit `API_BASE` in `app.py` if the backend runs on a different host/port.
