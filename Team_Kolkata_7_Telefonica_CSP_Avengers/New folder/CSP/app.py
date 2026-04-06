import pandas as pd  # type: ignore
import re
import streamlit as st  # type: ignore

from app_logic import (
    predict_incident_resolution,
    prepare_ticket_dataframe,
    process_dataframe,
)


def _extract_section(summary: str, section: str) -> str:
    pattern = rf"{section}:\s*(.*?)(?=\n[A-Za-z ]+:\s|$)"
    match = re.search(pattern, summary, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _to_bullets(text: str, max_items: int = 3) -> list[str]:
    if not text:
        return []

    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    if len(lines) == 1:
        lines = [
            part.strip(" -")
            for part in re.split(r"(?<=[.!?])\s+", lines[0])
            if part.strip()
        ]

    cleaned: list[str] = []
    seen = set()
    for line in lines:
        line = line.rstrip(".").strip()
        if not line:
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(line)
        if len(cleaned) >= max_items:
            break

    return cleaned


def render_search_summary(record: pd.Series) -> None:
    summary = str(record.get("summary", ""))
    issue = _extract_section(summary, "Issue")
    impact = _extract_section(summary, "Impact")
    resolution = _extract_section(summary, "Resolution")
    current_status = _extract_section(summary, "Current Status")

    resolution_bullets = _to_bullets(resolution, max_items=3)
    status_bullets = _to_bullets(current_status, max_items=3)

    st.markdown("### Incident Summary")
    st.markdown(f"**Incident ID:** {record['incident_id']}")
    st.markdown(f"**Priority:** {record['priority']}")

    if issue:
        st.markdown("**Issue**")
        st.markdown(f"- {issue.rstrip('.')}.")
    if impact:
        st.markdown("**Impact**")
        st.markdown(f"- {impact.rstrip('.')}.")
    if resolution_bullets:
        st.markdown("**Resolution**")
        for bullet in resolution_bullets:
            st.markdown(f"- {bullet}.")
    if status_bullets:
        st.markdown("**Current Status**")
        for bullet in status_bullets:
            st.markdown(f"- {bullet}.")

    next_steps: list[str] = []
    if resolution_bullets:
        next_steps.append(f"Confirm the applied fix remains stable: {resolution_bullets[0]}.")
    if any("monitor" in item.lower() for item in status_bullets):
        next_steps.append("Continue active monitoring to ensure there is no recurrence.")
    priority = str(record.get("priority", "Medium"))
    if priority in {"Critical", "High"}:
        next_steps.append("Provide frequent stakeholder updates until service performance is consistently normal.")
    else:
        next_steps.append("Close the incident after validation checks confirm stability across the next monitoring window.")

    st.markdown("**Recommended Next Steps**")
    for step in next_steps[:3]:
        st.markdown(f"- {step}")


st.set_page_config(page_title="Incident AI Assistant", layout="wide")

st.title("AI Incident Summary Generator")
st.markdown("Default dataset is auto-loaded for analysis and prediction.")

if "results" not in st.session_state:
    st.session_state.results = []
if "ticket_df" not in st.session_state:
    st.session_state.ticket_df = None
if "base_loaded" not in st.session_state:
    st.session_state.base_loaded = False
if "dataset_status" not in st.session_state:
    st.session_state.dataset_status = ""

with st.sidebar:
    st.header("Configuration")
    st.caption("Set `GENAILAB_API_KEY` in your environment to enable live LLM summarization.")

if not st.session_state.base_loaded:
    try:
        with st.spinner("Loading default dataset from data/incidents.csv..."):
            base_df = pd.read_csv("data/incidents.csv")
            prepared_base_df = prepare_ticket_dataframe(base_df)
            st.session_state.ticket_df = prepared_base_df
            st.session_state.results = process_dataframe(prepared_base_df)
        st.session_state.dataset_status = (
            f"Default dataset loaded: {len(prepared_base_df)} incidents."
        )
    except ValueError as exc:
        st.session_state.results = []
        st.session_state.ticket_df = None
        st.session_state.dataset_status = f"Failed to load default dataset: {exc}"
    finally:
        st.session_state.base_loaded = True

if st.session_state.dataset_status:
    st.info(st.session_state.dataset_status)

results = st.session_state.results
if results:
    results_df = pd.DataFrame(results)

    priority_order = ["Critical", "High", "Medium", "Low"]
    priority_counts = (
        results_df["priority"]
        .value_counts()
        .reindex(priority_order, fill_value=0)
        .reset_index()
    )
    priority_counts.columns = ["Priority", "Total Incidents"]

    st.subheader("Priority-wise Incident Distribution")
    st.bar_chart(
        data=priority_counts.set_index("Priority")["Total Incidents"],
        use_container_width=True,
    )

    st.dataframe(priority_counts, use_container_width=True)

    st.subheader("Filter Incidents by Priority")
    selected_priority = st.selectbox(
        "Choose priority",
        options=["Select priority", "Critical", "High", "Medium", "Low"],
        index=0,
    )

    if selected_priority == "Select priority":
        filtered_df = results_df.iloc[0:0].copy()
    else:
        filtered_df = results_df[results_df["priority"] == selected_priority]

    st.markdown(f"**Total incidents shown:** {len(filtered_df)}")
    table_df = filtered_df[["incident_id", "priority", "reported_on"]].reset_index(
        drop=True
    )
    if selected_priority == "Select priority":
        st.dataframe(table_df, use_container_width=True, hide_index=True)
        st.info("Choose a priority to view incidents.")
    else:
        table_event = st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        selected_rows = table_event.selection.rows
        if selected_rows:
            selected_row = selected_rows[0]
            selected_incident_id = table_df.iloc[selected_row]["incident_id"]
            selected_record = filtered_df[
                filtered_df["incident_id"] == selected_incident_id
            ].iloc[0]
            render_search_summary(selected_record)
        else:
            st.info("Select an incident row from the table to view its summary.")

    st.subheader("Search Incident Summary")
    search_id = st.text_input(
        "Enter Incident ID",
        placeholder="Example: INC014",
    ).strip()

    if search_id:
        matched = results_df[
            results_df["incident_id"].str.upper() == search_id.upper()
        ]
        if matched.empty:
            st.warning(f"No incident found for '{search_id}'.")
        else:
            record = matched.iloc[0]
            render_search_summary(record)

st.subheader("1) Predict Resolution (RAG)")
with st.form("rag_resolution_form"):
    rag_priority = st.selectbox(
        "Priority *",
        options=["Select priority", "Critical", "High", "Medium", "Low"],
        index=0,
    )
    rag_issue = st.text_area(
        "Issue Description *",
        placeholder="Describe the issue in detail...",
        height=120,
    )
    rag_submit = st.form_submit_button("Predict Resolution")

if rag_submit:
    if rag_priority == "Select priority":
        st.error("Please select a priority.")
    elif not rag_issue.strip():
        st.error("Please enter the issue description.")
    elif st.session_state.ticket_df is None:
        st.error("No incident dataset available for RAG retrieval.")
    else:
        with st.spinner("Retrieving similar incidents and predicting resolution..."):
            rag_result = predict_incident_resolution(
                priority=rag_priority,
                issue_description=rag_issue.strip(),
                tickets_df=st.session_state.ticket_df,
            )

        st.markdown("### Predicted Resolution")
        st.markdown(rag_result["prediction"])
        st.caption(f"Source: {rag_result['source']}")

        similar_cases = rag_result.get("similar_cases", [])
        if similar_cases:
            st.markdown("### Retrieved Similar Past Incidents")
            similar_df = pd.DataFrame(similar_cases)
            st.dataframe(
                similar_df[
                    [
                        "incident_id",
                        "priority",
                        "description",
                        "resolution_notes",
                        "similarity",
                    ]
                ],
                use_container_width=True,
            )
