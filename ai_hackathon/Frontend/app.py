"""Streamlit frontend for the Insurance Policy Provider platform."""

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://127.0.0.1:8000/api"

CATEGORY_ICONS = {
    "Car": "\U0001f697",
    "Health": "\U0001fa7a",
    "Life": "\U0001f6e1\ufe0f",
}

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Policy Lens",
    page_icon="\U0001f50d",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Global dark theme ─────────────────────────────────── */
    .stApp {
        background: linear-gradient(160deg, #0b0f1a 0%, #111827 40%, #0f172a 100%);
    }
    .stApp * { color: #e2e8f0; }

    /* ── Sidebar ───────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #302b63, #24243e) !important;
        border-right: 1px solid rgba(139,92,246,0.15);
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        overflow: hidden !important;
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] * { color: #e0d6ff !important; }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(139,92,246,0.2);
        background: rgba(139,92,246,0.08);
        color: #f0e6ff !important;
        font-size: 0.88rem;
        font-weight: 600;
        text-align: left;
        padding: 0.55rem 0.9rem;
        margin-bottom: 0.15rem;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(139,92,246,0.2);
        border-color: rgba(139,92,246,0.45);
        transform: translateX(3px);
    }
    section[data-testid="stSidebar"] hr {
        margin: 0.4rem 0 !important;
        border-color: rgba(139,92,246,0.15) !important;
    }
    .sidebar-brand {
        font-size: 1.5rem; font-weight: 800;
        background: linear-gradient(135deg, #a78bfa, #6ee7b7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sidebar-tagline {
        font-size: 0.8rem; color: rgba(200,190,240,0.6) !important;
        margin-bottom: 0.5rem; line-height: 1.4;
    }
    .user-badge {
        text-align: center; margin-bottom: 4px;
    }
    .user-badge .avatar {
        width: 48px; height: 48px; border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; font-weight: 700; color: #fff;
        margin: 0 auto 6px;
        box-shadow: 0 0 20px rgba(139,92,246,0.35);
    }
    .user-badge .uname {
        font-size: 0.85rem; font-weight: 600; opacity: 0.9;
    }

    /* ── Metrics ───────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(6,182,212,0.08));
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 16px; padding: 16px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important; font-weight: 800 !important;
        background: linear-gradient(135deg, #a78bfa, #22d3ee);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* ── Policy Cards ──────────────────────────────────────── */
    .policy-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border-radius: 20px; padding: 26px; color: #fff;
        box-shadow: 0 8px 32px rgba(99,102,241,0.2);
        margin-bottom: 14px; min-height: 170px;
        display: flex; flex-direction: column; justify-content: space-between;
        border: 1px solid rgba(139,92,246,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .policy-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99,102,241,0.35);
    }
    .policy-card .card-cat {
        font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1.5px;
        color: #a5b4fc; margin-bottom: 6px;
    }
    .policy-card .card-tier {
        font-size: 1.4rem; font-weight: 700; margin-bottom: 6px;
    }
    .policy-card .card-num {
        font-size: 0.82rem; opacity: 0.6; font-family: monospace;
    }
    .policy-card .card-price {
        font-size: 1.15rem; font-weight: 700; margin-top: 10px;
        color: #6ee7b7;
    }

    /* ── Recommendation Cards ──────────────────────────────── */
    .rec-card {
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 18px; padding: 22px; margin-bottom: 14px;
        background: linear-gradient(135deg, rgba(30,27,75,0.6), rgba(49,46,129,0.3));
        backdrop-filter: blur(12px);
        transition: border-color 0.2s ease;
    }
    .rec-card:hover {
        border-color: rgba(139,92,246,0.4);
    }
    .rec-badge-upgrade {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px;
        background: linear-gradient(135deg, #059669, #10b981); color: #fff;
        margin-bottom: 10px;
    }
    .rec-badge-loan {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px;
        background: linear-gradient(135deg, #2563eb, #06b6d4); color: #fff;
        margin-bottom: 10px;
    }

    /* ── Offering Cards ────────────────────────────────────── */
    .offering-card {
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 18px; padding: 20px; margin-bottom: 12px;
        background: linear-gradient(145deg, rgba(30,27,75,0.5), rgba(15,23,42,0.8));
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .offering-card:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,0.4);
    }
    .offering-cat {
        font-size: 1.15rem; font-weight: 700; margin-bottom: 10px;
    }
    .tier-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 8px 0; border-bottom: 1px solid rgba(139,92,246,0.08);
    }
    .tier-row:last-child { border-bottom: none; }
    .tier-name { font-weight: 600; }
    .tier-price {
        font-weight: 600; font-size: 0.88rem;
        color: #6ee7b7;
    }
    .tier-badge-silver { color: #94a3b8; }
    .tier-badge-gold { color: #fbbf24; }
    .tier-badge-platinum { color: #c084fc; }

    /* ── Divider ───────────────────────────────────────────── */
    .divider {
        height: 2px; border-radius: 2px; margin: 28px 0;
        background: linear-gradient(90deg, transparent, #8b5cf6, #06b6d4, transparent);
    }

    /* ── Buttons ───────────────────────────────────────────── */
    .stButton > button {
        border-radius: 12px; font-weight: 600; padding: 0.5rem 1.6rem;
        transition: all 0.2s ease;
        border: 1px solid rgba(139,92,246,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139,92,246,0.25);
        border-color: rgba(139,92,246,0.4);
    }

    /* ── Login Hero ────────────────────────────────────────── */
    .login-hero {
        text-align: center; padding: 48px 20px 12px;
    }
    .login-hero h1 {
        font-size: 2.8rem; font-weight: 800; margin-bottom: 6px;
        background: linear-gradient(135deg, #a78bfa, #6ee7b7, #22d3ee);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .login-hero .tagline {
        font-size: 1.05rem; color: #94a3b8; max-width: 540px;
        margin: 0 auto 8px; line-height: 1.6;
    }
    .login-hero .features {
        display: flex; justify-content: center; gap: 28px;
        margin-top: 18px; flex-wrap: wrap;
    }
    .login-hero .feat {
        text-align: center; min-width: 110px;
    }
    .login-hero .feat-icon { font-size: 1.6rem; margin-bottom: 4px; }
    .login-hero .feat-label {
        font-size: 0.82rem; font-weight: 600; color: #a5b4fc;
    }

    /* ── Login Form ────────────────────────────────────────── */
    .login-container {
        max-width: 420px; margin: 20px auto; padding: 36px;
        border-radius: 22px;
        background: linear-gradient(145deg, #1e1b4b, #312e81);
        box-shadow: 0 16px 48px rgba(99,102,241,0.2);
        border: 1px solid rgba(139,92,246,0.2);
        text-align: center; color: #e0e8f5;
    }
    .login-container h2 {
        color: #fff; margin-bottom: 4px; font-size: 1.4rem;
    }
    .login-container p {
        color: rgba(200,200,240,0.6); font-size: 0.88rem; margin-bottom: 16px;
    }

    /* ── Inputs ─────────────────────────────────────────────── */
    .stTextInput input {
        background: rgba(30,27,75,0.5) !important;
        border: 1px solid rgba(139,92,246,0.2) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    .stTextInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139,92,246,0.2) !important;
    }
    .stSelectbox > div > div {
        background: rgba(30,27,75,0.5) !important;
        border: 1px solid rgba(139,92,246,0.2) !important;
        border-radius: 10px !important;
    }

    /* ── Expander ──────────────────────────────────────────── */
    .streamlit-expanderHeader,
    [data-testid="stExpander"] summary,
    details summary,
    [data-testid="stExpander"] [data-testid="stExpanderToggleDetails"],
    .st-expander summary {
        background: #1e1b4b !important;
        border-radius: 12px !important;
        border: 1px solid rgba(139,92,246,0.2) !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stExpander"] summary:hover,
    details summary:hover {
        border-color: rgba(139,92,246,0.4) !important;
    }
    [data-testid="stExpander"] summary *,
    details summary * {
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
        background: none !important;
    }
    [data-testid="stExpander"],
    [data-testid="stExpander"][open],
    details[open] {
        background: rgba(15,12,41,0.6) !important;
        border: 1px solid rgba(139,92,246,0.12) !important;
        border-radius: 14px !important;
    }
    [data-testid="stExpander"] > div,
    details > div {
        background: transparent !important;
    }

    /* ── Code / monospace ──────────────────────────────────── */
    code {
        background: rgba(139,92,246,0.15) !important;
        color: #c4b5fd !important;
        padding: 2px 6px; border-radius: 4px;
    }

    /* ── Section headings ──────────────────────────────────── */
    h1, h2, h3 {
        background: linear-gradient(135deg, #c4b5fd, #6ee7b7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* ── Chat ──────────────────────────────────────────────── */
    .stChatMessage {
        border-radius: 16px !important;
        border: 1px solid rgba(139,92,246,0.1) !important;
        background: rgba(30,27,75,0.3) !important;
    }
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    .stChatInput, .stChatInput > div {
        background: #ffffff !important;
        border-color: rgba(139,92,246,0.35) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea,
    .stChatInput textarea,
    [data-testid="stChatInputTextArea"],
    [data-testid="stChatInput"] [data-testid="stChatInputTextArea"] {
        background: transparent !important;
        color: #111 !important;
        caret-color: #8b5cf6 !important;
        -webkit-text-fill-color: #111 !important;
    }
    [data-testid="stBottom"] {
        background: transparent !important;
    }

    /* ── Text selection highlight ──────────────────────────── */
    ::selection {
        background: rgba(139,92,246,0.45) !important;
        color: #fff !important;
        -webkit-text-fill-color: #fff !important;
    }
    ::-moz-selection {
        background: rgba(139,92,246,0.45) !important;
        color: #fff !important;
    }
    [data-testid="stChatInput"] button,
    .stChatInput button {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4) !important;
        color: #fff !important;
    }

    /* ── Form submit / download buttons ────────────────────── */
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
        color: #fff !important;
        border: none !important;
        font-weight: 600;
    }
    .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #a78bfa, #7c3aed) !important;
        box-shadow: 0 6px 24px rgba(139,92,246,0.35) !important;
    }

    /* ── Captions / labels ─────────────────────────────────── */
    .stCaption, small { color: #94a3b8 !important; }
    label { color: #c4b5fd !important; -webkit-text-fill-color: #c4b5fd !important; }

    /* ── Password eye icon ─────────────────────────────────── */
    .stTextInput button {
        color: #94a3b8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
for key, default in {
    "token": None,
    "user": None,
    "page": "dashboard",
    "chat_history": [],
    "active_policy_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def api_headers():
    h = {}
    if st.session_state.token:
        h["Authorization"] = f"Token {st.session_state.token}"
    return h


def api_get(path, **kwargs):
    return requests.get(f"{API_BASE}{path}", headers=api_headers(), timeout=30, **kwargs)


def api_post(path, **kwargs):
    return requests.post(f"{API_BASE}{path}", headers=api_headers(), timeout=180, **kwargs)


def do_login(username, password):
    r = requests.post(f"{API_BASE}/auth/login/", json={
        "username": username, "password": password,
    }, timeout=10)
    if r.status_code == 200:
        data = r.json()
        st.session_state.token = data["token"]
        st.session_state.user = data
        return True, None
    return False, r.json().get("error", "Login failed")


def do_logout():
    try:
        api_post("/auth/logout/")
    except Exception:
        pass
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.chat_history = []
    st.session_state.active_policy_id = None
    st.session_state.page = "dashboard"


def check_health():
    try:
        return requests.get(f"{API_BASE}/health/", timeout=3).status_code == 200
    except Exception:
        return False


def nav(page_key):
    st.session_state.page = page_key
    if page_key != "chat":
        st.session_state.chat_history = []
        st.session_state.active_policy_id = None


# ---------------------------------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------------------------------
if not st.session_state.token:
    # Hide sidebar and make the page fill the viewport
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none; }
        .block-container { padding-top: 1.5rem !important; padding-bottom: 0 !important; max-width: 100% !important; }
        header[data-testid="stHeader"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left_col, spacer, right_col = st.columns([1.4, 0.1, 0.9])

    # ── LEFT: Hero + Offerings ────────────────────────────────────
    with left_col:
        st.markdown(
            '<div class="login-hero" style="text-align:left;padding:16px 0 0;">'
            '<h1>\U0001f50d Policy Lens</h1>'
            '<p class="tagline" style="margin:0 0 12px;">'
            'AI-powered insurance platform \u2014 manage policies, '
            'get instant answers, and smart recommendations.'
            '</p>'
            '<div class="features" style="justify-content:flex-start;gap:20px;margin-top:12px;">'
            '<div class="feat"><div class="feat-icon">\U0001f6e1\ufe0f</div><div class="feat-label">Multi-tier Coverage</div></div>'
            '<div class="feat"><div class="feat-icon">\U0001f4b0</div><div class="feat-label">Affordable Plans</div></div>'
            '<div class="feat"><div class="feat-icon">\U0001f916</div><div class="feat-label">AI-Powered</div></div>'
            '<div class="feat"><div class="feat-icon">\u26a1</div><div class="feat-label">Instant Answers</div></div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        st.markdown("##### Our Offerings")

        try:
            off_r = requests.get(f"{API_BASE}/offerings/", timeout=5)
            if off_r.status_code == 200:
                categories = off_r.json().get("categories", [])
                if categories:
                    off_cols = st.columns(min(len(categories), 3))
                    for idx, cat in enumerate(categories):
                        icon = CATEGORY_ICONS.get(cat["name"], "\U0001f4c4")
                        with off_cols[idx % len(off_cols)]:
                            tier_rows = ""
                            for t in cat["tiers"]:
                                badge_cls = f"tier-badge-{t['name']}"
                                price = f"\u20b9{t['price_monthly']:.0f}/mo" if t["price_monthly"] else ""
                                tier_rows += (
                                    f'<div class="tier-row">'
                                    f'<span class="tier-name {badge_cls}">{t["display_name"]}</span>'
                                    f'<span class="tier-price">{price}</span>'
                                    f'</div>'
                                )
                            st.markdown(
                                f'<div class="offering-card">'
                                f'<div class="offering-cat">{icon} {cat["name"]}</div>'
                                f'<div style="font-size:0.78rem;opacity:0.65;margin-bottom:6px;">{cat["description"]}</div>'
                                f'{tier_rows}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
        except Exception:
            pass

    # ── RIGHT: Sign-in form ───────────────────────────────────────
    with right_col:
        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="login-container" style="max-width:100%;margin:0;">'
            '<h2>\U0001f512 Sign In</h2>'
            '<p>Access your personalised policy dashboard</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. swarnali")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                ok, err = do_login(username.strip(), password)
                if ok:
                    st.rerun()
                else:
                    st.error(err)

        st.caption("Demo: **swarnali** / swarnali123  \u2022  **aritro** / aritro123")

    st.stop()


# ---------------------------------------------------------------------------
# SIDEBAR (logged in)
# ---------------------------------------------------------------------------
with st.sidebar:
    user = st.session_state.user
    initials = user['username'][:2].upper()
    st.markdown(
        f'<div class="user-badge">'
        f'<div class="avatar">{initials}</div>'
        f'<div class="uname">{user["username"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        '<div class="sidebar-brand">\U0001f50d Policy Lens</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-tagline">AI-powered insurance platform</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if st.button("\U0001f3e0 Dashboard", key="nav_dash", use_container_width=True):
        nav("dashboard")
    if st.button("\U0001f4cb My Policies", key="nav_pol", use_container_width=True):
        nav("policies")
    if st.button("\U0001f4ac Ask a Question", key="nav_chat", use_container_width=True):
        nav("chat")
    if st.button("\u2b50 Recommendations", key="nav_rec", use_container_width=True):
        nav("recommendations")

    st.markdown("---")

    if st.button("\U0001f6aa Logout", key="nav_logout", use_container_width=True):
        do_logout()
        st.rerun()



# ---------------------------------------------------------------------------
# PAGE: DASHBOARD
# ---------------------------------------------------------------------------
if st.session_state.page == "dashboard":
    r = api_get("/dashboard/")
    if r.status_code != 200:
        st.error("Failed to load dashboard.")
        st.stop()

    data = r.json()
    uinfo = data["user"]
    policies = data["policies"]
    rec_summary = data["recommendation_summary"]

    st.markdown(f"# Welcome back, **{uinfo['username']}**")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Metrics row
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Policies", len(policies))
    c2.metric("Upgrade Options", rec_summary["upgrade_count"])
    c3.metric("Loan Eligible", rec_summary["loan_count"])

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Policy cards
    st.markdown("### Your Policies")
    if not policies:
        st.info("No active policies found. Contact your provider.")
    else:
        cols = st.columns(min(len(policies), 3))
        for i, pol in enumerate(policies):
            cat_name = pol["tier"]["category"]["name"]
            icon = CATEGORY_ICONS.get(cat_name, "\U0001f4c4")
            with cols[i % len(cols)]:
                st.markdown(
                    f'<div class="policy-card">'
                    f'<div class="card-cat">{icon} {cat_name}</div>'
                    f'<div class="card-tier">{pol["tier"]["display_name"]}</div>'
                    f'<div class="card-num">{pol["policy_number"]}</div>'
                    f'<div class="card-price">\u20b9{pol["tier"]["price_monthly"]}/mo</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Inline Recommendations ───────────────────────────────────────
    if rec_summary["total"] > 0:
        st.markdown("### \u2b50 Recommendations for You")
        with st.spinner("Generating personalised recommendations..."):
            rec_r = api_get("/recommendations/")

        if rec_r.status_code == 200:
            recs = rec_r.json().get("recommendations", [])
            for rec in recs:
                rec_type = rec.get("type", "")
                badge_cls = "rec-badge-upgrade" if rec_type == "upgrade" else "rec-badge-loan"
                badge_txt = "UPGRADE" if rec_type == "upgrade" else "LOAN"

                if rec_type == "upgrade":
                    title = f'{rec["category"]} \u2014 {rec["current_display"]} \u2192 {rec["recommended_display"]}'
                    sub_line = ""
                    if rec.get("current_price") and rec.get("recommended_price"):
                        sub_line = (
                            f'<div style="margin:4px 0 8px;font-size:0.9rem;opacity:0.75;">'
                            f'\u20b9{rec["current_price"]:.0f}/mo \u2192 '
                            f'\u20b9{rec["recommended_price"]:.0f}/mo '
                            f'(+\u20b9{rec["price_difference"]:.0f}/mo)</div>'
                        )
                else:
                    title = f'{rec["category"]} \u2014 Loan against {rec["tier_display"]}'
                    sub_line = (
                        f'<div style="margin:4px 0 8px;font-size:0.9rem;opacity:0.75;">'
                        f'Policy {rec["policy_number"]} \u2022 {rec["months_remaining"]} months remaining</div>'
                    )

                desc = rec.get("description", "")
                st.markdown(
                    f'<div class="rec-card">'
                    f'<span class="{badge_cls}">{badge_txt}</span>'
                    f'<div style="font-size:1.1rem;font-weight:600;margin-bottom:2px;">{title}</div>'
                    f'{sub_line}'
                    f'<div style="opacity:0.85;line-height:1.6;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Recommendations are temporarily unavailable.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Our Offerings ────────────────────────────────────────────────
    st.markdown("### \U0001f4cb Our Offerings")
    st.caption("All available policy categories and tiers.")

    off_r = api_get("/offerings/")
    if off_r.status_code == 200:
        categories = off_r.json().get("categories", [])
        off_cols = st.columns(min(len(categories), 3)) if categories else []
        for idx, cat in enumerate(categories):
            icon = CATEGORY_ICONS.get(cat["name"], "\U0001f4c4")
            with off_cols[idx % len(off_cols)]:
                tier_rows = ""
                for t in cat["tiers"]:
                    badge_cls = f"tier-badge-{t['name']}"
                    price = f"\u20b9{t['price_monthly']:.0f}/mo" if t["price_monthly"] else ""
                    tier_rows += (
                        f'<div class="tier-row">'
                        f'<span class="tier-name {badge_cls}">{t["display_name"]}</span>'
                        f'<span class="tier-price">{price}</span>'
                        f'</div>'
                    )
                st.markdown(
                    f'<div class="offering-card">'
                    f'<div class="offering-cat">{icon} {cat["name"]}</div>'
                    f'<div style="font-size:0.85rem;opacity:0.7;margin-bottom:10px;">{cat["description"]}</div>'
                    f'{tier_rows}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("Offerings are temporarily unavailable.")


# ---------------------------------------------------------------------------
# PAGE: MY POLICIES
# ---------------------------------------------------------------------------
elif st.session_state.page == "policies":
    st.markdown("# My Policies")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    r = api_get("/my-policies/")
    if r.status_code != 200:
        st.error("Failed to load policies.")
        st.stop()

    policies = r.json()
    if not policies:
        st.info("No active policies.")
        st.stop()

    for pol in policies:
        cat = pol["tier"]["category"]
        tier = pol["tier"]
        icon = CATEGORY_ICONS.get(cat["name"], "\U0001f4c4")

        with st.expander(f'{icon} **{tier["display_name"]}** \u2014 {pol["policy_number"]}', expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Category:** {cat['name']}")
                st.markdown(f"**Tier:** {tier['name'].title()}")
                st.markdown(f"**Price:** \u20b9{tier['price_monthly']}/month")
            with col2:
                st.markdown(f"**Policy #:** `{pol['policy_number']}`")
                st.markdown(f"**Start:** {pol['start_date']}")
                st.markdown(f"**End:** {pol['end_date']}")

            if tier.get("highlights"):
                st.markdown(f"**Coverage:** {tier['highlights']}")

            if cat.get("description"):
                st.caption(cat["description"])

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if pol.get("has_document"):
                    if st.button("\U0001f4c4 View Document", key=f"doc_{pol['id']}"):
                        st.session_state[f"show_doc_{pol['id']}"] = True
                else:
                    st.caption("No document uploaded yet")
            with btn_col2:
                if st.button("\U0001f4ac Ask about this policy", key=f"chat_{pol['id']}"):
                    st.session_state.active_policy_id = pol["id"]
                    st.session_state.chat_history = []
                    nav("chat")
                    st.session_state.page = "chat"
                    st.rerun()

            if st.session_state.get(f"show_doc_{pol['id']}"):
                with st.spinner("Loading document..."):
                    doc_resp = api_get(f"/my-policies/{pol['id']}/document/")
                    if doc_resp.status_code == 200:
                        st.download_button(
                            label="\u2b07\ufe0f Download PDF",
                            data=doc_resp.content,
                            file_name=f"{pol['policy_number']}.pdf",
                            mime="application/pdf",
                            key=f"dl_{pol['id']}",
                        )
                    else:
                        st.warning("Document not available.")


# ---------------------------------------------------------------------------
# PAGE: CHAT (Q&A)
# ---------------------------------------------------------------------------
elif st.session_state.page == "chat":
    st.markdown("# Ask a Question")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Policy selector
    r = api_get("/my-policies/")
    if r.status_code == 200:
        policies = r.json()
    else:
        policies = []

    if policies:
        options = ["All my policies"] + [
            f'{p["tier"]["display_name"]} ({p["policy_number"]})'
            for p in policies
        ]
        policy_ids = [None] + [p["id"] for p in policies]

        # Find the index if a policy was pre-selected
        default_idx = 0
        if st.session_state.active_policy_id:
            try:
                default_idx = policy_ids.index(st.session_state.active_policy_id)
            except ValueError:
                default_idx = 0

        selected = st.selectbox("Scope to policy:", options, index=default_idx)
        selected_id = policy_ids[options.index(selected)]
        st.session_state.active_policy_id = selected_id

    st.markdown("---")

    # Chat history display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Ask anything about your policy...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching your policy..."):
                payload = {
                    "question": prompt,
                    "chat_history": st.session_state.chat_history[:-1],
                }

                pid = st.session_state.active_policy_id
                if pid:
                    resp = api_post(f"/my-policies/{pid}/query/", json=payload)
                else:
                    resp = api_post("/query/", json=payload)

                if resp.status_code == 200:
                    answer_data = resp.json()
                    answer = answer_data.get("answer", "Sorry, something went wrong.")
                    st.markdown(answer)
                    st.session_state.chat_history.append({
                        "role": "assistant", "content": answer,
                    })

                    sources = answer_data.get("sources", [])
                    if sources:
                        with st.expander("Sources"):
                            for s in sources:
                                st.caption(
                                    f'{s.get("doc_name", "?")} \u2014 '
                                    f'p.{s.get("page", "?")} | '
                                    f'{s.get("tier", "")} | '
                                    f'{s.get("policy_number", "")}'
                                )
                else:
                    err = "Failed to get an answer. Please try again."
                    try:
                        err = resp.json().get("error", err)
                    except Exception:
                        pass
                    st.error(err)


# ---------------------------------------------------------------------------
# PAGE: RECOMMENDATIONS
# ---------------------------------------------------------------------------
elif st.session_state.page == "recommendations":
    st.markdown("# Recommendations")
    st.markdown("Personalised suggestions based on your current policies.")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.spinner("Generating recommendations..."):
        r = api_get("/recommendations/")

    if r.status_code != 200:
        st.error("Failed to load recommendations.")
        st.stop()

    recs = r.json().get("recommendations", [])
    if not recs:
        st.success("You're all set! No recommendations at this time.")
        st.stop()

    for rec in recs:
        rec_type = rec.get("type", "")
        badge_cls = "rec-badge-upgrade" if rec_type == "upgrade" else "rec-badge-loan"
        badge_txt = "UPGRADE" if rec_type == "upgrade" else "LOAN"

        if rec_type == "upgrade":
            title = f'{rec["category"]} \u2014 {rec["current_display"]} \u2192 {rec["recommended_display"]}'
            sub_line = ""
            if rec.get("current_price") and rec.get("recommended_price"):
                sub_line = (
                    f'<div style="margin:4px 0 8px;font-size:0.9rem;opacity:0.75;">'
                    f'\u20b9{rec["current_price"]:.0f}/mo \u2192 '
                    f'\u20b9{rec["recommended_price"]:.0f}/mo '
                    f'(+\u20b9{rec["price_difference"]:.0f}/mo)</div>'
                )
        else:
            title = f'{rec["category"]} \u2014 Loan against {rec["tier_display"]}'
            sub_line = (
                f'<div style="margin:4px 0 8px;font-size:0.9rem;opacity:0.75;">'
                f'Policy {rec["policy_number"]} \u2022 {rec["months_remaining"]} months remaining</div>'
            )

        desc = rec.get("description", "")

        st.markdown(
            f'<div class="rec-card">'
            f'<span class="{badge_cls}">{badge_txt}</span>'
            f'<div style="font-size:1.1rem;font-weight:600;margin-bottom:2px;">{title}</div>'
            f'{sub_line}'
            f'<div style="opacity:0.85;line-height:1.6;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
