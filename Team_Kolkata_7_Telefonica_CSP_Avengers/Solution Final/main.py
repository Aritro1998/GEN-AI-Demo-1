import json
import os
import random
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    AzureOpenAI,
    DefaultHttpxClient,
    OpenAI,
)


def getenv_any(*keys: str, default: str = "") -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value.strip()
    return default


def generate_synthetic_tickets(size: int = 5) -> list[dict]:
    priorities = ["P1 - Critical", "P2 - High", "P3 - Medium", "P4 - Low"]
    systems = [
        "Payment API Gateway",
        "Payroll Processing Engine",
        "Corporate VPN Service",
        "Windows Patch Management",
        "Primary SAN Storage Cluster",
        "Service Desk Portal",
        "Identity Provider (SSO)",
        "Customer Notifications Service",
    ]
    symptoms = [
        "intermittent 502 responses and rising error rates",
        "job failures with repeated retry exhaustion",
        "high authentication latency and sporadic login timeouts",
        "policy conflict errors preventing endpoint compliance",
        "disk I/O saturation and queue-depth spikes",
        "unexpected service unavailability after config sync",
        "token validation failures for active sessions",
        "message delivery backlog growing beyond SLA",
    ]
    actions = [
        "On-call engineer restarted the affected pods and cleared stale sessions",
        "Team rolled back the most recent deployment and re-applied baseline config",
        "Ops enabled temporary traffic shaping to reduce user impact",
        "Vendor support was engaged and diagnostic bundles were shared",
        "Database failover simulation was executed to validate resilience",
        "Infra team expanded capacity and tuned connection pools",
    ]
    evidence = [
        "Logs show error bursts between 08:40 and 09:05 UTC with correlation IDs attached",
        "Monitoring captured CPU above 90% and API p95 latency crossing 4.2s",
        "Audit trail indicates a policy update 17 minutes before first alert",
        "Synthetic checks failed from two regions while internal health checks remained green",
        "Queue depth tripled compared to daily baseline, indicating cascading degradation",
    ]
    assignees = ["Ops Team", "Infra Team", "App Support", "Service Desk", "Platform SRE"]

    tickets: list[dict] = []
    now = datetime.now()
    for i in range(size):
        ticket_id = f"INC-{100000 + i}"
        created = now - timedelta(minutes=random.randint(10, 72 * 60))
        is_resolved = random.random() < 0.3
        resolved_at = ""
        resolution_notes = ""

        if is_resolved:
            resolved_time = created + timedelta(minutes=random.randint(20, 24 * 60))
            if resolved_time > now:
                resolved_time = now - timedelta(minutes=random.randint(1, 30))
            resolved_at = resolved_time.strftime("%Y-%m-%d %H:%M:%S")
            resolution_notes = (
                f"Resolved by {random.choice(actions)}. Root cause confirmed after log correlation and "
                "post-change validation. Service restored and alerts normalized; closure approved by incident manager."
            )

        system = random.choice(systems)
        symptom = random.choice(symptoms)
        detail_description = (
            f"{system} is experiencing {symptom}. Multiple teams reported degraded behavior impacting internal "
            "users and dependent services. "
            f"{random.choice(evidence)}. "
            f"Initial mitigation: {random.choice(actions)}. "
            "Stakeholders requested regular status updates with next-action ownership and ETA."
        )
        priority = random.choice(priorities)
        tickets.append(
            {
                "ticket_id": ticket_id,
                "priority": priority,
                "timestamp": created.strftime("%Y-%m-%d %H:%M:%S"),
                "description": detail_description,
                "status": "Resolved" if is_resolved else "Open",
                "resolved_at": resolved_at,
                "resolution_notes": resolution_notes,
                "assignee": random.choice(assignees),
            }
        )
    return tickets


def normalize_base_url(endpoint: str) -> str:
    cleaned = endpoint.strip().strip('"').strip("'").rstrip("/")
    if cleaned.endswith("/v1"):
        return cleaned
    return f"{cleaned}/v1"


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def build_client() -> tuple[Any | None, str, str, str]:
    load_dotenv()
    api_key = getenv_any("API_KEY", "api_key")
    endpoint = getenv_any("API_ENDPOINT", "api_endpoint")
    model = getenv_any("MODEL_NAME", "model", default="gpt-4o-mini").strip().strip('"').strip("'")
    use_system_proxy = as_bool(getenv_any("USE_SYSTEM_PROXY", default="false"))
    verify_ssl_raw = getenv_any("VERIFY_SSL", default="true")
    ca_bundle_path = getenv_any("CA_BUNDLE_PATH", default="")

    if not api_key or not endpoint:
        return None, model, "", "Missing API config in .env (api_key + api_endpoint are required)."

    normalized_endpoint = endpoint.strip().strip('"').strip("'")
    verify: bool | str = as_bool(verify_ssl_raw)
    if ca_bundle_path:
        verify = ca_bundle_path.strip().strip('"').strip("'")
    http_client = DefaultHttpxClient(trust_env=use_system_proxy, verify=verify)
    if "openai.azure.com" in normalized_endpoint.lower():
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=normalized_endpoint,
            api_version="2024-02-15-preview",
            http_client=http_client,
        )
        return client, model, "azure", ""

    # OpenAI-compatible providers often expose a v1-style base URL.
    client = OpenAI(
        api_key=api_key,
        base_url=normalize_base_url(normalized_endpoint),
        http_client=http_client,
    )
    return client, model, "openai_compatible", ""


def generate_incident_summary(client: Any, model: str, ticket: dict) -> str:
    payload = json.dumps(ticket, ensure_ascii=True)
    prompt = (
        "Create a concise incident summary for IT stakeholders in this exact markdown format:\n"
        "### Situation Summary\n"
        "<1 sentence>\n\n"
        "### Impact Scope\n"
        "<scope and affected users/systems>\n\n"
        "### Priority Cue\n"
        "<urgency guidance inferred from incident description and current status>\n\n"
        "### Recommended Next Steps\n"
        "1. <action>\n"
        "2. <action>\n"
        "3. <action>\n\n"
        "Important: infer urgency from ticket description/status; do not assume a precomputed priority cue field.\n\n"
        f"Ticket data: {payload}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert ITSM incident communicator. "
                    "Be concise, factual, and avoid invented details."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "No summary generated."


def normalize_tickets(records: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    required = ["ticket_id", "priority", "timestamp", "description"]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    if "resolution_notes" not in df.columns:
        df["resolution_notes"] = ""
    if "assignee" not in df.columns:
        df["assignee"] = ""
    if "status" not in df.columns:
        df["status"] = "Open"
    if "resolved_at" not in df.columns:
        df["resolved_at"] = ""
    return df[
        [
            "ticket_id",
            "priority",
            "status",
            "timestamp",
            "resolved_at",
            "assignee",
            "description",
            "resolution_notes",
        ]
    ]


def build_stakeholder_update_text(summary_map: dict[str, str], source_df: pd.DataFrame) -> str:
    report_lines = [
        "INCIDENT STAKEHOLDER UPDATE",
        f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Summarized Incidents: {len(summary_map)}",
        "",
    ]

    for idx, (ticket_id, summary) in enumerate(summary_map.items(), start=1):
        row = source_df[source_df["ticket_id"].astype(str) == str(ticket_id)]
        meta = row.iloc[0].to_dict() if not row.empty else {}

        report_lines.extend(
            [
                "=" * 90,
                f"Incident {idx}: {ticket_id}",
                "=" * 90,
                f"Priority      : {meta.get('priority', 'N/A')}",
                f"Status        : {meta.get('status', 'N/A')}",
                f"Assignee      : {meta.get('assignee', 'N/A')}",
                f"Created Time  : {meta.get('timestamp', 'N/A')}",
                f"Resolved Time : {meta.get('resolved_at', 'N/A') or 'N/A'}",
                "",
                "AI INCIDENT SUMMARY",
                "-" * 90,
                str(summary).strip(),
                "",
                "ORIGINAL INCIDENT DESCRIPTION",
                "-" * 90,
                str(meta.get("description", "N/A")).strip(),
            ]
        )

        notes = str(meta.get("resolution_notes", "")).strip()
        if notes:
            report_lines.extend(
                [
                    "",
                    "RESOLUTION NOTES",
                    "-" * 90,
                    notes,
                ]
            )

        report_lines.append("")

    return "\n".join(report_lines).strip() + "\n"


st.set_page_config(page_title="Incident Summarizer Agent", layout="wide")
st.title("AI-Powered Incident Summary Agent")
st.caption("Summarize raw IT incidents into concise stakeholder updates.")

client, model, provider_mode, config_error = build_client()
if config_error:
    st.warning(config_error)

if "tickets_df" not in st.session_state:
    st.session_state["tickets_df"] = pd.DataFrame()
if "summaries" not in st.session_state:
    st.session_state["summaries"] = {}

with st.sidebar:
    st.header("Data Ingestion")
    uploaded = st.file_uploader("Upload tickets (JSON or CSV)", type=["json", "csv"])
    if uploaded is not None:
        if uploaded.name.lower().endswith(".json"):
            records = json.loads(uploaded.read().decode("utf-8"))
            st.session_state["tickets_df"] = normalize_tickets(records)
        else:
            df_upload = pd.read_csv(uploaded)
            st.session_state["tickets_df"] = normalize_tickets(df_upload.to_dict(orient="records"))
        st.success(f"Loaded {len(st.session_state['tickets_df'])} ticket(s).")

    synthetic_size = st.slider("Generate synthetic tickets", min_value=10, max_value=1000, value=100, step=10)
    if st.button("Generate Synthetic Data"):
        st.session_state["tickets_df"] = normalize_tickets(generate_synthetic_tickets(synthetic_size))
        st.success(f"Generated {synthetic_size} synthetic tickets.")

    st.divider()
    st.subheader("Add Incident Manually")
    with st.form("manual_incident_form", clear_on_submit=False):
        manual_ticket_id = st.text_input("ticket_id *", placeholder="INC-200001")
        manual_priority = st.selectbox(
            "priority *",
            options=["P1 - Critical", "P2 - High", "P3 - Medium", "P4 - Low"],
            index=2,
        )
        manual_status = st.selectbox("status *", options=["Open", "Resolved"], index=0)
        manual_timestamp = st.text_input(
            "timestamp *",
            value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            help="Format: YYYY-MM-DD HH:MM:SS",
        )
        manual_assignee = st.text_input("assignee *", placeholder="App Support")
        manual_description = st.text_area(
            "description *",
            height=140,
            placeholder="Provide detailed incident context, impact, timeline, and mitigation actions.",
        )
        manual_resolved_at = st.text_input(
            "resolved_at",
            value="",
            help="Required if status is Resolved. Format: YYYY-MM-DD HH:MM:SS",
        )
        manual_resolution_notes = st.text_area(
            "resolution_notes",
            height=100,
            placeholder="Required if status is Resolved.",
        )
        submit_manual = st.form_submit_button("Add Incident")

    if submit_manual:
        required_errors = []
        if not manual_ticket_id.strip():
            required_errors.append("ticket_id is required.")
        if not manual_priority.strip():
            required_errors.append("priority is required.")
        if not manual_status.strip():
            required_errors.append("status is required.")
        if not manual_timestamp.strip():
            required_errors.append("timestamp is required.")
        if not manual_assignee.strip():
            required_errors.append("assignee is required.")
        if not manual_description.strip():
            required_errors.append("description is required.")

        # Validate timestamp fields with strict format.
        for label, value, is_required in [
            ("timestamp", manual_timestamp, True),
            ("resolved_at", manual_resolved_at, manual_status == "Resolved"),
        ]:
            if is_required and not value.strip():
                required_errors.append(f"{label} is required when status is Resolved." if label == "resolved_at" else f"{label} is required.")
            if value.strip():
                try:
                    datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    required_errors.append(f"{label} must be in format YYYY-MM-DD HH:MM:SS.")

        if manual_status == "Resolved" and not manual_resolution_notes.strip():
            required_errors.append("resolution_notes is required when status is Resolved.")

        existing_df = st.session_state["tickets_df"]
        if not existing_df.empty and manual_ticket_id.strip() in existing_df["ticket_id"].astype(str).tolist():
            required_errors.append("ticket_id already exists in the queue. Please use a unique value.")

        if required_errors:
            for err in required_errors:
                st.error(err)
        else:
            new_incident = {
                "ticket_id": manual_ticket_id.strip(),
                "priority": manual_priority.strip(),
                "status": manual_status.strip(),
                "timestamp": manual_timestamp.strip(),
                "resolved_at": manual_resolved_at.strip(),
                "assignee": manual_assignee.strip(),
                "description": manual_description.strip(),
                "resolution_notes": manual_resolution_notes.strip(),
            }

            if st.session_state["tickets_df"].empty:
                st.session_state["tickets_df"] = normalize_tickets([new_incident])
            else:
                updated_records = st.session_state["tickets_df"].to_dict(orient="records")
                updated_records.append(new_incident)
                st.session_state["tickets_df"] = normalize_tickets(updated_records)
            st.success(f"Incident {manual_ticket_id.strip()} added to queue.")

df = st.session_state["tickets_df"]
if df.empty:
    st.info("Load mock tickets, upload a file, ingest payload, or generate synthetic data to begin.")
    st.stop()

st.subheader("Raw Ticket Queue")
st.dataframe(df, use_container_width=True)

st.subheader("Priority Distribution")
priority_counts = (
    df.groupby(["priority", "status"]).size().reset_index(name="count").sort_values(["priority", "status"])
)
priority_chart = priority_counts.pivot(index="priority", columns="status", values="count").fillna(0)
st.bar_chart(priority_chart, use_container_width=True)
st.dataframe(priority_counts, use_container_width=True)

st.divider()
st.subheader("AI Summary Workspace")
filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
with filter_col1:
    ticket_filter = st.text_input("Filter by ticket_id", placeholder="INC-100123")
with filter_col2:
    priority_filter = st.multiselect(
        "Filter by priority",
        options=sorted(df["priority"].astype(str).unique().tolist()),
        default=sorted(df["priority"].astype(str).unique().tolist()),
    )
with filter_col3:
    status_filter = st.multiselect(
        "Filter by status",
        options=sorted(df["status"].astype(str).unique().tolist()),
        default=sorted(df["status"].astype(str).unique().tolist()),
    )

filtered_df = df.copy()
if ticket_filter.strip():
    filtered_df = filtered_df[
        filtered_df["ticket_id"].astype(str).str.contains(ticket_filter.strip(), case=False, regex=False)
    ]
if priority_filter:
    filtered_df = filtered_df[filtered_df["priority"].astype(str).isin(priority_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["status"].astype(str).isin(status_filter)]

st.caption(f"Filtered incidents: {len(filtered_df)}")
st.dataframe(filtered_df, use_container_width=True)

if filtered_df.empty:
    st.info("No incidents match current filters. Adjust filters to generate a summary.")
    st.stop()

selected_id = st.selectbox("Select ticket", filtered_df["ticket_id"].tolist())
ticket_row = filtered_df[filtered_df["ticket_id"] == selected_id].iloc[0].to_dict()
st.json(ticket_row)

if st.button("Generate Summary", type="primary"):
    if client is None:
        st.error("API configuration missing. Update .env and retry.")
    else:
        try:
            with st.spinner("Generating summary..."):
                summary = generate_incident_summary(client, model, ticket_row)
            st.session_state["summaries"][selected_id] = summary
        except APIConnectionError as e:
            st.error(
                "Connection failed. Check api_endpoint reachability, VPN/proxy, and SSL trust "
                "for your network. If your org uses private CA, set CA_BUNDLE_PATH in .env. "
                "For temporary local testing only, set VERIFY_SSL=false. "
                f"Details: {e}"
            )
        except AuthenticationError as e:
            st.error(f"Authentication failed. Verify api_key. Details: {e}")
        except APIStatusError as e:
            st.error(
                "API request reached server but failed. Verify model/deployment name and endpoint path. "
                f"Status: {e.status_code}"
            )
        except Exception as e:
            st.error(f"Unexpected error while generating summary: {e}")

if selected_id in st.session_state["summaries"]:
    st.markdown(st.session_state["summaries"][selected_id])

st.divider()
if st.session_state["summaries"]:
    joined = build_stakeholder_update_text(st.session_state["summaries"], df)
    st.download_button(
        label="Export Stakeholder Update (TXT)",
        data=joined,
        file_name="stakeholder_update.txt",
        mime="text/plain",
    )
