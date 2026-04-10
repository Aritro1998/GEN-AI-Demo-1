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
    "Home": "\U0001f3e0",
    "Life": "\U0001f9ec",
    "Travel": "\u2708\ufe0f",
}

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PolicyHub",
    page_icon="\U0001f6e1\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628, #162544, #1a3a5c);
    }
    section[data-testid="stSidebar"] * { color: #d0d8e8 !important; }
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.05);
        color: #f0f4ff !important;
        font-size: 1rem;
        font-weight: 600;
        text-align: left;
        padding: 0.8rem 1rem;
        margin-bottom: 0.4rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.12);
        border-color: rgba(255,255,255,0.25);
    }
    .sidebar-brand {
        font-size: 1.8rem; font-weight: 700; color: #fff;
        margin-bottom: 0.2rem;
    }
    .sidebar-tagline {
        font-size: 0.92rem; color: rgba(200,215,240,0.75);
        margin-bottom: 1.2rem; line-height: 1.5;
    }
    .status-pill {
        display: inline-block; padding: 4px 14px; border-radius: 16px;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.3px;
    }
    .status-on  { background: #00c853; color: #fff; }
    .status-off { background: #ff1744; color: #fff; }

    /* Cards */
    .policy-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
        border-radius: 16px; padding: 24px; color: #fff;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        margin-bottom: 12px; min-height: 160px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .policy-card .card-cat {
        font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;
        opacity: 0.8; margin-bottom: 4px;
    }
    .policy-card .card-tier {
        font-size: 1.35rem; font-weight: 700; margin-bottom: 6px;
    }
    .policy-card .card-num {
        font-size: 0.85rem; opacity: 0.7; font-family: monospace;
    }
    .policy-card .card-price {
        font-size: 1.1rem; font-weight: 600; margin-top: 8px;
    }

    .rec-card {
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 14px; padding: 20px; margin-bottom: 12px;
        background: rgba(255,255,255,0.03);
    }
    .rec-badge-upgrade {
        display: inline-block; padding: 3px 10px; border-radius: 10px;
        font-size: 0.72rem; font-weight: 700; background: #4caf50; color: #fff;
        margin-bottom: 8px;
    }
    .rec-badge-loan {
        display: inline-block; padding: 3px 10px; border-radius: 10px;
        font-size: 0.72rem; font-weight: 700; background: #2196f3; color: #fff;
        margin-bottom: 8px;
    }

    /* Divider */
    .divider {
        height: 2px; border-radius: 1px; margin: 28px 0;
        background: linear-gradient(90deg, #1e3a5f, #4a90d9, #1e3a5f);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px; font-weight: 600; padding: 0.5rem 1.6rem;
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(30,58,95,0.3);
    }

    /* Login form styling */
    .login-container {
        max-width: 420px; margin: 80px auto; padding: 40px;
        border-radius: 20px;
        background: linear-gradient(145deg, #0e1a2e, #1a3050);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        text-align: center; color: #e0e8f5;
    }
    .login-container h2 {
        color: #fff; margin-bottom: 4px; font-size: 1.6rem;
    }
    .login-container p {
        color: rgba(200,215,240,0.7); font-size: 0.92rem; margin-bottom: 24px;
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
    st.markdown(
        '<div class="login-container">'
        '<h2>\U0001f6e1\ufe0f PolicyHub</h2>'
        '<p>Sign in to access your insurance policies</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. alice")
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

        st.caption("Demo accounts: **alice** / alice123  |  **bob** / bob123")

    st.stop()


# ---------------------------------------------------------------------------
# SIDEBAR (logged in)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">\U0001f6e1\ufe0f PolicyHub</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-tagline">Your insurance policies, AI-powered Q&A, and smart recommendations.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    user = st.session_state.user
    st.markdown(f"**{user['username']}**")

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

    st.markdown("---")
    ok = check_health()
    pill = "status-on" if ok else "status-off"
    lbl = "Online" if ok else "Offline"
    st.markdown(
        f'<div style="text-align:center"><span class="status-pill {pill}">Backend {lbl}</span></div>',
        unsafe_allow_html=True,
    )


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

    if rec_summary["total"] > 0:
        st.markdown(
            f"You have **{rec_summary['total']}** personalised recommendations. "
        )
        if st.button("View Recommendations \u2192"):
            nav("recommendations")
            st.rerun()


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

            if st.button(f"Ask about this policy \u2192", key=f"chat_{pol['id']}"):
                st.session_state.active_policy_id = pol["id"]
                st.session_state.chat_history = []
                nav("chat")
                st.session_state.page = "chat"
                st.rerun()


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
            price_info = ""
            if rec.get("price_difference") is not None:
                price_info = f' (+\u20b9{rec["price_difference"]:.0f}/mo)'
        else:
            title = f'{rec["category"]} \u2014 Loan against {rec["tier_display"]}'
            price_info = f' | {rec["months_remaining"]} months remaining'

        desc = rec.get("description", "")

        st.markdown(
            f'<div class="rec-card">'
            f'<span class="{badge_cls}">{badge_txt}</span>'
            f'<div style="font-size:1.1rem;font-weight:600;margin-bottom:6px;">{title}{price_info}</div>'
            f'<div style="opacity:0.85;line-height:1.6;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
