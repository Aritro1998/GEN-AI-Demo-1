"""Streamlit frontend for the AI Hackathon multimodal incident analysis platform."""

import io

import requests
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://127.0.0.1:8000/api"

CATEGORIES = ["CPU", "Memory", "I/O", "Network", "Others"]

# ---------------------------------------------------------------------------
# Page config & global styles
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Incident Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ---- Global ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
    }
    section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    section[data-testid="stSidebar"] .stRadio label:hover { color: #fff !important; }

    /* ---- Status badge ---- */
    .status-badge {
        display: inline-block; padding: 6px 18px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem; letter-spacing: 0.4px;
    }
    .status-online  { background: #00c853; color: #fff; }
    .status-offline { background: #ff1744; color: #fff; }

    /* ---- Cards ---- */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px; padding: 28px; color: #fff; text-align: center;
        box-shadow: 0 8px 32px rgba(102,126,234,.25);
    }
    .metric-card h2 { margin: 0 0 4px; font-size: 2rem; }
    .metric-card p  { margin: 0; opacity: .85; font-size: .95rem; }

    .result-card {
        background: #ffffff08; border: 1px solid #ffffff18;
        border-radius: 14px; padding: 24px; margin-bottom: 16px;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        border-radius: 10px; font-weight: 600; padding: 0.55rem 2rem;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(102,126,234,.35);
    }

    /* ---- Spinner ---- */
    .processing-msg {
        text-align: center; padding: 40px; font-size: 1.1rem;
        color: #b0b0b0; animation: pulse 1.8s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100%{opacity:.5} 50%{opacity:1} }

    /* ---- Divider ---- */
    .section-divider {
        height: 3px; border-radius: 2px; margin: 32px 0;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def check_health() -> bool:
    """Return True when the backend /api/health/ endpoint responds 200."""
    try:
        r = requests.get(f"{API_BASE}/health/", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def post_process(text: str, audio_file=None, image_files=None) -> dict:
    """POST multipart form-data to /api/process/ and return the JSON body."""
    data = {}
    files = []

    if text:
        data["text"] = text
    if audio_file is not None:
        files.append(("audio", (audio_file.name, audio_file, audio_file.type)))
    for img in (image_files or []):
        files.append(("images", (img.name, img, img.type)))

    # Always send at least one file tuple so requests uses multipart encoding,
    # which the Django backend's MultiPartParser expects.
    if not files:
        files = [("_dummy", ("", b"", "application/octet-stream"))]

    r = requests.post(
        f"{API_BASE}/process/",
        data=data,
        files=files,
        timeout=300,
    )
    if not r.ok:
        detail = ""
        try:
            detail = r.json().get("details") or r.json().get("error") or r.text
        except Exception:
            detail = r.text
        raise Exception(f"Backend error ({r.status_code}): {detail}")
    return r.json()


def post_knowledge(payload: dict) -> dict:
    """POST JSON to /api/knowledge/."""
    r = requests.post(f"{API_BASE}/knowledge/", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def post_promote(payload: dict) -> dict:
    """POST JSON to /api/knowledge/promote/."""
    r = requests.post(f"{API_BASE}/knowledge/promote/", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔍 Incident Analyzer")
    st.caption("AI-powered infrastructure RCA platform")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "⚡ Analyze Incident", "📚 Add Knowledge"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    # Live health indicator
    backend_ok = check_health()
    badge = "status-online" if backend_ok else "status-offline"
    label = "Backend Online" if backend_ok else "Backend Offline"
    st.markdown(
        f'<div style="text-align:center"><span class="status-badge {badge}">{label}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.caption("Django REST API  •  Port 8000")


# ===================================================================
# PAGE: Dashboard
# ===================================================================
if page == "🏠 Dashboard":
    st.markdown("# 🏠 Dashboard")
    st.markdown("Welcome to the **Incident Analyzer** — a multimodal AI platform that classifies, "
                "investigates, and generates Root Cause Analysis reports from text, audio, and screenshots.")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="metric-card"><h2>⚡</h2><p>Analyze incidents with text, audio &amp; images</p></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="metric-card"><h2>📚</h2><p>Build a knowledge base for RAG retrieval</p></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-card"><h2>🚀</h2><p>Promote reviewed outputs to knowledge</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("### How it works")
    st.markdown(
        """
        1. **Submit an incident** — paste logs, upload screenshots, or attach an audio note.
        2. **AI pipeline runs** — classification → root-cause reasoning (with RAG) → RCA report generation.
        3. **Review the report** — if it looks good, promote it to your knowledge base for future retrieval.
        """
    )


# ===================================================================
# PAGE: Analyze Incident
# ===================================================================
elif page == "⚡ Analyze Incident":
    st.markdown("# ⚡ Analyze Incident")
    st.markdown("Submit an infrastructure issue for AI-powered analysis. "
                "Provide **text**, **screenshots**, and/or an **audio note**.")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # --- Audio recorder (outside form — custom components can't live inside st.form) ---
    st.markdown("#### 🎙️ Record Audio Note (optional)")
    st.caption("Click the mic to start recording, click again to stop.")
    audio_data = mic_recorder(
        start_prompt="🔴  Start Recording",
        stop_prompt="⏹️  Stop Recording",
        just_once=False,
        use_container_width=False,
        key="mic_recorder",
    )
    if audio_data and audio_data.get("bytes"):
        st.audio(audio_data["bytes"], format="audio/wav")
        st.session_state["recorded_audio"] = audio_data["bytes"]

    st.markdown("---")

    with st.form("process_form"):
        text_input = st.text_area(
            "Incident description / logs",
            height=200,
            placeholder="Paste your incident description, error logs, metrics here…",
        )

        image_files = st.file_uploader(
            "Screenshots (optional)",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            accept_multiple_files=True,
        )

        submitted = st.form_submit_button("🔍  Analyze", use_container_width=True)

    if submitted:
        recorded_bytes = st.session_state.get("recorded_audio")
        audio_file = None
        if recorded_bytes:
            audio_file = io.BytesIO(recorded_bytes)
            audio_file.name = "recording.wav"
            audio_file.type = "audio/wav"

        if not text_input.strip() and not audio_file and not image_files:
            st.warning("Please provide at least one input — text, image, or audio.")
        else:
            with st.spinner(""):
                st.markdown(
                    '<div class="processing-msg">🧠 AI pipeline is analyzing your incident… '
                    'This may take a minute or two.</div>',
                    unsafe_allow_html=True,
                )
                try:
                    result = post_process(text_input, audio_file, image_files)
                    st.session_state["last_result"] = result
                    st.session_state.pop("recorded_audio", None)
                    st.success("Analysis complete!")
                except Exception as exc:
                    st.error(f"Request failed: {exc}")
                    result = None

    # Display results
    result = st.session_state.get("last_result")
    if result:
        output = result.get("output", {})
        step_outputs = output.get("step_outputs", {})

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Results")

        # Classification badge
        classification = step_outputs.get("classification", "N/A").strip()
        st.markdown(f"**Category:**  `{classification}`")

        # Tabs for different outputs
        tab_rca, tab_analysis, tab_raw = st.tabs(["📝 RCA Report", "🔬 Technical Analysis", "📦 Raw Output"])

        with tab_rca:
            final = step_outputs.get("final_output", output.get("final_output", ""))
            if final:
                st.markdown(final)
            else:
                st.info("No RCA report generated.")

        with tab_analysis:
            analysis = step_outputs.get("analysis", "")
            if analysis:
                st.markdown(analysis)
            else:
                st.info("No technical analysis available.")

        with tab_raw:
            st.json(result)

        # Promote section
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 🚀 Promote this result to Knowledge Base")
        st.caption("If this analysis looks accurate, promote it so future incidents benefit from RAG retrieval.")

        with st.form("promote_from_result"):
            p_title = st.text_input("Title", placeholder="Short title for this incident")
            p_summary = st.text_input("Summary", placeholder="One-line summary")
            p_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(classification) if classification in CATEGORIES else 4)
            p_notes = st.text_area("Notes (optional)", height=80, placeholder="Any reviewer notes…")

            promote_clicked = st.form_submit_button("🚀  Promote to Knowledge", use_container_width=True)

        if promote_clicked:
            if not p_title.strip() or not p_summary.strip():
                st.warning("Title and Summary are required to promote.")
            else:
                final_output_text = step_outputs.get("final_output", output.get("final_output", ""))
                analysis_text = step_outputs.get("analysis", "")
                payload = {
                    "title": p_title.strip(),
                    "summary": p_summary.strip(),
                    "description": analysis_text or final_output_text,
                    "category": p_category,
                    "notes": p_notes.strip(),
                    "final_output": final_output_text,
                    "source": "promoted_output",
                }
                try:
                    resp = post_promote(payload)
                    st.success(resp.get("message", "Promoted successfully!"))
                except requests.exceptions.RequestException as exc:
                    st.error(f"Promote failed: {exc}")


# ===================================================================
# PAGE: Add Knowledge
# ===================================================================
elif page == "📚 Add Knowledge":
    st.markdown("# 📚 Add Knowledge Entry")
    st.markdown("Manually add a reviewed incident record to the knowledge base for RAG retrieval.")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    with st.form("knowledge_form"):
        k_title = st.text_input("Title *", placeholder="e.g. Checkout 502 after deploy")
        k_summary = st.text_area("Summary *", height=80, placeholder="Brief summary of the incident…")
        k_description = st.text_area(
            "Description *", height=160,
            placeholder="Detailed description — root cause, resolution, evidence…",
        )

        col1, col2 = st.columns(2)
        with col1:
            k_category = st.selectbox("Category", CATEGORIES, index=4)
        with col2:
            k_source = st.text_input("Source", value="manual")

        k_notes = st.text_area("Notes (optional)", height=80, placeholder="Any additional notes…")

        k_submitted = st.form_submit_button("📥  Add to Knowledge Base", use_container_width=True)

    if k_submitted:
        if not k_title.strip() or not k_summary.strip() or not k_description.strip():
            st.warning("Title, Summary, and Description are required.")
        else:
            payload = {
                "title": k_title.strip(),
                "summary": k_summary.strip(),
                "description": k_description.strip(),
                "category": k_category,
                "notes": k_notes.strip(),
                "source": k_source.strip() or "manual",
            }
            try:
                resp = post_knowledge(payload)
                st.success(resp.get("message", "Knowledge entry added!"))
                with st.expander("Response details"):
                    st.json(resp)
            except requests.exceptions.RequestException as exc:
                st.error(f"Failed to add knowledge entry: {exc}")
