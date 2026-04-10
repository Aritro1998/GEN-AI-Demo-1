"""Generate personalised policy recommendations for a user."""

import logging
from datetime import date

from config import (
    LOAN_ELIGIBLE_MIN_MONTHS_REMAINING,
    LOAN_ELIGIBLE_TIERS,
    RECOMMENDATION_MODEL,
    RECOMMENDATION_SYSTEM_PROMPT,
    TIER_UPGRADE_ORDER,
)
from api.models import PolicyChunk, PolicyTier, UserPolicy
from modules.llm import call_llm

logger = logging.getLogger(__name__)

# Maximum characters of document content to include per tier in the prompt
_MAX_EXCERPT_CHARS = 2000

# Words that may trigger content-safety filters on some LLM endpoints.
# We redact them in excerpts sent to the recommendation prompt.
_FILTER_WORDS = [
    "illness", "disease", "death", "suicide", "murder", "cancer",
    "tumor", "tumour", "HIV", "AIDS", "drug", "narcotic",
]


def _sanitize_excerpt(text):
    """Replace known content-filter trigger words with neutral alternatives."""
    if not text:
        return text
    import re
    for word in _FILTER_WORDS:
        text = re.sub(
            rf'\b{re.escape(word)}\b',
            '[medical-condition]',
            text,
            flags=re.IGNORECASE,
        )
    return text


def _get_tier_excerpt(tier):
    """Return a text excerpt from the policy document for a given tier.

    Concatenates stored chunks up to _MAX_EXCERPT_CHARS so the LLM can
    reference actual policy content when generating recommendations.
    """
    chunks = (
        PolicyChunk.objects
        .filter(document__tier=tier)
        .order_by("chunk_index")
        .values_list("text", flat=True)
    )
    excerpt = ""
    for text in chunks:
        if len(excerpt) + len(text) > _MAX_EXCERPT_CHARS:
            remaining = _MAX_EXCERPT_CHARS - len(excerpt)
            if remaining > 100:
                excerpt += text[:remaining] + "..."
            break
        excerpt += text + "\n"
    return excerpt.strip() or None


def _months_remaining(end_date):
    """Return approximate months between today and the policy end date."""
    today = date.today()
    delta = end_date - today
    return max(delta.days // 30, 0)


def _next_tier(current_tier_name):
    """Return the next tier name in the upgrade ladder, or None if at top."""
    try:
        idx = TIER_UPGRADE_ORDER.index(current_tier_name)
    except ValueError:
        return None
    if idx + 1 < len(TIER_UPGRADE_ORDER):
        return TIER_UPGRADE_ORDER[idx + 1]
    return None


def get_upgrade_recommendations(user_policies):
    """Identify tier upgrade opportunities for each user policy.

    Returns a list of dicts with upgrade details (no LLM call yet).
    """
    recommendations = []

    for up in user_policies:
        next_tier_name = _next_tier(up.tier.name)
        if not next_tier_name:
            continue

        next_tier = PolicyTier.objects.filter(
            category=up.tier.category, name=next_tier_name,
        ).first()
        if not next_tier:
            continue

        price_diff = None
        if up.tier.price_monthly and next_tier.price_monthly:
            price_diff = float(next_tier.price_monthly) - float(up.tier.price_monthly)

        current_excerpt = _get_tier_excerpt(up.tier)
        upgrade_excerpt = _get_tier_excerpt(next_tier)

        recommendations.append({
            "type": "upgrade",
            "policy_number": up.policy_number,
            "category": up.tier.category.name,
            "current_tier": up.tier.name,
            "current_display": up.tier.display_name,
            "current_price": float(up.tier.price_monthly) if up.tier.price_monthly else None,
            "recommended_tier": next_tier.name,
            "recommended_display": next_tier.display_name,
            "recommended_price": float(next_tier.price_monthly) if next_tier.price_monthly else None,
            "price_difference": price_diff,
            "highlights": next_tier.highlights,
            "current_excerpt": current_excerpt,
            "upgrade_excerpt": upgrade_excerpt,
        })

    return recommendations


def get_loan_recommendations(user_policies):
    """Identify loan-against-policy opportunities.

    Only gold/platinum tiers with sufficient remaining duration qualify.
    """
    recommendations = []

    for up in user_policies:
        if up.tier.name not in LOAN_ELIGIBLE_TIERS:
            continue

        months_left = _months_remaining(up.end_date)
        if months_left < LOAN_ELIGIBLE_MIN_MONTHS_REMAINING:
            continue

        tier_excerpt = _get_tier_excerpt(up.tier)

        recommendations.append({
            "type": "loan",
            "policy_number": up.policy_number,
            "category": up.tier.category.name,
            "tier": up.tier.name,
            "tier_display": up.tier.display_name,
            "months_remaining": months_left,
            "policy_excerpt": tier_excerpt,
        })

    return recommendations


def generate_recommendation_descriptions(raw_recommendations):
    """Use the LLM to generate friendly descriptions for each recommendation."""
    if not raw_recommendations:
        return []

    # Build a single prompt with all recommendations for efficiency
    parts = []
    for i, rec in enumerate(raw_recommendations, 1):
        if rec["type"] == "upgrade":
            block = (
                f"{i}. UPGRADE: {rec['category']} policy ({rec['current_display']}) "
                f"→ {rec['recommended_display']}.\n"
                f"   Current price: ₹{rec['current_price']}/month. "
                f"Upgrade price: ₹{rec['recommended_price']}/month "
                f"(+₹{rec['price_difference']:.2f}/month).\n"
                f"   Upgrade tier highlights: {rec['highlights']}"
            )
            if rec.get("current_excerpt"):
                block += f"\n   --- Current plan document excerpt ---\n{_sanitize_excerpt(rec['current_excerpt'])}"
            if rec.get("upgrade_excerpt"):
                block += f"\n   --- Upgrade plan document excerpt ---\n{_sanitize_excerpt(rec['upgrade_excerpt'])}"
            parts.append(block)

        elif rec["type"] == "loan":
            block = (
                f"{i}. LOAN: {rec['category']} policy ({rec['tier_display']}), "
                f"policy number {rec['policy_number']}, "
                f"{rec['months_remaining']} months remaining.\n"
                f"   Eligible for loan against policy."
            )
            if rec.get("policy_excerpt"):
                block += f"\n   --- Policy document excerpt ---\n{_sanitize_excerpt(rec['policy_excerpt'])}"
            parts.append(block)

    user_prompt = (
        "Generate a short, friendly recommendation message for each of the "
        "following opportunities. Number each recommendation to match.\n\n"
        + "\n".join(parts)
    )

    try:
        response = call_llm(
            model=RECOMMENDATION_MODEL,
            system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.5,
        )
    except Exception as exc:
        logger.warning("LLM call failed for recommendations, using fallback: %s", exc)
        return _fallback_descriptions(raw_recommendations)

    # Parse numbered responses back into individual descriptions
    descriptions = response.strip().split("\n")
    desc_map = {}
    current_num = None
    current_text = []

    for line in descriptions:
        line = line.strip()
        if not line:
            continue
        # Check if line starts with a number
        for j in range(1, len(raw_recommendations) + 1):
            if line.startswith(f"{j}.") or line.startswith(f"{j})"):
                if current_num is not None:
                    desc_map[current_num] = " ".join(current_text)
                current_num = j
                current_text = [line[len(f"{j}."):].strip().lstrip(")").strip()]
                break
        else:
            if current_num is not None:
                current_text.append(line)

    if current_num is not None:
        desc_map[current_num] = " ".join(current_text)

    # Attach descriptions and strip raw excerpts (only needed for the prompt)
    excerpt_keys = ("current_excerpt", "upgrade_excerpt", "policy_excerpt")
    for i, rec in enumerate(raw_recommendations, 1):
        rec["description"] = desc_map.get(i, "")
        for key in excerpt_keys:
            rec.pop(key, None)

    return raw_recommendations


def _fallback_descriptions(raw_recommendations):
    """Generate simple rule-based descriptions when LLM is unavailable."""
    excerpt_keys = ("current_excerpt", "upgrade_excerpt", "policy_excerpt")
    for rec in raw_recommendations:
        if rec["type"] == "upgrade":
            diff = rec.get("price_difference")
            diff_str = f" for just \u20b9{diff:.0f} more per month" if diff else ""
            rec["description"] = (
                f"Consider upgrading from {rec['current_display']} to "
                f"{rec['recommended_display']}{diff_str}. "
                f"{rec.get('highlights', 'Enhanced coverage and benefits await you.')}"
            )
        elif rec["type"] == "loan":
            rec["description"] = (
                f"Your {rec['tier_display']} policy (#{rec['policy_number']}) with "
                f"{rec['months_remaining']} months remaining qualifies for a loan "
                f"against policy. Use your policy as collateral for quick financing."
            )
        for key in excerpt_keys:
            rec.pop(key, None)
    return raw_recommendations


def get_recommendations_for_user(user):
    """Return all recommendations for a user with LLM-generated descriptions."""
    policies = UserPolicy.objects.filter(
        user=user, is_active=True,
    ).select_related("tier", "tier__category")

    if not policies.exists():
        return []

    upgrades = get_upgrade_recommendations(policies)
    loans = get_loan_recommendations(policies)

    all_recs = upgrades + loans
    if not all_recs:
        return []

    return generate_recommendation_descriptions(all_recs)
