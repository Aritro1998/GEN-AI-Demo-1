# Policy Lens — Backend

Multi-tenant insurance policy platform with AI-powered Q&A and recommendations.

## Tech Stack

- **Django** + **Django REST Framework** — API and auth
- **SQLite** — database (categories, tiers, documents, chunks, user policies)
- **OpenAI API** — embeddings (text-embedding-3-large) + chat (GPT-4o)
- **PyPDF2** — PDF text extraction
- **tiktoken** — token-based chunking
- **NumPy** — cosine similarity

## Quick Start

```bash
# From ai_hackathon/ directory
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
pip install -r requirements.txt

cd Backend
cp .env.example .env                # Edit with your API key
python manage.py migrate
python manage.py createsuperuser    # Create admin user
python manage.py seed_demo          # Seed demo data
python manage.py runserver
```

## Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | — |
| `BASE_URL` | Yes | — |
| `DEFAULT_MODEL` | No | genailab-maas-gpt-4o |
| `EMBEDDING_MODEL` | No | azure/genailab-maas-text-embedding-3-large |

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/health/ | — | Health check |
| POST | /api/auth/login/ | — | Login → token |
| POST | /api/auth/logout/ | Token | Logout |
| GET | /api/auth/me/ | Token | Current user |
| GET | /api/dashboard/ | Token | User + policies + recommendation summary |
| GET | /api/my-policies/ | Token | List active policies |
| GET | /api/my-policies/\<id\>/ | Token | Policy detail |
| POST | /api/my-policies/\<id\>/query/ | Token | Scoped Q&A |
| POST | /api/query/ | Token | Auto-routed Q&A |
| GET | /api/recommendations/ | Token | Upgrade + loan suggestions |
| POST | /api/upload-policy/ | Admin | Upload PDF for a tier |

## Demo Workflow

1. **Admin** logs in → uploads PDFs for each tier via `/api/upload-policy/`
2. **Admin** assigns users to tiers via `/admin/` panel
3. **User** logs in → sees dashboard → chats with their policies → views recommendations

## Demo Accounts

| Username | Password | Role | Policies |
|----------|----------|------|----------|
| admin | admin123 | Superuser | — |
| swarnali | swarnali123 | User | Car Gold, Health Silver |
| aritro | aritro123 | User | Car Silver, Life Gold |

## Project Structure

See [`architecture.md`](architecture.md) for the full Mermaid diagram and file map.
