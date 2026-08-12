import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harbor_resilience import SYNTHETIC_LABEL
from harbor_resilience.ecosystem import (
    VIEW_LAYERS,
    filter_graph,
    graph_figure,
    indicators_csv,
    load_ecosystem,
    responsibility_csv,
    scenario_json,
    service_report,
    validate_graph,
)
from harbor_resilience.reporting import write_pdf

nodes, relationships, responsibilities, indicators, coverage, states = load_ecosystem()
validate_graph(nodes, relationships)
out = ROOT / "examples" / "ecosystem-exports"; images = ROOT / "docs" / "images"; pdfs = ROOT / "output" / "pdf"
for path in (out, images, pdfs): path.mkdir(parents=True, exist_ok=True)


def export_view(name, selected_nodes, selected_edges, stagger_labels=False):
    fig = graph_figure(selected_nodes, selected_edges)
    if stagger_labels:
        positions = {"Critical Service": "bottom center", "Business Process": "top center", "Application Data": "bottom center", "Infrastructure": "top center", "Security": "bottom center", "Internal Player": "bottom center"}
        for trace in fig.data:
            if "markers+text" in (trace.mode or ""):
                trace.textposition = positions.get(trace.name, "middle right")
    fig.update_layout(title=f"{name.replace('-', ' ').title()} | {SYNTHETIC_LABEL}", height=900)
    fig.write_html(out / f"{name}.html", include_plotlyjs="cdn", full_html=True)
    fig.write_image(images / f"{name}.svg", width=1600, height=900)
    fig.write_image(images / f"{name}.png", width=1600, height=900, scale=1)


board, board_edges = filter_graph(nodes, relationships, layers=VIEW_LAYERS["Board view"])
principal = {"IP-01", "IP-02", "IP-03", "IP-07", "EP-01", "EP-02", "EP-04"}
board = [n for n in board if n.layer == "critical_service" or n.tier0 or n.id in principal]
ids = {n.id for n in board}; board_edges = [r for r in board_edges if r.source in ids and r.destination in ids]
export_view("high-level-banking-ecosystem", board, board_edges)

tier = [n for n in nodes if n.tier0 or n.layer == "critical_service"]
ids = {n.id for n in tier}; export_view("tier0-dependency-map", tier, [r for r in relationships if r.source in ids and r.destination in ids])

wire = [n for n in nodes if n.id == "CBS-05" or "CBS-05" in n.critical_services]
ids = {n.id for n in wire}; export_view("wire-transfer-service-map", wire, [r for r in relationships if r.source in ids and r.destination in ids])

identity_ids = {"CBS-01", "BP-08", "AD-09", "IF-01", "SC-04", "IP-09", "IP-04", "IP-07"}
identity = [n for n in nodes if n.id in identity_ids]; export_view("identity-compromise-propagation-map", identity, [r for r in relationships if r.source in identity_ids and r.destination in identity_ids], stagger_labels=True)

recovery = [n for n in nodes if n.recovery_capability or n.id in {"IF-01", "IF-04", "IF-17", "IF-18", "CBS-03", "CBS-05", "CBS-12", "CBS-16", "AD-14", "AD-16", "IP-05", "IP-18"}]
ids = {n.id for n in recovery}; export_view("recovery-dependency-map", recovery, [r for r in relationships if r.source in ids and r.destination in ids])

crisis_ids = {"IP-01", "IP-02", "IP-03", "IP-04", "IP-05", "IP-06", "IP-07", "IP-14", "IP-18", "IP-20", "IP-21", "IP-22", "EP-10", "EP-12", "EP-13", "EP-15", "EP-19", "EP-20"}
crisis = [n for n in nodes if n.id in crisis_ids]; export_view("crisis-responsibility-map", crisis, [r for r in relationships if r.source in crisis_ids and r.destination in crisis_ids])

(out / "responsibility-matrix.csv").write_text(responsibility_csv(responsibilities), encoding="utf-8")
(out / "warning-indicator-matrix.csv").write_text(indicators_csv(indicators), encoding="utf-8")
(out / "current-scenario-state.json").write_text(scenario_json(5, states, []), encoding="utf-8")
wire_node = next(n for n in nodes if n.id == "CBS-05")
(out / "wire-transfer-dependency-report.md").write_text(service_report(wire_node, nodes, relationships), encoding="utf-8")
(out / "decision-log.csv").write_text(f"synthetic_label,phase,decision,owner,action,residual_risk\n{SYNTHETIC_LABEL},5,Isolate identity systems,IP-05,Use independent recovery identity,Payment delay remains\n", encoding="utf-8")

tier_md = "\n".join(["# Tier 0 Dependency Map", "", f"**{SYNTHETIC_LABEL}**", "", "Institution-specific operational designation; not a NIST CSF Implementation Tier. Human approval and evidence remain required.", "", "## Approved synthetic candidates", "", *[f"- {n.name}: {n.tier0_rationale}. Owner: {n.owner}. Services: {', '.join(n.critical_services)}." for n in nodes if n.tier0], "", "## Review rule", "", "Revalidate after material change and test recovery without assuming availability proves integrity."])
board_md = "\n".join(["# Board Ecosystem Risk View", "", f"**{SYNTHETIC_LABEL}**", "", "## Critical services", "Sixteen critical services are connected to explicitly declared Tier 0, owner, external, monitoring, and recovery relationships.", "", "## Current decision frame", "Customer harm: review affected-service thresholds. Payment and settlement: preserve obligations without posting untrusted data. Liquidity: maintain independently reconciled position. Integrity and recovery confidence remain unvalidated until evidence supports restoration.", "", "## Concentrations", "Enterprise identity, privileged access, payment gateway, telecommunications, backup, DNS, certificates, and third parties require accountable review.", "", "## Evidence", "Relationship identifiers connect every board item to a declared dependency, rationale, owner, incident behavior, and recovery behavior. Weak signals do not establish attribution.", "", "## Decisions", "Approve recovery identity independence, transaction integrity validation, carrier diversity, and tested substitution without assuming any control is infallible.", "", "## Oversight measures", "Track Tier 0 recovery tests, independent investigation, recovery visibility, manual-service capacity, third-party substitution, unreconciled transactions, and overdue corrective actions."])
write_pdf(tier_md, pdfs / "tier0-dependency-map.pdf")
write_pdf(board_md, pdfs / "board-ecosystem-risk-view.pdf")
