# Frontend Setup Guide

This frontend is a lightweight web interface built for interacting with the backend analysis APIs.

It provides a simple UI for:

- entering text input
- uploading image files
- recording audio input
- viewing analysis results
- submitting knowledge entries back to the backend

## Tech Stack

- Python
- Streamlit
- `requests` for backend API calls
- `streamlit-mic-recorder` for browser-based audio capture
- `pandas` for lightweight data handling

## Project Files

- [`app.py`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend/app.py): main Streamlit application
- [`requirements.txt`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend/requirements.txt): frontend Python dependencies

## Prerequisites

- Python 3.10+ recommended
- A working backend running locally

The frontend currently expects the backend API at:

```python
http://127.0.0.1:8000/api
```

If your backend runs elsewhere, update `API_BASE` in [`app.py`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend/app.py).

## Setup

From the repository root:

```bash
cd ai_hackathon/Frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Frontend

```bash
streamlit run app.py
```

By default, Streamlit will open a local browser session, usually at:

```text
http://localhost:8501
```

## Run with the Backend

Make sure the backend is already running before you start the frontend.

Typical flow:

1. Start the backend service
2. Start the Streamlit frontend
3. Open the browser UI
4. Submit text, images, or audio for processing

## Features

- Health check for backend availability
- Text-based submission flow
- Multi-image upload
- In-browser audio recording
- Result display for pipeline outputs
- Ability to submit or promote knowledge records

## Customization

The quickest frontend changes usually happen in [`app.py`](/Users/aritro-mac/Documents/VS_Code/GEN-AI-Demo-1/ai_hackathon/Frontend/app.py):

- change the backend base URL
- adjust labels and section text
- add/remove fields from forms
- update layout or styling

## Notes

- This frontend is built as a Streamlit app, so it is best suited for demos, internal tools, and rapid prototyping.
- Audio recording depends on browser microphone permissions.
- If the backend is unavailable, the UI will still load, but API-driven actions will fail until the backend is reachable.
