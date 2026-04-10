# 🔍 Policy Lens — Architecture Overview

> **AI-Powered Insurance Policy Platform** — Manage policies, get instant AI answers, and receive smart upgrade & loan recommendations grounded in actual policy documents.

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    subgraph Frontend["🖥️ Frontend (Streamlit)"]
        direction TB
        LP["Login Page\n+ Our Offerings"]
        DB["Dashboard\n• Policy Cards\n• Recommendations\n• Offerings"]
        MP["My Policies\n• Detail View\n• PDF Download"]
        QA["AI Q&A Chat\n• Policy-Scoped\n• Conversation History"]
        REC["Recommendations\n• Upgrade\n• Loan"]
    end

    subgraph Backend["⚙️ Backend (Django REST)"]
        direction TB
        AUTH["🔐 Auth Layer\nToken-Based Login"]
        API["📡 REST API\n13 Endpoints"]
        SVC["🧠 Service Layer\nPolicy Routing\nFull-Doc Detection"]
        RECENG["⭐ Recommendation\nEngine"]
    end

    subgraph AI["🤖 AI Engine"]
        direction TB
        RAG["📚 Per-Tier RAG\nVector Index\n(Cached In-Memory)"]
        EMB["Embeddings\ntext-embedding-3-large"]
        LLM["Chat Completion\nGPT-4o"]
    end

    subgraph Data["💾 Data Layer"]
        direction TB
        SQLITE["SQLite DB\n6 Models"]
        PDF["PDF Storage\n9 Policy Documents"]
        CHUNKS["Policy Chunks\nTokenized & Indexed"]
    end

    Frontend -->|"HTTPS / Token Auth"| Backend
    Backend -->|"RAG Retrieval"| AI
    Backend -->|"ORM Queries"| Data
    AI -->|"OpenAI API"| EMB
    AI -->|"OpenAI API"| LLM
    RAG --> CHUNKS
```

---

## 🌟 Key Wow Factors

### 1. 🧠 Document-Grounded AI Recommendations
> **Not just rule-based** — The system pulls actual policy document excerpts and feeds them to GPT-4o, generating recommendations that cite specific coverages, limits, and benefits from real documents.

```mermaid
flowchart LR
    A["User's Silver Plan\n(Document Chunks)"] --> C["GPT-4o\nComparison Engine"]
    B["Gold Plan\n(Document Chunks)"] --> C
    C --> D["'Your Silver plan covers ₹2L.\nGold adds ₹5L + dental\n+ zero co-pay...'"]
```

### 2. 🔍 Smart Policy Routing
> User asks a question → system auto-detects which policy category (Car/Health/Life) is relevant and routes to the correct RAG index. No manual selection needed.

### 3. 📄 Full-Document Intelligence
> Detects when users ask for complete policy details ("Show my entire policy") and serves ALL document chunks to the LLM — not just top-K excerpts — for a comprehensive structured summary.

### 4. 🛡️ Content Safety Pipeline
> Automatic sanitization of medical/sensitive terms before LLM calls to prevent content-filter blocks, with graceful fallback to rule-based responses if the LLM is unavailable.

### 5. ⚡ Per-Tier RAG Caching
> Each policy tier gets its own in-memory vector index. Once built, queries are instant — no re-embedding on every request.

---

## 📐 Detailed Data Flow

### User Query Flow
```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 🖥️ Streamlit
    participant A as ⚙️ Django API
    participant S as 🧠 Service Layer
    participant R as 📚 RAG Engine
    participant L as 🤖 GPT-4o

    U->>F: Types question
    F->>A: POST /api/my-policies/{id}/query/
    A->>S: query_policy(user, question)
    S->>S: Detect intent (full-doc vs Q&A)
    S->>S: Auto-detect category
    S->>R: Retrieve chunks (top-K or ALL)
    R->>R: Cosine similarity search
    S->>S: Sanitize for content safety
    S->>L: Context + Question → GPT-4o
    L-->>S: Generated answer
    S-->>A: Answer + Sources
    A-->>F: JSON response
    F-->>U: Rendered answer + citations
```

### Recommendation Flow
```mermaid
sequenceDiagram
    participant U as 👤 User
    participant F as 🖥️ Streamlit
    participant A as ⚙️ Django API
    participant RE as ⭐ Rec Engine
    participant DB as 💾 Database
    participant L as 🤖 GPT-4o

    U->>F: Opens Dashboard
    F->>A: GET /api/recommendations/
    A->>RE: get_recommendations_for_user()
    RE->>DB: Fetch user policies + tier ladder
    RE->>DB: Pull document excerpts (current + upgrade tier)
    RE->>RE: Sanitize excerpts
    RE->>L: Excerpts + metadata → GPT-4o
    L-->>RE: Grounded recommendation text
    RE-->>A: Recommendations[]
    A-->>F: JSON response
    F-->>U: Upgrade & Loan cards with AI descriptions
```

---

## 🗄️ Data Model

```mermaid
erDiagram
    User ||--o{ UserPolicy : "has"
    User ||--o| Token : "authenticates with"
    PolicyCategory ||--o{ PolicyTier : "contains"
    PolicyTier ||--o{ PolicyDocument : "has"
    PolicyDocument ||--o{ PolicyChunk : "split into"
    PolicyTier ||--o{ UserPolicy : "assigned to"

    PolicyCategory {
        string name
        string description
        string icon
    }
    PolicyTier {
        string name "silver|gold|platinum"
        string display_name
        decimal price_monthly
        text highlights
    }
    PolicyDocument {
        string file_name
        file pdf_file
        int page_count
    }
    PolicyChunk {
        int chunk_index
        int page
        text text
    }
    UserPolicy {
        string policy_number
        date start_date
        date end_date
        bool is_active
    }
```

---

## 🖥️ Frontend Pages

| Page | Key Features |
|------|-------------|
| **Login** | Hero branding, product highlights, Our Offerings grid (3 categories × 3 tiers), credentials form |
| **Dashboard** | Policy cards, inline AI recommendations (upgrade + loan), full offerings catalog |
| **My Policies** | Expandable detail cards, PDF download, "Ask about this policy" button |
| **AI Q&A** | Chat interface with conversation history, policy-scoped or auto-routed, source citations |
| **Recommendations** | UPGRADE / LOAN badges, price comparisons, document-backed reasoning |

---

## ⚙️ Backend API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/health/` | — | Health check |
| POST | `/api/auth/login/` | — | Token login |
| POST | `/api/auth/logout/` | Token | Logout |
| GET | `/api/auth/me/` | Token | Current user |
| GET | `/api/dashboard/` | Token | Dashboard data |
| GET | `/api/my-policies/` | Token | User's policies |
| GET | `/api/my-policies/<id>/` | Token | Policy detail |
| GET | `/api/my-policies/<id>/document/` | Token | PDF download |
| POST | `/api/my-policies/<id>/query/` | Token | Scoped AI Q&A |
| POST | `/api/query/` | Token | Auto-routed AI Q&A |
| GET | `/api/recommendations/` | Token | AI recommendations |
| GET | `/api/offerings/` | — | All plans & pricing |
| POST | `/api/upload-policy/` | Admin | Upload tier PDF |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit, Custom CSS, Inter font |
| **Backend** | Django 6.0, Django REST Framework |
| **Database** | SQLite (6 models) |
| **AI/ML** | OpenAI GPT-4o (chat), text-embedding-3-large (embeddings) |
| **PDF Processing** | PyPDF2 (extraction), tiktoken (chunking) |
| **RAG** | Custom in-memory vector index with cosine similarity |
| **Auth** | DRF TokenAuthentication |
| **Admin** | Django Admin panel |

---

## 📁 Project Structure

```
ai_hackathon/
├── Backend/
│   ├── config.py                    # Models, prompts, RAG config
│   ├── manage.py
│   ├── api/
│   │   ├── models.py                # 6 Django models
│   │   ├── views.py                 # 9 API views
│   │   ├── auth_views.py            # Login/Logout/Me
│   │   ├── serializers.py           # Request validation
│   │   ├── policy_services.py       # Core logic: ingest, query, routing
│   │   ├── urls.py                  # 13 endpoints
│   │   ├── admin.py                 # Admin panel config
│   │   └── management/commands/
│   │       ├── seed_demo.py         # Demo data seeder
│   │       └── upload_policies.py   # Bulk PDF uploader
│   ├── modules/
│   │   ├── llm.py                   # OpenAI client wrapper
│   │   ├── pdf_ingestion.py         # PDF → text extraction
│   │   ├── chunker.py              # Token-based overlapping chunker
│   │   ├── policy_rag.py           # Per-tier vector index
│   │   └── recommendations.py      # Upgrade + loan engine with doc excerpts
│   ├── core/
│   │   ├── settings.py              # Django config
│   │   └── urls.py                  # Root routing
│   └── utils/
│       └── similarity.py            # Cosine similarity
├── Frontend/
│   ├── app.py                       # Full Streamlit app (5 pages, custom CSS)
│   └── requirements.txt
└── Policy Plan/                     # Source PDFs (9 documents)
    ├── Vehicle Insurance/           # Silver, Gold, Platinum
    ├── Health Insurance/            # Silver, Gold, Platinum
    └── Life Insurance/              # Silver, Gold, Platinum
```

---

## 📊 Demo Users

| User | Password | Policies | Recommendations |
|------|----------|----------|-----------------|
| **swarnali** | swarnali123 | Car Gold, Health Silver | Car → Platinum, Health → Gold, Car Loan |
| **aritro** | aritro123 | Car Silver, Life Gold | Car → Gold, Life → Platinum, Life Loan |

---

## 🔑 What Makes This Different

| Feature | Traditional Approach | Policy Lens |
|---------|---------------------|-------------|
| **Recommendations** | Generic "upgrade now" messages | AI compares actual plan documents, cites specific benefits |
| **Policy Q&A** | FAQ page or call center | RAG-powered instant answers from your actual policy PDF |
| **Full Document View** | Download and read 10+ page PDF | AI detects intent, summarizes entire policy in structured format |
| **Multi-Policy Routing** | User must select which policy | Auto-detects category from question keywords |
| **Content Safety** | Crashes on blocked content | Auto-sanitizes + graceful fallback to rule-based responses |
