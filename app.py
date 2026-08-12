import csv
import io
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
import streamlit as st

from harbor_resilience import SYNTHETIC_LABEL
from harbor_resilience.assessment_ui import render_assessment_wizard
from harbor_resilience.data import load_services, load_tier0
from harbor_resilience.ecosystem import load_ecosystem, validate_graph
from harbor_resilience.ecosystem_ui import render_ecosystem
from harbor_resilience.engine import assess_tier_zero, impact_status
from harbor_resilience.exercise import PHASES, ROLES
from harbor_resilience.models import Decision
from harbor_resilience.reporting import after_action_markdown, board_markdown, write_pdf

st.set_page_config(page_title="Harbor Ridge Resilience", page_icon="⚓", layout="wide")
st.markdown(
    "<style>.synthetic{background:#7b1f1f;color:white;padding:.55rem;text-align:center;font-weight:700}.stMetric{border:1px solid #d4d8dd;padding:.7rem;border-radius:.4rem}</style>",
    unsafe_allow_html=True,
)
st.markdown(f'<div class="synthetic">{SYNTHETIC_LABEL}</div>', unsafe_allow_html=True)
st.title("Harbor Ridge Bank | Nation-State Resilience Tabletop")
st.caption(
    "Fictional U.S. regional bank | $35B assets | 1.4M customers | 140 branches | defensive exercise"
)

services, candidates = load_services(), load_tier0()
eco_nodes, eco_relationships, eco_responsibilities, eco_indicators, eco_coverage, eco_states = (
    load_ecosystem()
)
validate_graph(eco_nodes, eco_relationships)
defaults = {
    "started": False,
    "phase": 0,
    "decisions": [],
    "questions": [],
    "participants": [],
    "start": None,
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

with st.sidebar:
    st.header("Exercise control")
    if st.button("Start new exercise", type="primary"):
        st.session_state.update(
            started=True,
            phase=0,
            decisions=[],
            questions=[],
            start=datetime.now(timezone.utc).isoformat(),
        )
    st.session_state.participants = st.multiselect(
        "Participants", ROLES, default=st.session_state.participants
    )
    st.progress((st.session_state.phase + 1) / 6, text=f"Phase {st.session_state.phase} of 5")
    if st.button(
        "Advance phase", disabled=not st.session_state.started or st.session_state.phase == 5
    ):
        st.session_state.phase += 1
        st.rerun()

tabs = st.tabs(
    [
        "Exercise",
        "Board dashboard",
        "Resilience Ecosystem Map",
        "Critical-Service Assessment Wizard",
        "Tier 0",
        "Decisions",
        "Reports",
    ]
)
with tabs[0]:
    phase, title, injects = PHASES[st.session_state.phase]
    st.subheader(f"Phase {phase}: {title}")
    reveal = st.slider("Progressive evidence reveal", 1, len(injects), 1)
    for idx, inject in enumerate(injects[:reveal], 1):
        st.info(f"Inject {phase}.{idx} | {inject} | Synthetic evidence")
    st.text_area("Facilitator evidence and observations", key=f"evidence_{phase}")
    question = st.text_input("Unresolved question")
    if st.button("Track question") and question:
        st.session_state.questions.append(question)
with tabs[1]:
    elapsed = st.slider("Synthetic disruption elapsed (minutes)", 0, 1440, 30, 15)
    selected = st.multiselect("Critical services affected", [x.name for x in services])
    rows = []
    for service in services:
        if service.name in selected:
            result = impact_status(elapsed, service)
            rows.append(
                {
                    "Service": service.name,
                    "MTD": service.tolerance.mtd_minutes,
                    "Consumed": f"{result['consumed_pct']}%",
                    "Status": result["rag"],
                }
            )
    st.dataframe(rows, use_container_width=True, hide_index=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tier 0 at risk", sum(1 for x in candidates if x.approved))
    c2.metric("Payment status", "Decision required" if selected else "Within baseline")
    c3.metric("Data integrity", "Uncertain" if phase >= 3 else "No confirmed loss")
    c4.metric("Recovery confidence", "Low" if phase >= 4 else "Unvalidated")
    st.warning(
        "RAG rules: Red = any explicit tolerance breached; Amber = at least 75% of MTD consumed; Green = below 75% with no breach. Customer harm, liquidity, third parties, deadlines, residual risk, management actions, and board decisions require accountable human entry."
    )
with tabs[2]:
    render_ecosystem(
        eco_nodes,
        eco_relationships,
        eco_responsibilities,
        eco_indicators,
        eco_coverage,
        eco_states,
        services,
        st.session_state.decisions,
    )
with tabs[3]:
    render_assessment_wizard()
with tabs[4]:
    st.write(
        "Institution-specific Tier 0 is not a universal regulatory designation and is distinct from NIST CSF Implementation Tiers."
    )
    for candidate in candidates:
        qualified, reasons = assess_tier_zero(candidate)
        with st.expander(
            f"{candidate.name} — {'Approved Tier 0' if candidate.approved else 'Candidate / not approved'}"
        ):
            st.write(
                "Decision-rule result:",
                "; ".join(reasons) if qualified else "No automatic criterion met",
            )
            st.write(
                "Human approval:", candidate.approved, "| Evidence:", ", ".join(candidate.evidence)
            )
with tabs[5]:
    with st.form("decision"):
        decision = st.selectbox(
            "Decision required",
            [
                "Raise threat posture",
                "Declare a material cyber incident",
                "Invoke crisis management",
                "Freeze privileged changes",
                "Isolate identity infrastructure",
                "Suspend selected payment channels",
                "Activate manual processing",
                "Fail over to recovery systems",
                "Disconnect a third party",
                "Notify regulators (counsel/compliance determine jurisdiction-specific timing)",
                "Contact CISA, FBI and FS-ISAC",
                "Communicate with customers",
                "Restore from a selected recovery point",
                "Accept temporary reduced service",
            ],
        )
        owner = st.selectbox("Decision owner", ROLES)
        action = st.text_area("Chosen action")
        assumptions = st.text_area("Assumptions / unknowns / evidence needed")
        dissent = st.text_area("Dissent")
        residual = st.text_area("Residual risk accepted")
        if st.form_submit_button("Record decision") and action and residual:
            st.session_state.decisions.append(
                Decision(
                    phase=phase,
                    decision=decision,
                    owner=owner,
                    chosen_action=action,
                    assumptions=assumptions,
                    dissent=dissent,
                    residual_risk=residual,
                )
            )
    st.dataframe([x.model_dump() for x in st.session_state.decisions], use_container_width=True)
    decision_output = io.StringIO()
    decision_writer = csv.DictWriter(
        decision_output,
        fieldnames=[
            "synthetic_label",
            "phase",
            "decision",
            "owner",
            "chosen_action",
            "assumptions",
            "dissent",
            "residual_risk",
        ],
    )
    decision_writer.writeheader()
    for item in st.session_state.decisions:
        decision_writer.writerow({"synthetic_label": SYNTHETIC_LABEL, **item.model_dump()})
    st.download_button(
        "Export decision log CSV",
        decision_output.getvalue(),
        "synthetic-exercise-decisions.csv",
        "text/csv",
    )
with tabs[6]:
    board = board_markdown(services, candidates, st.session_state.decisions)
    aar = after_action_markdown(st.session_state.participants, st.session_state.decisions)
    st.download_button("Download board packet (Markdown)", board, "board-packet.md")
    st.download_button("Download after-action report", aar, "after-action-report.md")
    if st.button("Generate board PDF"):
        target = Path("exercise-output/board-packet.pdf")
        write_pdf(board, target)
        st.download_button(
            "Download board packet (PDF)", target.read_bytes(), target.name, "application/pdf"
        )
    st.caption(
        "Reports preserve empty findings until exercise evidence is entered; scoring and conclusions remain reviewable."
    )
