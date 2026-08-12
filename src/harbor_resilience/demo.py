from __future__ import annotations

from pathlib import Path

import streamlit as st

from . import SYNTHETIC_LABEL
from .assessment import (
    board_packet_markdown,
    generate_analysis,
    generate_tier0_candidates,
    load_assessment,
)
from .ecosystem import filter_graph, graph_figure

DEMO_ASSESSMENT = Path("data/synthetic_assessments/harbor-ridge-2026.json")
CHECKPOINTS = [
    "Overview",
    "Critical service",
    "Impact tolerance",
    "Dependency map",
    "Tier 0",
    "Concentration finding",
    "Scenario warning",
    "Integrity dilemma",
    "Recovery",
    "Board packet",
]


def reset_demo_state() -> None:
    st.session_state.demo_checkpoint = 0
    st.session_state.demo_checkpoint_selector = 0
    st.session_state.demo_decision = "Pending presenter selection"


def demo_snapshot() -> dict:
    assessment = load_assessment(DEMO_ASSESSMENT)
    candidates = generate_tier0_candidates(assessment)
    findings, gaps = generate_analysis(assessment)
    return {"assessment": assessment, "candidates": candidates, "findings": findings, "gaps": gaps}


def _wire_service(assessment):
    return next(
        (service for service in assessment.services if "wire" in service.name.lower()),
        assessment.services[0],
    )


def _checkpoint_navigation() -> int:
    st.session_state.setdefault("demo_checkpoint", 0)
    st.session_state.setdefault("demo_decision", "Pending presenter selection")
    left, middle, right = st.columns([1, 1, 2])
    if left.button("Reset demo", use_container_width=True):
        reset_demo_state()
        st.rerun()
    if middle.button(
        "Next checkpoint",
        disabled=st.session_state.demo_checkpoint >= len(CHECKPOINTS) - 1,
        use_container_width=True,
    ):
        st.session_state.demo_checkpoint = min(
            st.session_state.demo_checkpoint + 1, len(CHECKPOINTS) - 1
        )
        st.session_state.pop("demo_checkpoint_selector", None)
        st.rerun()
    right.progress(
        (st.session_state.demo_checkpoint + 1) / len(CHECKPOINTS),
        text=f"Checkpoint {st.session_state.demo_checkpoint + 1} of 10",
    )
    selected = st.selectbox(
        "Presenter checkpoint",
        range(len(CHECKPOINTS)),
        index=st.session_state.demo_checkpoint,
        format_func=lambda index: f"{index + 1}. {CHECKPOINTS[index]}",
        key="demo_checkpoint_selector",
    )
    if selected != st.session_state.demo_checkpoint:
        st.session_state.demo_checkpoint = selected
    return selected


def render_demo_mode(nodes, relationships, indicators, states) -> None:
    st.header("Continuum Resilience | Presenter Demo Mode")
    st.success(f"READ-ONLY DEMONSTRATION • {SYNTHETIC_LABEL}")
    st.caption(
        "Canonical synthetic data only. Private assessments, local paths, developer controls, and persistence actions are unavailable in this mode."
    )
    checkpoint = _checkpoint_navigation()
    snapshot = demo_snapshot()
    assessment = snapshot["assessment"]
    service = _wire_service(assessment)
    tolerance = next(
        (item for item in assessment.tolerances if item.service_id == service.id), None
    )
    st.subheader(f"{checkpoint + 1}. {CHECKPOINTS[checkpoint]}")
    if checkpoint == 0:
        st.markdown(
            "**Business outcome:** connect critical services to technical concentration, exercise leadership decisions, and produce evidence-linked board actions."
        )
        cols = st.columns(4)
        cols[0].metric("Critical services", len(assessment.services))
        cols[1].metric("Declared relationships", len(assessment.relationships))
        cols[2].metric("Tier 0 candidates", len(snapshot["candidates"]))
        cols[3].metric("Evidence gaps", len(snapshot["gaps"]))
    elif checkpoint == 1:
        st.markdown(f"### {service.name}")
        st.write(service.description)
        st.dataframe(
            [
                {
                    "Business owner": service.owner,
                    "Technical owner": service.technical_owner,
                    "Operating hours": service.operating_hours,
                    "Criticality": service.criticality,
                    "Minimum alternative": service.manual_alternative,
                }
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.info(f"Why it matters: {service.rationale}")
    elif checkpoint == 2 and tolerance:
        cols = st.columns(4)
        cols[0].metric("Maximum tolerable disruption", f"{tolerance.mtd_minutes} min")
        cols[1].metric("Recovery time objective", f"{tolerance.rto_minutes} min")
        cols[2].metric("Recovery point objective", f"{tolerance.rpo_minutes} min")
        cols[3].metric("Manual continuity", f"{tolerance.manual_workaround_minutes} min")
        st.write("**Minimum viable service:**", tolerance.minimum_viable_service)
        st.caption(
            "Targets are synthetic management inputs. Approval and testing are displayed separately because a documented target is not proof of recoverability."
        )
    elif checkpoint == 3:
        service_node = next((n.id for n in nodes if "wire transfer" in n.name.lower()), None)
        selected_nodes, selected_relationships = filter_graph(
            nodes, relationships, service=service_node
        )
        st.plotly_chart(
            graph_figure(selected_nodes, selected_relationships), use_container_width=True
        )
        st.caption(
            "Deterministic dependency view. Only explicitly declared relationships are shown; the application does not infer undeclared failure paths."
        )
    elif checkpoint == 4:
        st.dataframe(
            [
                {
                    "Dependency": item.dependency_id,
                    "Services": len(item.service_ids),
                    "Rules triggered": "; ".join(item.triggered_rules),
                    "Evidence gaps": "; ".join(item.missing_evidence) or "None recorded",
                    "Human decision": item.reviewer_decision,
                }
                for item in snapshot["candidates"]
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.warning(
            "Candidate generation is explainable decision support; classification requires human approval."
        )
    elif checkpoint == 5:
        concentration = [f for f in snapshot["findings"] if "concentration" in f.condition.lower()]
        st.dataframe(
            [
                {
                    "Finding": item.condition,
                    "Services": ", ".join(item.service_ids),
                    "Evidence": ", ".join(item.evidence),
                    "Recommendation": item.recommendation,
                    "Residual uncertainty": item.residual_uncertainty,
                }
                for item in concentration
            ],
            hide_index=True,
            use_container_width=True,
        )
    elif checkpoint == 6:
        warning_states = [item for item in states if item.phase == 2]
        st.warning("AMBIGUOUS PRE-POSITIONING • attribution is not established")
        st.dataframe(
            [
                {
                    "Observed node": item.node_id,
                    "Status": item.status,
                    "Warning indicators": ", ".join(item.indicator_ids),
                    "Decision": item.decision,
                    "Deadline": f"{item.deadline_minutes} minutes",
                }
                for item in warning_states
            ],
            hide_index=True,
            use_container_width=True,
        )
    elif checkpoint == 7:
        dilemma = [item for item in states if item.phase == 5]
        st.error("DECISION • contain production identity without destroying recovery options")
        st.dataframe(
            [
                {
                    "Affected node": item.node_id,
                    "State": item.status,
                    "Required decision": item.decision,
                    "Deadline": f"{item.deadline_minutes} minutes",
                    "Prerequisite": item.recovery_prerequisite or "Not declared",
                }
                for item in dilemma
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.session_state.demo_decision = st.radio(
            "Presenter decision record (session-only; canonical data is unchanged)",
            [
                "Pending presenter selection",
                "Isolate production identity and preserve independent recovery access",
                "Delay isolation pending additional integrity evidence",
            ],
        )
    elif checkpoint == 8:
        recovery = [item for item in states if item.phase == 6]
        st.success("RECOVERY • validate trust before restoring throughput")
        st.dataframe(
            [
                {
                    "Node": item.node_id,
                    "State": item.status,
                    "Action": item.decision,
                    "Recovery prerequisite": item.recovery_prerequisite,
                }
                for item in recovery
            ],
            hide_index=True,
            use_container_width=True,
        )
        st.info("Recorded demonstration decision: " + st.session_state.demo_decision)
    else:
        packet = board_packet_markdown(assessment)
        cols = st.columns(3)
        cols[0].metric("Evidence-backed findings", len(snapshot["findings"]))
        cols[1].metric("Open evidence gaps", len(snapshot["gaps"]))
        cols[2].metric("Corrective actions", len(assessment.corrective_actions))
        with st.expander("Board packet preview", expanded=True):
            st.markdown(packet[:6000])
        st.download_button(
            "Download synthetic board packet",
            packet,
            "continuum-resilience-synthetic-board-packet.md",
            "text/markdown",
        )
        st.caption(
            "The packet reports synthetic evidence and residual uncertainty; it does not claim customer results, avoided losses, or control effectiveness."
        )
    st.divider()
    st.caption(
        "Presenter transition: pause, restate what changed and why it matters, then advance. All values and entities shown are fictional and synthetic."
    )
