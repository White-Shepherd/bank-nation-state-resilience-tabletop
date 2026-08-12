from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from pydantic import ValidationError

from .assessment import (
    BRANCHING_RULES,
    PRIVATE_ROOT,
    STEPS,
    SYNTHETIC_NOTICE,
    archive_assessment,
    board_packet_markdown,
    completeness,
    duplicate_assessment,
    generate_analysis,
    generate_tier0_candidates,
    import_assessment,
    integrity_digest,
    load_assessment,
    new_assessment,
    raci_conflicts,
    responsibility_csv,
    save_assessment,
    tolerance_conflicts,
)
from .assessment_import import TEMPLATE_SPECS, export_template_rows, import_valid_rows, validate_csv
from .assessment_models import Assessment
from .record_editor import render_record_editor
from .reporting import write_pdf


def _dashboard(assessment: Assessment) -> None:
    st.subheader("Assessment dashboard")
    scores = completeness(assessment)
    st.caption("Separate completeness dimensions; no universal cyber-risk score.")
    cols = st.columns(5)
    for col, (name, value) in zip(cols, scores.items()):
        col.metric(name, f"{value}%")
    st.bar_chart(scores, horizontal=True)
    st.info(
        "Decision interpretation: prioritize dimensions with weak evidence or testing before approving tolerances and recovery claims."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Critical services", len(assessment.services))
    c2.metric("Tier 0 candidates", len(assessment.tier0_candidates))
    c3.metric("Supported findings", len(assessment.findings))
    c4.metric("Evidence gaps", len(assessment.evidence_gaps))
    views = st.tabs(
        [
            "Criticality",
            "Conflicts",
            "Dependencies",
            "Concentration",
            "Coverage",
            "Recovery",
            "Ownership",
            "Scenarios",
            "Actions",
        ]
    )
    with views[0]:
        st.dataframe(
            [
                {
                    "Service": s.name,
                    "Designation": s.criticality,
                    "Owner": s.owner,
                    "Rationale": s.rationale,
                }
                for s in assessment.services
            ],
            hide_index=True,
            use_container_width=True,
        )
    with views[1]:
        st.dataframe(
            [{"Review item": x} for x in tolerance_conflicts(assessment)],
            hide_index=True,
            use_container_width=True,
        )
    with views[2]:
        if not assessment.relationships or not assessment.infrastructure:
            st.info(
                "Add explicit relationships and infrastructure dependencies to populate the dependency graph."
            )
            st.dataframe(
                [r.model_dump() for r in assessment.relationships],
                hide_index=True,
                use_container_width=True,
            )
            return
        edge_x = []
        edge_y = []
        for i, _ in enumerate(assessment.relationships):
            edge_x += [0, 1, None]
            edge_y += [i, i, None]
        fig = go.Figure(
            go.Scatter(
                x=edge_x, y=edge_y, mode="lines", line={"color": "#6b7280"}, hoverinfo="skip"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[0] * len(assessment.services),
                y=list(range(len(assessment.services))),
                mode="markers+text",
                text=[s.name for s in assessment.services],
                textposition="middle left",
                marker={"size": 15, "symbol": "square", "color": "#2563eb"},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[1] * len(assessment.services),
                y=list(range(len(assessment.services))),
                mode="markers+text",
                text=[
                    assessment.infrastructure[i % len(assessment.infrastructure)].name
                    for i in range(len(assessment.services))
                ],
                textposition="middle right",
                marker={"size": 15, "symbol": "hexagon", "color": "#f59e0b"},
            )
        )
        fig.update_layout(
            height=600,
            showlegend=False,
            xaxis={"visible": False, "range": [-0.25, 1.25]},
            yaxis={"visible": False},
            margin={"l": 180, "r": 200, "t": 10, "b": 10},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Text alternative: each critical service is linked to a synthetic infrastructure dependency; use the table below for exact evidence."
        )
        st.dataframe(
            [r.model_dump() for r in assessment.relationships],
            hide_index=True,
            use_container_width=True,
        )
    with views[3]:
        st.dataframe(
            [f.model_dump() for f in assessment.findings if "concentration" in f.condition.lower()],
            hide_index=True,
            use_container_width=True,
        )
    with views[4]:
        st.dataframe(
            [
                {
                    "Capability": c.name,
                    "Maturity": c.maturity,
                    "Data source": c.data_source,
                    "Recovery visible": c.available_during_recovery,
                    "Limitation": c.limitation,
                }
                for c in assessment.security_capabilities
            ],
            hide_index=True,
            use_container_width=True,
        )
    with views[5]:
        st.dataframe(
            [
                {
                    "Capability": r.name,
                    "State": r.status,
                    "Last exercise": r.last_exercise,
                    "Proven minutes": r.proven_duration_minutes,
                }
                for r in assessment.recovery_capabilities
            ],
            hide_index=True,
            use_container_width=True,
        )
    with views[6]:
        st.dataframe(
            [{"Issue": x} for x in raci_conflicts(assessment)]
            or [{"Issue": "No structural RACI conflict detected"}],
            hide_index=True,
            use_container_width=True,
        )
    with views[7]:
        st.dataframe(
            [s.model_dump() for s in assessment.scenarios],
            hide_index=True,
            use_container_width=True,
        )
    with views[8]:
        st.dataframe(
            [a.model_dump() for a in assessment.corrective_actions],
            hide_index=True,
            use_container_width=True,
        )


def render_assessment_wizard() -> None:
    st.header("Critical-Service Assessment Wizard")
    st.caption(
        "Local structured assessment | explicit atomic draft saves | human judgment required for final Tier 0 and risk decisions"
    )
    synthetic = Path("data/synthetic_assessments/harbor-ridge-2026.json")
    choices = sorted(PRIVATE_ROOT.glob("*.json")) if PRIVATE_ROOT.exists() else []
    with st.expander("Create blank assessment"), st.form("blank-assessment"):
        blank_id = st.text_input("Assessment ID", value="new-assessment")
        blank_title = st.text_input("Assessment title", value="Critical-Service Assessment")
        blank_org = st.text_input("Organization name", value="Unknown organization")
        if st.form_submit_button("Create assessment"):
            try:
                created = new_assessment(blank_id, blank_title, blank_org)
                save_assessment(created)
                st.session_state.wizard_assessment = created.model_dump(mode="json")
                st.session_state.wizard_unsaved = False
                st.session_state.wizard_last_save = created.updated_at.isoformat()
                st.success("Blank local assessment created and saved.")
                st.rerun()
            except (OSError, ValueError, ValidationError) as exc:
                st.error(f"Assessment could not be created: {exc}")
    source = st.selectbox("Assessment", [synthetic, *choices], format_func=lambda p: p.stem)
    assessment = load_assessment(source)
    source_key = str(source.resolve())
    if st.session_state.get("wizard_source") != source_key:
        st.session_state.wizard_source = source_key
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
        st.session_state.wizard_unsaved = False
        st.session_state.wizard_last_save = assessment.updated_at.isoformat()
    st.session_state.setdefault("wizard_assessment", assessment.model_dump(mode="json"))
    if st.button("Load selected assessment"):
        st.session_state.wizard_source = source_key
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
        st.session_state.wizard_unsaved = False
        st.session_state.wizard_last_save = assessment.updated_at.isoformat()
        st.rerun()
    assessment = Assessment.model_validate(st.session_state.wizard_assessment)
    if assessment.status == "Approved":
        st.info("Read-only approved mode. Duplicate the assessment to create an editable version.")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Save Draft", disabled=assessment.status == "Approved"):
        path = save_assessment(assessment)
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
        st.session_state.wizard_unsaved = False
        st.session_state.wizard_last_save = assessment.updated_at.isoformat()
        st.success(f"Saved version {assessment.version} locally: {path.name}")
    if c2.button("Duplicate"):
        copy = duplicate_assessment(assessment, f"{assessment.id}-copy")
        st.session_state.wizard_assessment = copy.model_dump(mode="json")
        st.rerun()
    if c3.button("Review mode"):
        assessment.status = "Review"
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
    if c4.button("Archive"):
        assessment = archive_assessment(assessment)
        save_assessment(assessment)
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
    last_save = st.session_state.get("wizard_last_save")
    st.caption(f"Last successful save: {last_save or 'Not saved in this session'}")
    if st.session_state.get("wizard_unsaved", False):
        st.warning(
            "This form has unsaved changes. Wizard navigation is disabled until you submit or discard them."
        )
    uploaded = st.file_uploader("Import assessment JSON", type="json")
    if uploaded and st.button("Validate and import"):
        imported = import_assessment(uploaded.getvalue())
        st.session_state.wizard_assessment = imported.model_dump(mode="json")
        st.success("Schema validated and imported.")
    st.progress(
        assessment.current_step / 16,
        text=f"Step {assessment.current_step} of 16 - {STEPS[assessment.current_step - 1]}",
    )
    step = st.selectbox(
        "Go to step",
        range(1, 17),
        index=assessment.current_step - 1,
        format_func=lambda n: f"{n}. {STEPS[n - 1]}",
        disabled=st.session_state.get("wizard_unsaved", False),
        key=f"wizard-step-{assessment.id}-{assessment.current_step}",
    )
    assessment.current_step = step
    with st.expander("Context, definitions, and branching", expanded=True):
        if step == 2:
            st.info(
                "A critical service describes an outcome delivered to customers, markets or the organization. 'Wire transfers' is a service. 'Wire application server' is a supporting asset."
            )
        st.write(BRANCHING_RULES)
        st.caption(
            "Unknown, Evidence unavailable, and Requires review are valid answers and remain visible as evidence gaps."
        )
    collections = {
        2: assessment.services,
        3: assessment.impacts,
        4: assessment.tolerances,
        5: assessment.processes,
        6: assessment.applications + assessment.data_assets,
        7: assessment.infrastructure + assessment.control_planes,
        8: assessment.internal_players,
        9: assessment.third_parties,
        10: assessment.security_capabilities,
        11: assessment.workarounds,
        12: assessment.recovery_capabilities,
        13: assessment.tier0_candidates,
        14: assessment.findings + assessment.evidence_gaps,
        15: assessment.scenarios,
        16: assessment.approvals,
    }
    if step == 1:
        st.json(assessment.organization.model_dump(mode="json"), expanded=True)
    else:
        st.dataframe(
            [x.model_dump(mode="json") for x in collections.get(step, [])],
            hide_index=True,
            use_container_width=True,
        )
    if step in range(2, 13) or step == 16:
        assessment = render_record_editor(assessment, step)
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
    nav1, nav2, _ = st.columns([1, 1, 6])
    navigation_disabled = st.session_state.get("wizard_unsaved", False)
    if nav1.button("Previous", disabled=step == 1 or navigation_disabled):
        assessment.current_step = step - 1
        save_assessment(assessment)
        st.session_state.wizard_last_save = assessment.updated_at.isoformat()
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
        st.rerun()
    if nav2.button("Next", disabled=step == 16 or navigation_disabled):
        assessment.current_step = step + 1
        save_assessment(assessment)
        st.session_state.wizard_last_save = assessment.updated_at.isoformat()
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
        st.rerun()
    assessment.tier0_candidates = generate_tier0_candidates(assessment)
    assessment.findings, assessment.evidence_gaps = generate_analysis(assessment)
    st.session_state.wizard_assessment = assessment.model_dump(mode="json")
    st.divider()
    st.subheader("Template-specific CSV import")
    template = st.selectbox("Assessment template", list(TEMPLATE_SPECS), key="csv-template")
    template_path = Path("templates/assessment") / f"{template}.csv"
    st.download_button(
        "Download selected template", template_path.read_bytes(), template_path.name, "text/csv"
    )
    csv_file = st.file_uploader(
        f"Upload {template_path.name}", type="csv", key=f"upload-{template}"
    )
    if csv_file:
        csv_text = csv_file.getvalue().decode("utf-8-sig")
        valid_rows, invalid_rows = validate_csv(template, csv_text, assessment)
        st.metric("Valid rows", len(valid_rows))
        st.metric("Invalid rows", len({x["row"] for x in invalid_rows}))
        st.caption("Import preview")
        st.dataframe(valid_rows, hide_index=True, use_container_width=True)
        if invalid_rows:
            st.error(
                "Invalid rows will not be imported. Correct each field-level message and upload again."
            )
            st.dataframe(invalid_rows, hide_index=True, use_container_width=True)
        confirm_import = st.checkbox(
            "Confirm import of valid preview rows", key=f"confirm-import-{template}"
        )
        if st.button(
            "Import valid rows",
            disabled=not confirm_import or not valid_rows,
            key=f"import-{template}",
        ):
            before = assessment.model_dump_json()
            try:
                assessment = import_valid_rows(assessment, template, valid_rows, True)
                save_assessment(assessment)
                st.session_state.wizard_assessment = assessment.model_dump(mode="json")
                st.session_state.wizard_last_save = assessment.updated_at.isoformat()
                st.success(
                    f"Imported {len(valid_rows)} valid rows; {len({x['row'] for x in invalid_rows})} invalid rows rejected. Version history preserved."
                )
            except (OSError, ValueError, ValidationError) as exc:
                assessment = Assessment.model_validate_json(before)
                st.error(f"Import rolled back: {exc}")
    staged_export = export_template_rows(assessment, template)
    if staged_export:
        st.download_button(
            "Export imported rows in the same schema", staged_export, template_path.name, "text/csv"
        )
    _dashboard(assessment)
    st.subheader("Export and comparison")
    if assessment.organization.classification in {"Confidential", "Restricted"}:
        st.warning(
            "This assessment contains confidential or restricted content. Confirm authorization before export."
        )
    packet = board_packet_markdown(assessment)
    st.download_button(
        "Export assessment JSON",
        assessment.model_dump_json(indent=2),
        f"{assessment.id}.json",
        "application/json",
    )
    st.download_button(
        "Board packet Markdown", packet, f"{assessment.id}-board-packet.md", "text/markdown"
    )
    st.download_button(
        "Responsibility matrix CSV",
        responsibility_csv(assessment),
        f"{assessment.id}-responsibility.csv",
        "text/csv",
    )
    if st.button("Generate board packet PDF"):
        target = Path("exercise-output") / f"{assessment.id}-board-packet.pdf"
        write_pdf(packet, target)
        st.download_button(
            "Download board packet PDF", target.read_bytes(), target.name, "application/pdf"
        )
    compare = st.file_uploader(
        "Compare with another assessment version", type="json", key="compare"
    )
    if compare:
        other = import_assessment(compare.getvalue())
        st.dataframe(
            [
                {"Measure": "Version", "Current": assessment.version, "Compared": other.version},
                {
                    "Measure": "Services",
                    "Current": len(assessment.services),
                    "Compared": len(other.services),
                },
                {
                    "Measure": "Findings",
                    "Current": len(assessment.findings),
                    "Compared": len(other.findings),
                },
                {
                    "Measure": "Evidence gaps",
                    "Current": len(assessment.evidence_gaps),
                    "Compared": len(other.evidence_gaps),
                },
            ],
            hide_index=True,
        )
    if source.parent == PRIVATE_ROOT:
        st.caption(f"Integrity SHA-256: {integrity_digest(source)}")
        confirm = st.checkbox("I confirm deletion of this local draft")
        if st.button(
            "Delete local draft",
            disabled=not (confirm and assessment.status == "Draft"),
            type="secondary",
        ):
            from .assessment import delete_draft

            delete_draft(source, confirmed=True)
            st.success("Local draft deleted.")
            st.rerun()
    with st.expander("Tabular accessibility fallback"):
        st.caption(
            "All dashboard visuals are represented by the service, relationship, finding, coverage, recovery, and action tables above. Controls are keyboard accessible where Streamlit supports it; browser zoom is supported."
        )
        st.dataframe(
            [s.model_dump(mode="json") for s in assessment.services],
            hide_index=True,
            use_container_width=True,
        )
    st.caption(SYNTHETIC_NOTICE)
