"""Service layer for the insurance policy provider platform."""

import logging
import re
import tempfile
from pathlib import Path

from django.db import transaction

from config import (
    POLICY_QA_MODEL,
    POLICY_QA_SYSTEM_PROMPT,
    POLICY_RAG_CONFIG,
)
from api.models import PolicyChunk, PolicyDocument, PolicyTier, UserPolicy
from modules.chunker import chunk_pages
from modules.llm import call_llm
from modules.pdf_ingestion import extract_text_from_pdf
from modules.policy_rag import PolicyRAG

logger = logging.getLogger(__name__)

# ── Cache for per-tier RAG instances ──────────────────────────────────
_tier_rag_cache = {}


def get_rag_for_tier(tier_id):
    """Return a PolicyRAG instance for a specific tier, cached."""
    if tier_id not in _tier_rag_cache:
        chunks = list(
            PolicyChunk.objects.filter(document__tier_id=tier_id)
            .values("id", "page", "text", "document__file_name")
        )
        chunk_dicts = [
            {
                "chunk_id": c["id"],
                "doc_name": c["document__file_name"],
                "page": c["page"],
                "text": c["text"],
            }
            for c in chunks
        ]
        rag = PolicyRAG(
            embedding_model=POLICY_RAG_CONFIG["embedding_model"],
            top_k=POLICY_RAG_CONFIG["top_k"],
            chunks=chunk_dicts,
        )
        _tier_rag_cache[tier_id] = rag
    return _tier_rag_cache[tier_id]


def invalidate_rag_cache(tier_id=None):
    """Clear cached RAG index after a new upload."""
    if tier_id:
        _tier_rag_cache.pop(tier_id, None)
    else:
        _tier_rag_cache.clear()


# ── Admin: ingest a policy PDF into the DB ────────────────────────────

def ingest_policy_pdf(uploaded_file, tier_id):
    """Extract text from PDF, chunk it, and store in the database.

    Replaces any existing documents for this tier.
    """
    tier = PolicyTier.objects.get(pk=tier_id)
    doc_name = uploaded_file.name
    suffix = Path(doc_name).suffix or ".pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for file_chunk in uploaded_file.chunks():
            tmp.write(file_chunk)
        tmp_path = tmp.name

    try:
        pages = extract_text_from_pdf(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not pages:
        raise ValueError(f"No readable text found in {doc_name}")

    text_chunks = chunk_pages(
        pages,
        doc_name=doc_name,
        chunk_size=POLICY_RAG_CONFIG["chunk_size"],
        chunk_overlap=POLICY_RAG_CONFIG["chunk_overlap"],
    )

    with transaction.atomic():
        # Remove old documents for this tier
        PolicyDocument.objects.filter(tier=tier).delete()

        doc = PolicyDocument.objects.create(
            tier=tier,
            file_name=doc_name,
            page_count=len(pages),
            chunk_count=len(text_chunks),
        )

        # Save a copy of the PDF for user download
        uploaded_file.seek(0)
        doc.pdf_file.save(doc_name, uploaded_file, save=True)

        db_chunks = [
            PolicyChunk(
                document=doc,
                chunk_index=i,
                page=c["page"],
                text=c["text"],
            )
            for i, c in enumerate(text_chunks)
        ]
        PolicyChunk.objects.bulk_create(db_chunks)

    invalidate_rag_cache(tier_id)

    logger.info(
        "Ingested %s for tier %s: %d pages → %d chunks",
        doc_name, tier, len(pages), len(text_chunks),
    )

    return {
        "doc_name": doc_name,
        "tier": str(tier),
        "pages_extracted": len(pages),
        "chunks_created": len(text_chunks),
    }


def ingest_policy_pdf_from_path(pdf_path, tier_id):
    """Ingest a PDF from a filesystem path (used by management commands).

    Works like ingest_policy_pdf but reads from disk instead of an upload.
    """
    from django.core.files.base import ContentFile

    pdf_path = Path(pdf_path)
    tier = PolicyTier.objects.get(pk=tier_id)
    doc_name = pdf_path.name

    pages = extract_text_from_pdf(str(pdf_path))
    if not pages:
        raise ValueError(f"No readable text found in {doc_name}")

    text_chunks = chunk_pages(
        pages,
        doc_name=doc_name,
        chunk_size=POLICY_RAG_CONFIG["chunk_size"],
        chunk_overlap=POLICY_RAG_CONFIG["chunk_overlap"],
    )

    with transaction.atomic():
        PolicyDocument.objects.filter(tier=tier).delete()

        doc = PolicyDocument.objects.create(
            tier=tier,
            file_name=doc_name,
            page_count=len(pages),
            chunk_count=len(text_chunks),
        )

        # Save a copy of the PDF for user download
        pdf_bytes = pdf_path.read_bytes()
        doc.pdf_file.save(doc_name, ContentFile(pdf_bytes), save=True)

        db_chunks = [
            PolicyChunk(
                document=doc,
                chunk_index=i,
                page=c["page"],
                text=c["text"],
            )
            for i, c in enumerate(text_chunks)
        ]
        PolicyChunk.objects.bulk_create(db_chunks)

    invalidate_rag_cache(tier_id)

    logger.info(
        "Ingested %s for tier %s: %d pages → %d chunks",
        doc_name, tier, len(pages), len(text_chunks),
    )

    return {
        "doc_name": doc_name,
        "tier": str(tier),
        "pages_extracted": len(pages),
        "chunks_created": len(text_chunks),
    }


# ── User: query their assigned policy ────────────────────────────────

def get_user_policies(user):
    """Return all active policies for a user."""
    return UserPolicy.objects.filter(user=user, is_active=True).select_related(
        "tier", "tier__category",
    )


def _detect_category(question, available_categories):
    """Match the question to a policy category using keyword detection.

    Returns the matched category name or None if ambiguous / no match.
    """
    question_lower = question.lower()

    # Map common keywords to category names
    keyword_map = {
        "car": ["car", "motor", "vehicle", "driving", "accident", "collision",
                "windscreen", "breakdown", "tow", "road"],
        "health": ["health", "medical", "hospital", "doctor", "surgery",
                   "prescription", "dental", "vision", "illness", "treatment"],
        "home": ["home", "house", "property", "flood", "fire", "theft",
                 "burglary", "building", "contents"],
        "life": ["life", "death", "beneficiary", "term", "whole life",
                 "endowment", "annuity"],
        "travel": ["travel", "trip", "flight", "luggage", "cancellation",
                   "overseas", "abroad"],
    }

    available_lower = {c.lower(): c for c in available_categories}
    matched = set()

    for category_key, keywords in keyword_map.items():
        if category_key in available_lower:
            for kw in keywords:
                if kw in question_lower:
                    matched.add(available_lower[category_key])
                    break

    # Also check if the category name itself appears in the question
    for cat_lower, cat_original in available_lower.items():
        if cat_lower in question_lower and cat_original not in matched:
            matched.add(cat_original)

    if len(matched) == 1:
        return matched.pop()
    return None


_FILTER_WORDS = [
    "illness", "disease", "death", "suicide", "murder", "cancer",
    "tumor", "tumour", "HIV", "AIDS", "drug", "narcotic",
]


def _sanitize_for_llm(text):
    """Replace words that may trigger LLM content-safety filters."""
    if not text:
        return text
    for word in _FILTER_WORDS:
        text = re.sub(
            rf'\b{re.escape(word)}\b',
            '[medical-condition]',
            text,
            flags=re.IGNORECASE,
        )
    return text


# Keywords that signal the user wants the full policy content, not a specific Q&A
_FULL_DOC_KEYWORDS = [
    "show my policy", "show my entire", "full policy", "entire policy",
    "complete policy", "all details", "all the details", "whole policy",
    "policy document", "policy details", "show everything", "full details",
    "summarize my policy", "summarise my policy", "summary of my policy",
    "what does my policy cover", "what is covered", "what all is covered",
    "overview of my policy", "tell me about my policy",
]


def _is_full_document_request(question):
    """Return True if the user wants to see their full policy, not a narrow Q&A."""
    q = question.lower().strip()
    return any(kw in q for kw in _FULL_DOC_KEYWORDS)


def _get_all_chunks_as_context(tier_id):
    """Return ALL chunks for a tier as a formatted context string + source refs."""
    chunks = list(
        PolicyChunk.objects.filter(document__tier_id=tier_id)
        .order_by("chunk_index")
        .values("document__file_name", "page", "chunk_index", "text")
    )
    if not chunks:
        return "", []

    parts = []
    sources = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Section {i} | {c['document__file_name']} p.{c['page']}]\n"
            f"{c['text']}"
        )
        sources.append({
            "doc_name": c["document__file_name"],
            "page": c["page"],
            "chunk_id": c["chunk_index"],
        })
    return "\n\n".join(parts), sources


def query_policy(user, question, user_policy_id=None, chat_history=None):
    """Retrieve relevant chunks from the user's policy and generate an answer.

    Routing priority:
    1. user_policy_id — scope to that exact policy
    2. Category detection — detect from question keywords
    3. Fallback — search all user policies
    """
    policies = get_user_policies(user)
    if not policies.exists():
        return {
            "answer": "You don't have any active policies. Please contact support.",
            "sources": [],
        }

    if user_policy_id:
        policies = policies.filter(pk=user_policy_id)
        if not policies.exists():
            return {
                "answer": "Policy not found or not assigned to your account.",
                "sources": [],
            }
    elif policies.count() > 1:
        # Try to auto-detect the relevant category
        available_categories = list(
            policies.values_list("tier__category__name", flat=True).distinct()
        )
        detected = _detect_category(question, available_categories)
        if detected:
            policies = policies.filter(tier__category__name=detected)
            logger.info("Routed question to category: %s", detected)

    full_doc = _is_full_document_request(question)

    # Gather context from matched policies
    all_context_parts = []
    all_sources = []
    for policy in policies:
        if full_doc:
            context, src_refs = _get_all_chunks_as_context(policy.tier_id)
            if context:
                all_context_parts.append(context)
                for s in src_refs:
                    s["policy_number"] = policy.policy_number
                    s["category"] = policy.tier.category.name
                    s["tier"] = str(policy.tier)
                all_sources.extend(src_refs)
        else:
            rag = get_rag_for_tier(policy.tier_id)
            context = rag.retrieve_as_context(question)
            if context:
                all_context_parts.append(context)
                chunks = rag.retrieve(question)
                for c in chunks:
                    all_sources.append({
                        "doc_name": c["doc_name"],
                        "page": c["page"],
                        "chunk_id": c["chunk_id"],
                        "policy_number": policy.policy_number,
                        "category": policy.tier.category.name,
                        "tier": str(policy.tier),
                    })

    if not all_context_parts:
        return {
            "answer": "No relevant information was found in your policy documents "
                      "for this question.",
            "sources": [],
        }

    combined_context = "\n\n".join(all_context_parts)

    # Sanitize content that may trigger LLM content filters
    combined_context = _sanitize_for_llm(combined_context)

    # Build history block
    history_block = ""
    if chat_history:
        parts = []
        for msg in chat_history:
            role_label = "Customer" if msg["role"] == "user" else "Agent"
            parts.append(f"{role_label}: {msg['content']}")
        history_block = "Previous conversation:\n" + "\n".join(parts) + "\n\n"

    if full_doc:
        user_prompt = (
            f"{history_block}"
            f"Complete policy document content:\n{combined_context}\n\n"
            f"Customer question: {question}\n\n"
            f"The above is the COMPLETE policy document, not just excerpts. "
            f"Provide a comprehensive, well-structured summary covering all "
            f"key details: coverage, limits, premiums, exclusions, benefits, "
            f"and any other important terms."
        )
    else:
        user_prompt = (
            f"{history_block}"
            f"Policy excerpts:\n{combined_context}\n\n"
            f"Customer question: {question}\n\n"
            f"Provide a clear, accurate answer based on the policy excerpts above."
        )

    try:
        answer = call_llm(
            model=POLICY_QA_MODEL,
            system_prompt=POLICY_QA_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
        )
    except Exception as exc:
        logger.warning("LLM call failed for policy query: %s", exc)
        answer = (
            "I'm sorry, I wasn't able to process your question at this time. "
            "Please try rephrasing your question or try again later."
        )

    return {
        "answer": answer,
        "sources": all_sources,
    }
