import os
import re
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import requests  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

try:
    import faiss  # type: ignore

    HAS_FAISS = True
except Exception:
    faiss = None
    HAS_FAISS = False

DEFAULT_API_ENDPOINT = "https://genailab.tcs.in/v1/chat/completions"
API_ENDPOINT = os.getenv("GENAILAB_API_ENDPOINT", DEFAULT_API_ENDPOINT)
API_KEY = os.getenv("GENAILAB_API_KEY", "").strip()
MODEL_NAME = os.getenv("GENAILAB_MODEL", "azure/genailab-maas-gpt-4.1")

DEFAULT_TICKET_KB_PATH = "data/incidents.csv"
DEFAULT_ITIL_KB_PATH = "data/itil_reference.txt"

REQUIRED_COLUMNS = {
    "incident_id",
    "description",
    "priority",
    "created_at",
    "resolution_notes",
}

COLUMN_ALIASES = {
    "incident_id": {
        "incident_id",
        "incidentid",
        "incident",
        "incident_no",
        "incidentnumber",
        "ticket_id",
        "ticketid",
        "ticket_no",
        "id",
    },
    "description": {
        "description",
        "issue_description",
        "issue",
        "problem_description",
        "details",
        "summary",
    },
    "priority": {
        "priority",
        "severity",
        "impact_level",
    },
    "created_at": {
        "created_at",
        "createdon",
        "created_date",
        "timestamp",
        "reported_on",
        "reported_at",
        "opened_at",
        "opened_on",
    },
    "resolution_notes": {
        "resolution_notes",
        "resolution_note",
        "resolution",
        "resolutiondetails",
        "fix_notes",
        "closure_notes",
        "notes",
    },
}

DEFAULT_ITIL_SNIPPETS = [
    "Prioritize incidents by business impact and urgency so restoration actions can be sequenced quickly and transparently.",
    "For high or critical incidents, establish immediate containment first, then apply a stable fix, and document verification evidence.",
    "Use known-error patterns from prior incidents to accelerate diagnosis and reduce mean time to resolution.",
    "After service restoration, monitor key service indicators to confirm stability and prevent silent recurrence.",
    "Capture root cause, corrective action, and preventive action in closure notes so future incidents can be handled faster.",
]

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "this",
    "that",
    "were",
    "was",
    "are",
    "is",
    "into",
    "during",
    "after",
    "before",
    "when",
    "where",
    "while",
    "users",
    "user",
    "service",
    "system",
    "issue",
    "error",
    "incident",
}

ISSUE_FAMILY_KEYWORDS = {
    "database": {"database", "db", "sql", "query", "replication", "schema", "index"},
    "network": {"network", "dns", "vpn", "packet", "latency", "bandwidth", "routing"},
    "api": {"api", "endpoint", "gateway", "json", "token", "auth", "throttling"},
    "ui": {"ui", "dashboard", "button", "form", "css", "frontend", "mobile"},
    "infra": {"disk", "storage", "cpu", "memory", "server", "failover", "backup"},
    "security": {"firewall", "ssl", "certificate", "authorization", "authentication"},
}


def _normalize_col_name(name: str) -> str:
    return "".join(ch for ch in str(name).lower().strip() if ch.isalnum())


def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    used_targets = set()

    for col in df.columns:
        normalized = _normalize_col_name(col)
        for target, aliases in COLUMN_ALIASES.items():
            normalized_aliases = {_normalize_col_name(a) for a in aliases}
            if normalized in normalized_aliases and target not in used_targets:
                rename_map[col] = target
                used_targets.add(target)
                break

    if rename_map:
        return df.rename(columns=rename_map)
    return df


def normalize_priority(priority: str) -> str:
    value = str(priority).strip().title()
    if value not in {"Low", "Medium", "High", "Critical"}:
        return "Medium"
    return value


def _normalize_text_for_retrieval(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_keywords(text: str, max_terms: int = 12) -> List[str]:
    normalized = _normalize_text_for_retrieval(text)
    terms = []
    seen = set()
    for token in normalized.split():
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        terms.append(token)
        if len(terms) >= max_terms:
            break
    return terms


def _infer_issue_family(text: str) -> str:
    normalized = _normalize_text_for_retrieval(text)
    tokens = set(normalized.split())
    best_family = "general"
    best_score = 0
    for family, keywords in ISSUE_FAMILY_KEYWORDS.items():
        score = len(tokens.intersection(keywords))
        if score > best_score:
            best_family = family
            best_score = score
    return best_family


def _expand_query_text(issue_text: str, issue_family: str) -> str:
    family_terms = ISSUE_FAMILY_KEYWORDS.get(issue_family, set())
    if not family_terms:
        return issue_text
    expansion = " ".join(sorted(family_terms))
    return f"{issue_text} related_terms {expansion}"


def preprocess(ticket: Dict[str, str]) -> str:
    return f"""
Incident ID: {ticket.get("incident_id", "Unknown")}
Description: {ticket.get("description", "No description provided")}
Priority: {normalize_priority(ticket.get("priority", "Medium"))}
Created At: {ticket.get("created_at", "Unknown")}
Resolution Notes: {ticket.get("resolution_notes", "No resolution notes provided")}
"""


def generate_fallback_summary(ticket: Dict[str, str]) -> str:
    incident_id = ticket.get("incident_id", "Unknown")
    description = ticket.get("description", "No description provided")
    priority = normalize_priority(ticket.get("priority", "Medium"))
    created_at = ticket.get("created_at", "Unknown")
    resolution_notes = ticket.get("resolution_notes", "No resolution notes provided")

    impact_line = (
        "Business users experienced degraded service for this workflow."
        if priority in {"High", "Critical"}
        else "A limited user segment experienced disruption, with manageable business impact."
    )

    return f"""Incident Summary - {incident_id}

Issue: {description}

Impact: {impact_line}

Priority: {priority}

Reported On: {created_at}

Resolution:
The support team identified the likely failure point and applied corrective actions.
{resolution_notes}.
Post-fix checks were completed to confirm expected service behavior.

Current Status:
The incident is marked as resolved and services are operating normally.
The team will continue monitoring for recurrence and trend signals.
"""


def _call_chat_model(prompt: str, temperature: float = 0.3) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    response = requests.post(
        API_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    return body["choices"][0]["message"]["content"].strip()


def generate_summary(ticket: Dict[str, str]) -> Tuple[str, str]:
    text = preprocess(ticket)
    prompt = f"""
You are an IT incident management assistant.

Your task is to convert the given incident ticket into a clear, non-technical, and business-friendly summary.
The output should be easy for managers and non-technical stakeholders to understand.

Guidelines:
- DO NOT copy sentences directly from the input.
- Rephrase and simplify all fields, especially the Issue.
- The Issue must be one complete sentence (around 15-25 words) in plain business language.
- The Issue must NOT reuse 4 or more consecutive words from the Description.
- The Issue must explain the customer/business effect, not internal technical wording.
- Avoid technical jargon as much as possible.
- Explain Resolution and Current Status in a slightly elaborated, easy-to-understand way (2-3 lines each).
- If Root Cause is not explicitly provided, infer a reasonable explanation.
- Keep the tone professional and concise.
- Do not include any extra headings or explanations outside the format.

Issue rewrite quality example:
- Bad: "Database replication lag causing stale data"
- Good: "A delay in database synchronization caused users to see outdated information instead of the latest updates."
- Before finalizing, self-check and rewrite if the Issue sounds copied from input.

Input Ticket:
{text}

Output Format:

Incident Summary - <incident_id>

Issue: <rewrite the issue in simple, user-friendly language (do not copy input text)>

Impact: <who/what was affected in simple terms>

Priority: <priority level>

Reported On: <created_at in readable format>

Resolution:
<2-3 lines explaining what was done in simple, non-technical language>

Current Status:
<2-3 lines confirming system is stable and any monitoring steps>
"""

    if not API_KEY:
        return generate_fallback_summary(ticket), "Fallback"

    try:
        return _call_chat_model(prompt, temperature=0.3), "LLM API"
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return generate_fallback_summary(ticket), "Fallback"


def _validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_cols}")


def prepare_ticket_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    canonical_df = _canonicalize_columns(df.copy())
    _validate_columns(canonical_df)
    return canonical_df.fillna("")


def process_dataframe(df: pd.DataFrame) -> List[Dict[str, str]]:
    cleaned = prepare_ticket_dataframe(df)
    summaries = []

    for _, row in cleaned.iterrows():
        ticket = {
            "incident_id": str(row.get("incident_id", "")).strip(),
            "description": str(row.get("description", "")).strip(),
            "priority": str(row.get("priority", "")).strip(),
            "created_at": str(row.get("created_at", "")).strip(),
            "resolution_notes": str(row.get("resolution_notes", "")).strip(),
        }
        summary, source = generate_summary(ticket)
        summaries.append(
            {
                "incident_id": ticket["incident_id"] or "Unknown",
                "priority": normalize_priority(ticket["priority"]),
                "reported_on": ticket["created_at"] or "Unknown",
                "summary": summary,
                "source": source,
            }
        )

    return summaries


def process_csv(file_path: str) -> List[Dict[str, str]]:
    df = pd.read_csv(file_path)
    return process_dataframe(df)


def ingest_tickets_from_api(
    api_url: str,
    bearer_token: str = "",
    timeout_seconds: int = 30,
) -> pd.DataFrame:
    if not api_url.strip():
        raise ValueError("API URL is required.")

    headers = {}
    if bearer_token.strip():
        headers["Authorization"] = f"Bearer {bearer_token.strip()}"

    response = requests.get(api_url.strip(), headers=headers, timeout=timeout_seconds)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()

    if "application/json" in content_type or response.text.strip().startswith(("{", "[")):
        payload = response.json()
        if isinstance(payload, dict):
            for key in ("incidents", "tickets", "data", "items", "results"):
                if key in payload and isinstance(payload[key], list):
                    payload = payload[key]
                    break
            else:
                payload = [payload]
        if not isinstance(payload, list):
            raise ValueError("API JSON payload must be a list of ticket objects.")
        df = pd.DataFrame(payload)
    else:
        df = pd.read_csv(StringIO(response.text))

    return prepare_ticket_dataframe(df)


class IncidentRAGEngine:
    def __init__(
        self,
        ticket_kb_path: str = DEFAULT_TICKET_KB_PATH,
        itil_kb_path: str = DEFAULT_ITIL_KB_PATH,
        ticket_df: Optional[pd.DataFrame] = None,
    ):
        self.ticket_kb_path = ticket_kb_path
        self.itil_kb_path = itil_kb_path
        self.ticket_df = ticket_df
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=7000,
        )
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index: Optional[Any] = None
        self._build_index()

    def _build_index(self) -> None:
        ticket_docs = self._load_ticket_documents()
        itil_docs = self._load_itil_documents()
        self.documents = ticket_docs + itil_docs

        if not self.documents:
            raise ValueError("RAG knowledge base is empty.")

        corpus = [doc["text"] for doc in self.documents]
        matrix = self.vectorizer.fit_transform(corpus).astype(np.float32)
        dense = matrix.toarray().astype(np.float32)
        dense = self._l2_normalize(dense)
        self.embeddings = dense

        if HAS_FAISS and faiss is not None and dense.shape[0] > 0:
            index = faiss.IndexFlatIP(dense.shape[1])
            index.add(dense)
            self.faiss_index = index

    def _load_ticket_documents(self) -> List[Dict[str, Any]]:
        if self.ticket_df is not None:
            cleaned = prepare_ticket_dataframe(self.ticket_df)
        else:
            path = Path(self.ticket_kb_path)
            if not path.exists():
                raise ValueError(f"Ticket KB not found at {self.ticket_kb_path}")
            df = pd.read_csv(path)
            cleaned = prepare_ticket_dataframe(df)

        docs: List[Dict[str, Any]] = []
        for _, row in cleaned.iterrows():
            incident_id = str(row.get("incident_id", "")).strip() or "Unknown"
            description = str(row.get("description", "")).strip()
            priority = normalize_priority(str(row.get("priority", "")).strip())
            created_at = str(row.get("created_at", "")).strip()
            resolution_notes = str(row.get("resolution_notes", "")).strip()
            issue_family = _infer_issue_family(description)
            description_keywords = _extract_keywords(description, max_terms=12)
            resolution_keywords = _extract_keywords(resolution_notes, max_terms=12)
            merged_keywords = list(dict.fromkeys(description_keywords + resolution_keywords))

            docs.append(
                {
                    "doc_id": incident_id,
                    "source_type": "ticket",
                    "incident_id": incident_id,
                    "priority": priority,
                    "created_at": created_at,
                    "description": description,
                    "resolution_notes": resolution_notes,
                    "issue_family": issue_family,
                    "keywords": merged_keywords,
                    "text": (
                        f"Past incident {incident_id}. Priority {priority}. "
                        f"Issue description: {description}. "
                        f"Resolution notes: {resolution_notes}. "
                        f"Category: {issue_family}. "
                        f"Keywords: {' '.join(merged_keywords)}."
                    ),
                }
            )

        return docs

    def _load_itil_documents(self) -> List[Dict[str, Any]]:
        path = Path(self.itil_kb_path)
        if path.exists():
            raw_text = path.read_text(encoding="utf-8")
            chunks = [chunk.strip() for chunk in raw_text.split("\n\n") if chunk.strip()]
        else:
            chunks = DEFAULT_ITIL_SNIPPETS

        docs: List[Dict[str, Any]] = []
        for idx, chunk in enumerate(chunks, start=1):
            docs.append(
                {
                    "doc_id": f"ITIL-{idx:03d}",
                    "source_type": "itil",
                    "incident_id": "ITIL",
                    "priority": "General",
                    "created_at": "N/A",
                    "description": "ITIL incident management guidance",
                    "resolution_notes": chunk,
                    "text": f"ITIL guidance: {chunk}",
                }
            )
        return docs

    @staticmethod
    def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return matrix / norms

    def retrieve(
        self,
        priority: str,
        issue_description: str,
        top_k: int = 8,
    ) -> List[Dict[str, Any]]:
        if self.embeddings is None or not issue_description.strip():
            return []

        normalized_priority = normalize_priority(priority)
        issue_family = _infer_issue_family(issue_description)
        query_keywords = set(_extract_keywords(issue_description, max_terms=15))
        expanded_issue = _expand_query_text(issue_description.strip(), issue_family)
        query = (
            f"Priority: {normalized_priority}. "
            f"Issue family: {issue_family}. "
            f"New issue: {expanded_issue}"
        )
        qvec = self.vectorizer.transform([query]).toarray().astype(np.float32)
        qvec = self._l2_normalize(qvec)

        search_k = min(max(top_k * 4, top_k), len(self.documents))

        if HAS_FAISS and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(qvec, search_k)
            candidates = [
                (int(indices[0][i]), float(scores[0][i]))
                for i in range(search_k)
                if int(indices[0][i]) >= 0
            ]
        else:
            scores = self.embeddings @ qvec[0]
            top_indices = np.argsort(-scores)[:search_k]
            candidates = [(int(i), float(scores[i])) for i in top_indices]

        reranked = []
        for idx, base_score in candidates:
            doc = self.documents[idx]
            score = base_score
            if doc["source_type"] == "ticket":
                if doc["priority"] == normalized_priority:
                    score += 0.22
                elif (
                    normalized_priority in {"Critical", "High"}
                    and doc["priority"] in {"Critical", "High"}
                ):
                    score += 0.1

                doc_family = doc.get("issue_family", "general")
                if doc_family == issue_family and issue_family != "general":
                    score += 0.12

                doc_keywords = set(doc.get("keywords", []))
                if query_keywords and doc_keywords:
                    overlap = len(query_keywords.intersection(doc_keywords))
                    overlap_ratio = overlap / max(len(query_keywords), 1)
                    score += min(0.18, overlap_ratio * 0.25)

            elif doc["source_type"] == "itil":
                score -= 0.03
            reranked.append((score, base_score, doc))

        reranked.sort(key=lambda x: x[0], reverse=True)

        top_items = reranked[:top_k]
        has_itil = any(item[2].get("source_type") == "itil" for item in top_items)
        if not has_itil:
            best_itil = next(
                (item for item in reranked if item[2].get("source_type") == "itil"),
                None,
            )
            if best_itil is not None:
                if len(top_items) < top_k:
                    top_items.append(best_itil)
                else:
                    top_items[-1] = best_itil

        output = []
        for score, base_score, doc in top_items:
            item = dict(doc)
            item["rank_score"] = round(float(score), 4)
            item["similarity"] = round(float(base_score), 4)
            output.append(item)
        return output

    @staticmethod
    def _format_context(retrieved_docs: List[Dict[str, Any]]) -> str:
        lines = []
        for idx, doc in enumerate(retrieved_docs, start=1):
            if doc["source_type"] == "ticket":
                lines.append(
                    f"{idx}. [Past Ticket {doc['incident_id']}] Priority: {doc['priority']} | "
                    f"Issue: {doc['description']} | Resolution: {doc['resolution_notes']}"
                )
            else:
                lines.append(f"{idx}. [ITIL Guidance] {doc['resolution_notes']}")
        return "\n".join(lines)

    @staticmethod
    def _clean_resolution_text(text: str) -> str:
        cleaned = re.sub(r"\s+", " ", str(text).strip())
        cleaned = cleaned.rstrip(".")
        return cleaned

    @staticmethod
    def _historical_action_lines(
        ticket_docs: List[Dict[str, Any]],
        max_actions: int = 3,
    ) -> List[Tuple[str, str]]:
        actions: List[Tuple[str, str]] = []
        seen = set()

        for doc in ticket_docs:
            resolution = IncidentRAGEngine._clean_resolution_text(
                doc.get("resolution_notes", "")
            )
            if not resolution:
                continue
            key = resolution.lower()
            if key in seen:
                continue
            seen.add(key)
            actions.append((str(doc.get("incident_id", "Unknown")), resolution))
            if len(actions) >= max_actions:
                break

        return actions

    @staticmethod
    def _estimate_confidence_text(
        ticket_docs: List[Dict[str, Any]],
        requested_priority: str,
    ) -> str:
        if not ticket_docs:
            return "Low - no close historical ticket matches were retrieved."

        similarities = [float(doc.get("similarity", 0.0)) for doc in ticket_docs]
        avg_similarity = sum(similarities) / max(len(similarities), 1)
        same_priority_count = sum(
            1 for doc in ticket_docs if doc.get("priority") == requested_priority
        )
        same_priority_ratio = same_priority_count / max(len(ticket_docs), 1)

        if avg_similarity >= 0.22 and same_priority_ratio >= 0.5:
            return (
                "High - strong similarity with multiple same-priority historical "
                "incidents and consistent resolution patterns."
            )
        if avg_similarity >= 0.09:
            return (
                "Medium - partially similar historical incidents were found; "
                "recommended actions should be validated during execution."
            )
        return (
            "Low - weak similarity to historical incidents; treat this as a guided "
            "starting plan and validate quickly."
        )

    @staticmethod
    def _fallback_resolution(
        priority: str,
        issue_description: str,
        retrieved_docs: List[Dict[str, Any]],
    ) -> str:
        ticket_docs = [doc for doc in retrieved_docs if doc["source_type"] == "ticket"]
        itil_docs = [doc for doc in retrieved_docs if doc["source_type"] == "itil"]
        same_priority_docs = [doc for doc in ticket_docs if doc.get("priority") == priority]
        prioritized_docs = same_priority_docs if same_priority_docs else ticket_docs
        action_lines = IncidentRAGEngine._historical_action_lines(prioritized_docs, max_actions=3)

        if not action_lines:
            action_lines = [
                (
                    "N/A",
                    "Isolate the affected service path, apply a controlled fix, and confirm user-facing recovery",
                )
            ]

        itil_seed = (
            itil_docs[0]["resolution_notes"]
            if itil_docs
            else "Document root cause and preventive actions after restoring service stability."
        )

        top_case_ids = ", ".join([incident_id for incident_id, _ in action_lines])
        issue_short = IncidentRAGEngine._clean_resolution_text(issue_description)
        first_action = action_lines[0][1]
        second_action = (
            action_lines[1][1]
            if len(action_lines) > 1
            else "Validate end-to-end transactions and confirm service behavior is back to normal"
        )

        immediate_actions = [
            f"- From incident {incident_id}: {action}."
            for incident_id, action in action_lines
        ]
        while len(immediate_actions) < 3:
            immediate_actions.append(
                "- Verify recovery with production health checks and user-level validation."
            )

        preventive_actions = [
            f"- Convert the successful fix pattern into a runbook step: {first_action}.",
            f"- Add monitoring checks around the observed failure theme: {issue_short}.",
            f"- {itil_seed}",
        ]

        confidence_text = IncidentRAGEngine._estimate_confidence_text(
            ticket_docs=prioritized_docs,
            requested_priority=priority,
        )

        return f"""Predicted Resolution:
Based on similar {priority} incidents ({top_case_ids}), the likely resolution path is to apply the same successful remediation pattern.
Primary fix pattern: {first_action}.
Secondary validation pattern: {second_action}.

Recommended Immediate Actions:
{immediate_actions[0]}
{immediate_actions[1]}
{immediate_actions[2]}

Preventive Actions:
{preventive_actions[0]}
{preventive_actions[1]}
{preventive_actions[2]}

Confidence:
{confidence_text}"""

    def predict_resolution(
        self,
        priority: str,
        issue_description: str,
        top_k: int = 8,
    ) -> Dict[str, Any]:
        normalized_priority = normalize_priority(priority)
        description = issue_description.strip()
        if not description:
            raise ValueError("Issue description is required.")

        retrieved_docs = self.retrieve(
            priority=normalized_priority,
            issue_description=description,
            top_k=top_k,
        )
        context = self._format_context(retrieved_docs)

        prompt = f"""
You are an IT incident resolution advisor using RAG context.
Predict a practical resolution plan for a NEW incident.

Rules:
- Ground the answer in retrieved similar tickets and ITIL guidance.
- Keep language clear and execution-focused.
- Mention concrete steps, not vague statements.
- Use at least 2 retrieved ticket incident IDs in the response when available.
- Recommended Immediate Actions must be derived from retrieved resolution notes, not generic placeholders.
- Make actions priority-aware and specific to the new issue description.
- Keep each bullet under 18 words and start with an action verb.
- Avoid repeating the same action in multiple sections.
- If uncertainty exists, say so in Confidence.

New Incident:
Priority: {normalized_priority}
Issue: {description}

Retrieved Context:
{context}

Return exactly this format:
Predicted Resolution:
<2-3 short lines mentioning likely root cause and fix path>

Recommended Immediate Actions:
- <action 1>
- <action 2>
- <action 3>

Preventive Actions:
- <action 1>
- <action 2>
- <action 3>

Confidence:
<High/Medium/Low - one-line reason based on similarity and priority match>
"""

        if API_KEY:
            try:
                prediction = _call_chat_model(prompt, temperature=0.2)
                source = "RAG + LLM API"
            except (requests.RequestException, KeyError, ValueError, TypeError):
                prediction = self._fallback_resolution(
                    priority=normalized_priority,
                    issue_description=description,
                    retrieved_docs=retrieved_docs,
                )
                source = "RAG Fallback"
        else:
            prediction = self._fallback_resolution(
                priority=normalized_priority,
                issue_description=description,
                retrieved_docs=retrieved_docs,
            )
            source = "RAG Fallback"

        similar_cases = []
        for doc in retrieved_docs:
            if doc["source_type"] != "ticket":
                continue
            similar_cases.append(
                {
                    "incident_id": doc["incident_id"],
                    "priority": doc["priority"],
                    "description": doc["description"],
                    "resolution_notes": doc["resolution_notes"],
                    "similarity": doc["similarity"],
                }
            )

        return {
            "priority": normalized_priority,
            "issue_description": description,
            "prediction": prediction,
            "source": source,
            "similar_cases": similar_cases,
            "retrieved_count": len(retrieved_docs),
        }


_RAG_ENGINE: Optional[IncidentRAGEngine] = None


def _get_rag_engine() -> IncidentRAGEngine:
    global _RAG_ENGINE
    if _RAG_ENGINE is None:
        _RAG_ENGINE = IncidentRAGEngine()
    return _RAG_ENGINE


def predict_incident_resolution(
    priority: str,
    issue_description: str,
    tickets_df: Optional[pd.DataFrame] = None,
    top_k: int = 8,
) -> Dict[str, Any]:
    if tickets_df is None:
        engine = _get_rag_engine()
    else:
        engine = IncidentRAGEngine(ticket_df=tickets_df)
    return engine.predict_resolution(
        priority=priority,
        issue_description=issue_description,
        top_k=top_k,
    )
