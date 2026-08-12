from pathlib import Path

import pytest
from pydantic import ValidationError

from harbor_resilience import SYNTHETIC_LABEL
from harbor_resilience.ecosystem import (
    VIEW_LAYERS,
    dependency_cycles,
    filter_graph,
    graph_figure,
    indicators_csv,
    load_ecosystem,
    propagate,
    responsibility_csv,
    scenario_json,
    service_report,
    validate_graph,
)
from harbor_resilience.models import EcosystemNode, EcosystemRelationship, ToolCoverage


@pytest.fixture(scope="module")
def ecosystem():
    return load_ecosystem()


def test_node_schema_owners_counts_and_accessibility(ecosystem):
    nodes = ecosystem[0]
    assert len(nodes) >= 120
    assert all(n.owner and n.operator and n.decision_authority and n.accessibility_label for n in nodes)
    assert len([n for n in nodes if n.layer == "critical_service"]) == 16
    assert len([n for n in nodes if n.layer == "internal_player"]) == 24
    assert len([n for n in nodes if n.layer == "external_player"]) == 20


def test_relationship_schema_and_endpoints(ecosystem):
    nodes, relationships = ecosystem[:2]
    assert len(relationships) >= 100
    validate_graph(nodes, relationships)
    required = {"supports", "depends_on", "administers", "owns", "operates", "monitors", "protects", "approves", "escalates_to", "reports_to", "recovers", "validates", "provides_data_to", "communicates_with", "regulates", "supplies", "fails_over_to"}
    assert required <= {r.relationship_type for r in relationships}
    base = relationships[0].model_dump(); base.update(id="bad", destination="MISSING")
    with pytest.raises(ValueError):
        validate_graph(nodes, relationships + [EcosystemRelationship.model_validate(base)])


def test_duplicate_nodes_cycles_and_unbounded_guard(ecosystem):
    nodes, relationships = ecosystem[:2]
    with pytest.raises(ValueError): validate_graph(nodes + [nodes[0]], relationships)
    cycles = dependency_cycles(nodes, relationships)
    assert any("IF-02" in cycle and "IF-04" in cycle for cycle in cycles)


def test_missing_owner_and_tier0_rationale_rejected():
    common = {"id": "x", "name": "x", "layer": "infrastructure", "node_type": "x", "description": "x", "operator": "x", "decision_authority": "x", "accessibility_label": "x"}
    with pytest.raises(ValidationError): EcosystemNode(owner="", **common)
    with pytest.raises(ValidationError): EcosystemNode(owner="x", tier0=True, **common)


def test_raci_conflicts_alternates_and_business_approval(ecosystem):
    responsibilities = ecosystem[2]
    assert all(len(x.accountable) == 1 and x.alternate for x in responsibilities)
    assert all(not x.technical_action or x.business_approval for x in responsibilities)


def test_tool_coverage_requires_data_source():
    with pytest.raises(ValidationError):
        ToolCoverage(capability_id="x", target_id="y", data_source="", deployed=True, configured=True, telemetry_received=True, detection_tested=False, response_integrated=False, recovery_visibility_validated=False, independent_investigation=False, limitation="x")


def test_scenario_state_transitions(ecosystem):
    assert sorted({x.phase for x in ecosystem[5]}) == list(range(8))


def test_declared_bounded_failure_propagation(ecosystem):
    nodes, relationships = ecosystem[:2]
    affected, explanations = propagate({"IF-01"}, nodes, relationships)
    assert "AD-06" in affected and explanations
    assert all(set(x) >= {"trigger", "dependency", "effect", "confidence", "assumptions", "compensating_control"} for x in explanations)
    assert len(affected) <= 1 + sum(r.propagation for r in relationships)


def test_graph_filtering_and_board_limit(ecosystem):
    nodes, relationships = ecosystem[:2]
    wire, _ = filter_graph(nodes, relationships, service="CBS-05")
    assert wire and all(n.id == "CBS-05" or "CBS-05" in n.critical_services for n in wire)
    board, _ = filter_graph(nodes, relationships, layers=VIEW_LAYERS["Board view"])
    principal = {"IP-01", "IP-02", "IP-03", "IP-07", "EP-01", "EP-02", "EP-04"}
    board = [n for n in board if n.layer == "critical_service" or n.tier0 or n.id in principal]
    assert len(board) <= 50


def test_graph_exports_and_table_fallbacks(ecosystem, tmp_path):
    nodes, relationships, responsibilities, indicators, _, states = ecosystem
    selected = nodes[:10]; ids = {n.id for n in selected}
    fig = graph_figure(selected, [r for r in relationships if r.source in ids and r.destination in ids])
    target = tmp_path / "graph.html"
    target.write_text(SYNTHETIC_LABEL + fig.to_html(full_html=True), encoding="utf-8")
    assert target.exists() and SYNTHETIC_LABEL in target.read_text(encoding="utf-8")
    assert SYNTHETIC_LABEL in responsibility_csv(responsibilities)
    assert SYNTHETIC_LABEL in indicators_csv(indicators)
    assert SYNTHETIC_LABEL in scenario_json(5, states, [])
    assert SYNTHETIC_LABEL in service_report(nodes[0], nodes, relationships)


def test_all_ecosystem_files_synthetic():
    root = Path(__file__).resolve().parents[1] / "data" / "ecosystem"
    for path in root.glob("*.yaml"):
        assert SYNTHETIC_LABEL in path.read_text(encoding="utf-8"), path
