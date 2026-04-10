"""Central configuration for models, paths, and policy Q&A behavior."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

API_CONFIG = {
    "api_key_env": "OPENAI_API_KEY",
    "base_url_env": "BASE_URL",
}


def resolve_backend_path(path_value):
    """Resolve relative backend paths while still allowing absolute overrides."""
    candidate = Path(path_value)
    return candidate if candidate.is_absolute() else BASE_DIR / candidate


DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "genailab-maas-gpt-4o")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", DEFAULT_MODEL)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "azure/genailab-maas-text-embedding-3-large",
)

POLICY_RAG_CONFIG = {
    "embedding_model": EMBEDDING_MODEL,
    "top_k": 5,
    "chunk_size": 500,
    "chunk_overlap": 100,
}

POLICY_QA_MODEL = GENERATOR_MODEL

POLICY_QA_SYSTEM_PROMPT = (
    "You are an expert insurance policy analyst. Your role is to answer "
    "customer questions about their insurance policy coverage accurately and "
    "clearly.\n\n"
    "Rules:\n"
    "- Answer ONLY based on the provided policy excerpts.\n"
    "- If the answer is not found in the excerpts, say so clearly.\n"
    "- Cite the page number when referencing specific policy details.\n"
    "- Use simple, customer-friendly language.\n"
    "- Be concise but thorough.\n"
    "- Do not make up or assume any coverage details."
)

# ── Recommendation engine ─────────────────────────────────────────────

RECOMMENDATION_MODEL = GENERATOR_MODEL

TIER_UPGRADE_ORDER = ["silver", "gold", "platinum"]

LOAN_ELIGIBLE_TIERS = ["gold", "platinum"]
LOAN_ELIGIBLE_MIN_MONTHS_REMAINING = 6

RECOMMENDATION_SYSTEM_PROMPT = (
    "You are a friendly insurance advisor. Your job is to write short, "
    "personalised recommendations for customers about their insurance policies.\n\n"
    "You will be given actual excerpts from the policy documents. Use these "
    "excerpts to provide specific, grounded reasoning.\n\n"
    "Rules:\n"
    "- Keep each recommendation to 3-5 sentences.\n"
    "- For UPGRADE recommendations: compare the current plan excerpt with the "
    "upgrade plan excerpt. Highlight specific coverages, limits, or benefits "
    "the customer would gain by upgrading. Mention the price difference.\n"
    "- For LOAN recommendations: reference specific details from the policy "
    "document (e.g. sum assured, coverage value, policy type) to explain why "
    "the customer is eligible and how much they could potentially borrow.\n"
    "- Be encouraging but not pushy.\n"
    "- Do not invent policy details — use ONLY the information from the "
    "provided document excerpts and metadata."
)
