from __future__ import annotations

import streamlit as st

from .ecosystem import (
    LAYER_ORDER,
    VIEW_LAYERS,
    concentration,
    dependency_cycles,
    filter_graph,
    graph_figure,
    indicators_csv,
    responsibility_csv,
    scenario_json,
    service_report,
)

PHASES = ["Normal operations", "Strategic warning", "Ambiguous pre-positioning", "Coordinated disruption", "Integrity uncertainty", "Containment dilemma", "Recovery", "Post-incident stabilization"]
INVESTMENTS = {
    "Phishing-resistant administrative MFA": (["CBS-01", "CBS-03", "CBS-05", "CBS-16"], ["IF-01", "IF-03"], "Reduces credential-based administrative takeover; session and endpoint risk remains."),
    "Privileged workstations": (["CBS-03", "CBS-05", "CBS-12", "CBS-16"], ["IF-03", "IF-07", "IF-08"], "Reduces administrative endpoint exposure; does not remove control-plane concentration."),
    "Separate administrative identities": (["CBS-03", "CBS-05", "CBS-16"], ["IF-01", "IF-03"], "Separates routine and privileged use; identity provider compromise remains possible."),
    "Independent recovery identity": (["CBS-03", "CBS-04", "CBS-05", "CBS-12", "CBS-16"], ["IF-17", "IF-18", "IF-19"], "Breaks the production-identity recovery common mode; requires tested custody and access."),
    "Network-management segmentation": (["CBS-01", "CBS-04", "CBS-05", "CBS-16"], ["IF-07"], "Limits management-plane reach; emergency access paths remain."),
    "Immutable backups": (["CBS-03", "CBS-12", "CBS-16"], ["IF-17"], "Reduces deletion risk; does not prove financial integrity."),
    "Offline recovery data": (["CBS-03", "CBS-05", "CBS-12", "CBS-16"], ["AD-14", "AD-16", "IF-17"], "Creates an independent reference; freshness and reconciliation remain constrained."),
    "Clean-room recovery": (["CBS-03", "CBS-04", "CBS-05", "CBS-12", "CBS-16"], ["IF-19"], "Reduces production control-plane dependence; minimum viable capacity and data validation remain."),
    "Additional telecommunications provider": (["CBS-01", "CBS-04", "CBS-05", "CBS-06", "CBS-08", "CBS-14"], ["IF-13"], "Reduces carrier concentration if routes and facilities are genuinely diverse."),
    "Independent DNS": (["CBS-01", "CBS-14", "CBS-16"], ["IF-04", "IF-18"], "Supports recovery when production DNS is unavailable; configuration drift must be tested."),
    "Transaction-integrity validation": (["CBS-03", "CBS-04", "CBS-05", "CBS-07", "CBS-11", "CBS-12"], ["AD-14", "AD-16"], "Improves restoration confidence; authoritative sources can still conflict."),
    "Improved Tier 0 telemetry": (["CBS-01", "CBS-03", "CBS-05", "CBS-15", "CBS-16"], ["IF-01", "IF-03", "IF-07", "IF-17"], "Improves decision evidence; shared collection dependencies may remain."),
    "Third-party substitution capability": (["CBS-03", "CBS-04", "CBS-05", "CBS-06"], ["EP-01", "EP-02", "EP-04"], "Reduces provider concentration; switching time and correlated sector risk remain."),
    "Manual payment procedures": (["CBS-04", "CBS-05", "CBS-09"], ["BP-10"], "Maintains bounded service; capacity, fraud, reconciliation, and liquidity limits remain."),
}


def _status_marker(status):
    return {"failed": "[FAILED]", "degraded": "[DEGRADED]", "restored": "[RESTORED]", "warning": "[WARNING]", "unknown": "[UNKNOWN]"}.get(status, "[NORMAL]")


def render_ecosystem(nodes, relationships, responsibilities, indicators, coverage, states, services, decisions):
    def reset_view():
        st.session_state.update(ecosystem_phase=0, eco_view="Board view", eco_query="", eco_layers=sorted(VIEW_LAYERS["Board view"]), eco_service="", eco_owner="", eco_node_types=[], eco_tier="All", eco_state="All", eco_critical=False, eco_contrast=False, eco_highlights=[])

    def sync_view_layers():
        st.session_state.eco_layers = sorted(VIEW_LAYERS[st.session_state.eco_view])

    st.header("Resilience Ecosystem Map")
    st.caption("Deterministic, synthetic dependency model. Color is paired with shape, label, border weight, and text status. No undeclared dependency is propagated.")
    phase = st.select_slider("Scenario time", options=list(range(8)), format_func=lambda x: PHASES[x], key="ecosystem_phase")
    current_states = [x for x in states if x.phase == phase]
    statuses = {x.node_id: x.status for x in current_states}
    tabs = st.tabs(["Network map", "Critical-service explorer", "Responsibility map", "Warning indicators", "Tool coverage", "Failure and concentration", "Board decisions", "Investment view", "Tabular fallback"])

    with tabs[0]:
        view = st.radio("Progressive view", list(VIEW_LAYERS), horizontal=True, key="eco_view", on_change=sync_view_layers)
        c1, c2, c3, c4 = st.columns(4)
        query = c1.text_input("Search node", key="eco_query")
        layer_filter = c2.multiselect("Layer", LAYER_ORDER, default=sorted(VIEW_LAYERS[view]), key="eco_layers")
        service_options = [n for n in nodes if n.layer == "critical_service"]
        service = c3.selectbox("Critical service", [""] + [n.id for n in service_options], format_func=lambda x: "All" if not x else next(n.name for n in service_options if n.id == x), key="eco_service")
        owner = c4.selectbox("Owner", [""] + sorted({n.owner for n in nodes}), format_func=lambda x: x or "All", key="eco_owner")
        node_types = st.multiselect("Node type", sorted({n.node_type for n in nodes}), placeholder="All node types", key="eco_node_types")
        c5, c6, c7, c8 = st.columns(4)
        tier_filter = c5.selectbox("Tier 0", ["All", "Tier 0", "Not Tier 0"], key="eco_tier")
        state_filter = c6.selectbox("Operational state", ["All", "normal", "warning", "degraded", "failed", "unknown", "restored"], key="eco_state")
        critical_only = c7.checkbox("Hide noncritical relationships", key="eco_critical")
        high_contrast = c8.checkbox("High-contrast mode", key="eco_contrast")
        highlights = st.multiselect("Highlights", ["Single points of failure", "Shared dependencies", "Third-party concentration", "Missing monitoring", "Missing owners", "Recovery dependencies"], key="eco_highlights")
        st.button("Reset view", key="reset_graph", on_click=reset_view)
        tier = None if tier_filter == "All" else tier_filter == "Tier 0"
        visible, edges = filter_graph(nodes, relationships, layers=set(layer_filter), owner=owner or None, tier0=tier, service=service or None, critical_only=critical_only)
        if view == "Board view" and not service:
            principal = {"IP-01", "IP-02", "IP-03", "IP-07", "EP-01", "EP-02", "EP-04"}
            visible = [n for n in visible if n.layer == "critical_service" or n.tier0 or n.id in principal]
            ids = {n.id for n in visible}; edges = [r for r in edges if r.source in ids and r.destination in ids]
        if query: visible = [n for n in visible if query.lower() in (n.name + n.id + n.node_type).lower()]
        if node_types: visible = [n for n in visible if n.node_type in node_types]
        if state_filter != "All": visible = [n for n in visible if statuses.get(n.id, "normal") == state_filter]
        if "Single points of failure" in highlights: visible = [n for n in visible if n.single_point]
        if "Shared dependencies" in highlights:
            shared = set(concentration(nodes, relationships)); visible = [n for n in visible if n.id in shared]
        if "Third-party concentration" in highlights: visible = [n for n in visible if n.third_party and len(n.critical_services) > 1]
        if "Missing monitoring" in highlights:
            covered = {x.target_id for x in coverage}; visible = [n for n in visible if n.tier0 and n.id not in covered]
        if "Missing owners" in highlights: visible = [n for n in visible if not n.owner]
        if "Recovery dependencies" in highlights: visible = [n for n in visible if n.recovery_capability or "recovery" in n.node_type]
        ids = {n.id for n in visible}; edges = [r for r in edges if r.source in ids and r.destination in ids]
        if not visible: st.warning("No nodes match the current filters.")
        else:
            fig = graph_figure(visible, edges, statuses, high_contrast)
            event = st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True, "toImageButtonOptions": {"format": "png", "filename": "synthetic-resilience-map"}}, on_select="rerun", selection_mode="points", key="ecosystem_graph")
            chosen = None
            if event and event.selection and event.selection.points: chosen = event.selection.points[0].get("customdata")
            selected_id = st.selectbox("Selected node detail", [n.id for n in visible], index=next((i for i, n in enumerate(visible) if n.id == chosen), 0), format_func=lambda x: next(n.name for n in visible if n.id == x))
            node = next(n for n in visible if n.id == selected_id)
            incoming = [r.source for r in relationships if r.destination == node.id]; downstream = [r.source for r in relationships if r.destination == node.id and r.source.startswith("CBS-")]
            related_indicators = [x.signal for x in indicators if x.tier0_dependency == node.id or x.critical_service == node.id]
            related_decisions = [x.decision for x in decisions if any(s in node.critical_services for s in [f"CBS-{i:02}" for i in range(1, 17)])]
            st.markdown(f"**{_status_marker(statuses.get(node.id, 'normal'))} {node.name}** — {node.node_type}; owner: {node.owner}; operator: {node.operator}; authority: {node.decision_authority}")
            st.write({"description": node.description, "business_purpose": node.name, "critical_services": node.critical_services, "tier0": node.tier0, "tier0_rationale": node.tier0_rationale, "dependencies": incoming, "downstream_services": downstream, "security_capabilities": node.monitoring, "warning_indicators": related_indicators or node.warning_indicators, "impact_tolerance": "See selected critical-service tolerance", "recovery_objective": node.recovery_objective, "recovery_method": node.recovery_method, "controls": node.controls, "known_limitations": node.limitations, "scenario_status": statuses.get(node.id, "normal"), "related_exercise_decisions": related_decisions})
            html = fig.to_html(include_plotlyjs="cdn", full_html=True)
            st.download_button("Export interactive HTML", html, "synthetic-resilience-map.html", "text/html")
            st.download_button("Export current scenario JSON", scenario_json(phase, states, decisions), "synthetic-scenario-state.json", "application/json")
            st.download_button("Export selected service Markdown", service_report(node, nodes, relationships), "synthetic-dependency-report.md")
            try:
                st.download_button("Export SVG", fig.to_image(format="svg"), "synthetic-resilience-map.svg", "image/svg+xml")
                st.download_button("Export PNG", fig.to_image(format="png", width=1600, height=900, scale=1), "synthetic-resilience-map.png", "image/png")
            except (RuntimeError, ValueError) as exc:
                st.info(f"Static export requires a compatible local Chrome installation: {exc}")
        if current_states:
            st.subheader("Phase evidence and deadlines")
            st.dataframe([{"Node": x.node_id, "Status": _status_marker(x.status), "Indicators": ", ".join(x.indicator_ids), "Pending decision": x.decision, "Deadline minutes": x.deadline_minutes, "Recovery prerequisite": x.recovery_prerequisite} for x in current_states], hide_index=True, use_container_width=True)

    with tabs[1]:
        selected_service = st.selectbox("Explore critical service", [n.id for n in service_options], format_func=lambda x: next(n.name for n in service_options if n.id == x), key="service_explorer")
        service_node = next(n for n in service_options if n.id == selected_service)
        layers = [("Customer / market need", ["Safe, timely access to banking"]), ("Critical banking service", [service_node.name])]
        for layer, title in [("business_process", "Business processes"), ("application_data", "Applications and authoritative data"), ("infrastructure", "Infrastructure and control planes")]:
            layers.append((title, [n.name for n in nodes if n.layer == layer and selected_service in n.critical_services]))
        service_targets = {n.id for n in nodes if selected_service in n.critical_services}
        security_ids = {r.source for r in relationships if r.relationship_type in {"monitors", "protects", "validates"} and r.destination in service_targets}
        layers.append(("Security monitoring and protection", [n.name for n in nodes if n.id in security_ids]))
        layers.append(("Recovery capabilities", [n.name for n in nodes if n.recovery_capability and selected_service in n.critical_services]))
        for index, (title, values) in enumerate(layers):
            st.markdown(f"**{title}**")
            st.write(" • ".join(values) if values else "No declared nodes in this layer")
            if index < len(layers) - 1: st.markdown("↓")
        model_service = next(x for x in services if x.id == selected_service)
        t = model_service.tolerance
        st.dataframe([{"Business owner": model_service.owner, "Technical owner": service_node.operator, "Incident decision owner": service_node.decision_authority, "MTD minutes": t.mtd_minutes, "Minimum viable service": f"{t.minimum_service_pct}%", "RTO minutes": t.rto_minutes, "RPO minutes": t.rpo_minutes, "Data-integrity tolerance": f"{t.max_data_uncertainty_minutes} minutes uncertainty", "Manual workaround": f"{t.manual_workaround_minutes} minutes", "Third parties": ", ".join(n.name for n in nodes if n.third_party and selected_service in n.critical_services), "Warning indicators": ", ".join(x.signal for x in indicators if x.critical_service == selected_service), "Current state": statuses.get(selected_service, "normal")}], hide_index=True, use_container_width=True)

    with tabs[2]:
        rows = []
        for x in responsibilities:
            flags = []
            if len(x.accountable) == 0: flags.append("NO ACCOUNTABLE")
            if len(x.accountable) > 1: flags.append("CONFLICTING ACCOUNTABLE")
            if not x.alternate: flags.append("MISSING ALTERNATE")
            if x.technical_action and not x.business_approval: flags.append("TECHNICAL ACTION WITHOUT BUSINESS APPROVAL")
            rows.append({"Activity": x.activity, "R": ", ".join(x.responsible), "A": ", ".join(x.accountable), "C": ", ".join(x.consulted), "I": ", ".join(x.informed), "Deadline": x.deadline_minutes, "Escalation": x.escalation_authority, "Alternate": x.alternate, "Flags": "; ".join(flags) or "None"})
        unavailable = st.multiselect("Decision owners unavailable", sorted({x for r in responsibilities for x in r.accountable}))
        for row in rows:
            if any(x in unavailable for x in row["A"].split(", ")): row["Flags"] = (row["Flags"] + "; DECISION OWNER UNAVAILABLE").strip("; ")
        st.dataframe(rows, hide_index=True, use_container_width=True)
        st.download_button("Export responsibility matrix CSV", responsibility_csv(responsibilities), "synthetic-responsibility-matrix.csv", "text/csv")

    with tabs[3]:
        categories = st.multiselect("Signal category", sorted({x.category for x in indicators}), default=sorted({x.category for x in indicators}))
        shown = [x for x in indicators if x.category in categories]
        st.dataframe([x.model_dump() for x in shown], hide_index=True, use_container_width=True)
        st.warning("Weak signals remain weak signals and are not confirmed nation-state activity.")
        st.download_button("Export warning-indicator CSV", indicators_csv(shown), "synthetic-warning-indicators.csv", "text/csv")

    with tabs[4]:
        st.write("Maturity is a sequence: deployed → configured → telemetry received → detection tested → response integrated → recovery visibility validated. Owning a tool does not guarantee coverage.")
        st.dataframe([x.model_dump() for x in coverage], hide_index=True, use_container_width=True)
        covered = {x.target_id for x in coverage}; missing = [n for n in nodes if n.tier0 and n.id not in covered]
        st.error("Tier 0 without declared coverage: " + ", ".join(n.name for n in missing))

    with tabs[5]:
        st.subheader("Single points and shared dependencies")
        conc = concentration(nodes, relationships)
        st.dataframe([{"Dependency": next(n.name for n in nodes if n.id == node_id), "Critical relationships": count, "Single point": next(n.single_point for n in nodes if n.id == node_id), "Third party": next(n.third_party for n in nodes if n.id == node_id)} for node_id, count in sorted(conc.items(), key=lambda x: -x[1])], hide_index=True, use_container_width=True)
        st.subheader("Detected dependency cycles")
        st.write(dependency_cycles(nodes, relationships))
        st.subheader("Recovery paradoxes")
        from .ecosystem import _load
        st.dataframe(_load("recovery_dependencies.yaml")["paradoxes"], hide_index=True, use_container_width=True)

    with tabs[6]:
        board_nodes = [n for n in nodes if n.layer == "critical_service" or n.tier0 or (n.third_party and len(n.critical_services) > 2)]
        st.metric("Board items", len(board_nodes), help="Limited to services, Tier 0 concentrations, and major outside concentrations")
        selected_service_names = [next(n.name for n in nodes if n.id == x.node_id) for x in current_states if x.node_id.startswith("CBS-")]
        st.write({"Critical services": selected_service_names or "No phase-specific impairment", "Customer harm": "Review affected-service thresholds", "Payments and settlement": statuses.get("CBS-05", "normal"), "Liquidity consequence": statuses.get("CBS-11", "normal"), "Data-integrity confidence": "Low" if phase in {4, 5} else "Unvalidated", "Recovery confidence": "Improving" if phase >= 6 else "Unvalidated", "Third-party concentration": [n.name for n in board_nodes if n.third_party], "Decisions awaiting approval": [x.decision for x in current_states if x.decision], "Investment priorities": ["Independent recovery identity", "Transaction-integrity validation", "Third-party substitution"]})
        evidence = [r for r in relationships if r.source in {n.id for n in board_nodes} or r.destination in {n.id for n in board_nodes}]
        st.dataframe([{"Evidence": r.id, "Source": r.source, "Type": r.relationship_type, "Destination": r.destination, "Rationale": r.evidence} for r in evidence[:50]], hide_index=True, use_container_width=True)

    with tabs[7]:
        chosen = st.multiselect("Proposed resilience improvements", list(INVESTMENTS))
        for item in chosen:
            services_benefit, protected, residual = INVESTMENTS[item]
            st.markdown(f"**{item}**")
            st.write({"Services benefit": services_benefit, "Tier 0 or recovery dependencies protected": protected, "Failure paths reduced": "Declared paths touching protected dependencies", "Warning signals improve": "Coverage and confidence improve where telemetry is independent", "Recovery dependencies improve": any(x in {"IF-17", "IF-18", "IF-19"} for x in protected), "Residual risk": residual})
        st.caption("Qualitative bounded assumptions only; selections do not calculate false precision or approve investment.")

    with tabs[8]:
        st.write("Screen-reader and no-graphics fallback for the current phase.")
        st.dataframe([{"ID": n.id, "Name": n.name, "Layer": n.layer, "Type": n.node_type, "Owner": n.owner, "Tier 0": n.tier0, "Status": statuses.get(n.id, "normal"), "Text alternative": n.accessibility_label} for n in nodes], hide_index=True, use_container_width=True)
        st.dataframe([r.model_dump() for r in relationships], hide_index=True, use_container_width=True)
