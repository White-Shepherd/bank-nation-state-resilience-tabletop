from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict

import plotly.graph_objects as go
import yaml

from . import SYNTHETIC_LABEL
from .data import ROOT
from .models import (
    EcosystemNode,
    EcosystemRelationship,
    Responsibility,
    ScenarioNodeState,
    ToolCoverage,
    WarningIndicator,
)

LAYER_ORDER = ["critical_service", "business_process", "application_data", "infrastructure", "security", "internal_player", "external_player"]
LAYER_COLORS = {"critical_service": "#2563EB", "business_process": "#0F766E", "application_data": "#7C3AED", "infrastructure": "#B45309", "security": "#047857", "internal_player": "#475569", "external_player": "#9333EA"}
SYMBOLS = {"critical_service": "square", "business_process": "square", "application_data": "square", "infrastructure": "hexagon", "security": "diamond", "internal_player": "circle", "external_player": "circle-open"}
VIEW_LAYERS = {
    "Board view": {"critical_service", "infrastructure", "internal_player", "external_player"},
    "Risk view": set(LAYER_ORDER),
    "Technical view": {"critical_service", "business_process", "application_data", "infrastructure", "security"},
    "Incident-command view": {"critical_service", "security", "internal_player", "external_player"},
    "Recovery view": {"critical_service", "application_data", "infrastructure", "internal_player", "external_player"},
}


def _load(name: str):
    with (ROOT / "data" / "ecosystem" / name).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_ecosystem():
    nodes = [EcosystemNode.model_validate(x) for x in _load("nodes.yaml")["nodes"]]
    relationships = [EcosystemRelationship.model_validate(x) for x in _load("relationships.yaml")["relationships"]]
    responsibilities = [Responsibility.model_validate(x) for x in _load("responsibilities.yaml")["activities"]]
    indicators = [WarningIndicator.model_validate(x) for x in _load("warning_indicators.yaml")["indicators"]]
    coverage = [ToolCoverage.model_validate(x) for x in _load("tool_coverage.yaml")["coverage"]]
    states = [ScenarioNodeState.model_validate(x) for x in _load("scenario_states.yaml")["states"]]
    return nodes, relationships, responsibilities, indicators, coverage, states


def validate_graph(nodes, relationships):
    ids = [n.id for n in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate node identifiers")
    known = set(ids)
    invalid = [(r.id, r.source, r.destination) for r in relationships if r.source not in known or r.destination not in known]
    if invalid:
        raise ValueError(f"invalid relationship endpoints: {invalid}")


def dependency_cycles(nodes, relationships):
    graph = defaultdict(list)
    for r in relationships:
        if r.relationship_type in {"depends_on", "fails_over_to"}:
            graph[r.source].append(r.destination)
    cycles = set()
    def visit(node, path):
        if node in path:
            cycle = path[path.index(node):] + [node]
            cycles.add(tuple(cycle))
            return
        if len(path) > len(nodes):
            raise ValueError("unbounded propagation")
        for target in graph[node]: visit(target, path + [node])
    for node in list(graph): visit(node, [])
    return sorted(cycles)


def propagate(explicit_failed: set[str], nodes, relationships):
    affected = set(explicit_failed); explanations = []
    for r in relationships:
        if r.propagation and r.destination in affected and r.source not in affected:
            affected.add(r.source)
            explanations.append({"trigger": r.trigger, "dependency": r.destination, "effect": r.effect, "confidence": r.confidence, "assumptions": r.assumptions, "compensating_control": r.compensating_control})
    return affected, explanations


def filter_graph(nodes, relationships, *, layers=None, owner=None, tier0=None, service=None, critical_only=False):
    selected = [n for n in nodes if (not layers or n.layer in layers) and (not owner or n.owner == owner) and (tier0 is None or n.tier0 == tier0) and (not service or n.id == service or service in n.critical_services)]
    ids = {n.id for n in selected}
    edges = [r for r in relationships if r.source in ids and r.destination in ids and (not critical_only or r.criticality == "critical")]
    return selected, edges


def deterministic_positions(nodes):
    groups = defaultdict(list)
    for node in nodes: groups[node.layer].append(node)
    positions = {}
    for x, layer in enumerate(LAYER_ORDER):
        ordered = sorted(groups[layer], key=lambda n: n.id)
        offset = (len(ordered) - 1) / 2
        for index, node in enumerate(ordered): positions[node.id] = (x * 2.4, (offset - index) * 1.1)
    return positions


def graph_figure(nodes, relationships, statuses=None, high_contrast=False):
    statuses = statuses or {}; pos = deterministic_positions(nodes); fig = go.Figure()
    right_edge = max((value[0] for value in pos.values()), default=0)
    line_styles = {"supports": "solid", "depends_on": "dash", "monitors": "dot", "owns": "solid", "recovers": "dashdot", "escalates_to": "dot"}
    for rel in relationships:
        x0, y0 = pos[rel.source]; x1, y1 = pos[rel.destination]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line={"color": "#64748B", "width": 1.5, "dash": line_styles.get(rel.relationship_type, "solid")}, hoverinfo="text", text=rel.description, showlegend=False))
    for layer in LAYER_ORDER:
        group = [n for n in nodes if n.layer == layer]
        if not group: continue
        colors = ["#7F1D1D" if statuses.get(n.id) == "failed" else "#D97706" if statuses.get(n.id) == "degraded" else "#15803D" if statuses.get(n.id) == "restored" else LAYER_COLORS[layer] for n in group]
        fig.add_trace(go.Scatter(x=[pos[n.id][0] for n in group], y=[pos[n.id][1] for n in group], mode="markers+text", name=layer.replace("_", " ").title(), text=[n.name for n in group], textposition=["middle left" if pos[n.id][0] == right_edge else "middle right" for n in group], customdata=[n.id for n in group], hovertemplate="%{text}<br>%{customdata}<extra></extra>", marker={"symbol": SYMBOLS[layer], "size": [22 if n.tier0 else 16 for n in group], "color": colors, "line": {"color": "#111827" if high_contrast else "#FFFFFF", "width": [4 if n.tier0 else 1.5 for n in group]}}))
    fig.update_layout(height=max(620, len(nodes) * 12), margin={"l": 20, "r": 200, "t": 40, "b": 20}, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF", font={"size": 13, "color": "#111827"}, xaxis={"visible": False}, yaxis={"visible": False}, hovermode="closest", title="Deterministic resilience ecosystem map")
    return fig


def responsibility_csv(items):
    output = io.StringIO(); writer = csv.writer(output, lineterminator="\n")
    writer.writerow([SYNTHETIC_LABEL]); writer.writerow(["Activity", "Responsible", "Accountable", "Consulted", "Informed", "Deadline minutes", "Escalation", "Alternate"])
    for x in items: writer.writerow([x.activity, "; ".join(x.responsible), "; ".join(x.accountable), "; ".join(x.consulted), "; ".join(x.informed), x.deadline_minutes, x.escalation_authority, x.alternate])
    return output.getvalue()


def indicators_csv(items):
    output = io.StringIO(); writer = csv.writer(output, lineterminator="\n"); writer.writerow([SYNTHETIC_LABEL])
    writer.writerow(["Signal", "Data source", "Tool", "Monitoring team", "Tier 0 dependency", "Critical service", "Escalation threshold", "Possible benign cause"])
    for x in items: writer.writerow([x.signal, x.data_source, x.tool, x.monitoring_team, x.tier0_dependency, x.critical_service, x.escalation_threshold, x.possible_benign_cause])
    return output.getvalue()


def service_report(service, nodes, relationships):
    related = [r for r in relationships if r.source == service.id or r.destination == service.id]
    return "\n".join([f"# {service.name} Dependency Report", "", f"**{SYNTHETIC_LABEL}**", "", f"Owner: {service.owner}", f"Tier 0: {service.tier0}", "", "## Declared relationships", *[f"- {r.source} **{r.relationship_type}** {r.destination}: {r.description} ({r.confidence})" for r in related]])


def scenario_json(phase, states, decisions):
    return json.dumps({"synthetic_label": SYNTHETIC_LABEL, "phase": phase, "node_states": [x.model_dump() for x in states if x.phase == phase], "decisions": [x.model_dump() for x in decisions]}, indent=2)


def concentration(nodes, relationships):
    counts = Counter(r.destination for r in relationships if r.criticality == "critical")
    return {node.id: counts[node.id] for node in nodes if counts[node.id] > 1}
