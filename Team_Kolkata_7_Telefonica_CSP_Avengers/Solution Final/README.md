# Incident Summarizer Agent (v1)

A Streamlit prototype that ingests raw IT tickets and generates concise, structured incident summaries using `gpt-4o-mini`.

## What this version includes
- Ticket ingestion from:
  - local mock JSON (`mock_data.json`)
  - uploaded JSON/CSV
  - pasted JSON payload (API-style ingestion)
  - synthetic data generator
- AI-generated structured summary per ticket:
  - Situation Summary
  - Impact Scope
  - Priority Cue
  - Recommended Next Steps
- Queue metrics:
  - total tickets
  - critical ticket count
  - estimated time saved
- Export:
  - all summaries to CSV
  - stakeholder update to TXT

## 1) Configure `.env`
Use your existing values. Supported key names are both upper and lower case:

```env
api_key=YOUR_AZURE_OPENAI_KEY
api_endpoint=https://YOUR-RESOURCE-NAME.openai.azure.com/
model=gpt-4o-mini
```

Also supported:
- `API_KEY`
- `API_ENDPOINT`
- `MODEL_NAME`

## 2) Install dependencies
```bash
pip install -r requirements.txt
```

## 3) Run the app
```bash
streamlit run main.py
```

## Suggested first demo flow
1. Click `Load Mock JSON`.
2. Select a ticket and click `Generate Summary`.
3. Download `incident_summaries.csv`.
4. Generate synthetic tickets and repeat to show scale.

## Notes
- This prototype uses Azure OpenAI client configuration.
- If API settings are missing, the app still loads and allows data ingestion, but summary generation is disabled.
