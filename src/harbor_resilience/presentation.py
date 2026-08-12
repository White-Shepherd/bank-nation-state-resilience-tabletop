from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import SYNTHETIC_LABEL
from .ecosystem import concentration

PALETTE = {
    "ink": "#11243A",
    "navy": "#17395C",
    "blue": "#2B6F9E",
    "teal": "#16867A",
    "amber": "#C98324",
    "red": "#A63D40",
    "green": "#337A5B",
    "slate": "#5C6B7A",
    "mist": "#EDF3F5",
    "paper": "#F8FAFB",
    "white": "#FFFFFF",
}


@dataclass(frozen=True)
class Slide:
    number: int
    section: str
    title: str
    subtitle: str
    visual: str
    bullets: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


def _name_map(nodes):
    return {node.id: node.name for node in nodes}


def executive_metrics(nodes, relationships, indicators, coverage) -> dict:
    counts = Counter(node.layer for node in nodes)
    tier0 = [node for node in nodes if node.tier0]
    concentration_counts = concentration(nodes, relationships)
    names = _name_map(nodes)
    ranked = [
        {"id": node_id, "name": names[node_id], "critical_relationships": count}
        for node_id, count in sorted(
            concentration_counts.items(), key=lambda item: (-item[1], names[item[0]])
        )
    ]
    recovery_gaps = [
        node
        for node in nodes
        if node.recovery_capability and "unvalidated" in " ".join(node.limitations).lower()
    ]
    return {
        "node_count": len(nodes),
        "relationship_count": len(relationships),
        "critical_service_count": counts["critical_service"],
        "tier0_count": len(tier0),
        "internal_player_count": counts["internal_player"],
        "external_player_count": counts["external_player"],
        "warning_indicator_count": len(indicators),
        "tool_coverage_count": len(coverage),
        "top_concentrations": ranked,
        "recovery_gap_count": len(recovery_gaps),
    }


def build_executive_deck(nodes, relationships, responsibilities, indicators, coverage) -> list[Slide]:
    metrics = executive_metrics(nodes, relationships, indicators, coverage)
    top = metrics["top_concentrations"][:5]
    conflict_count = sum(len(item.accountable) != 1 for item in responsibilities)
    alternate_gaps = sum(not item.alternate for item in responsibilities)
    return [
        Slide(1, "Purpose", "Shared control planes turn isolated outages into enterprise decisions", "Board resilience briefing | Harbor Ridge Bank | fictional exercise", "title", (
            "Connect technical dependency to customer, payment, liquidity, and recovery consequence.",
            "Use declared evidence to frame timed executive decisions.",
            "Approve resilience priorities without treating relationship counts as risk scores.",
        )),
        Slide(2, "Executive summary", "Four management choices determine whether disruption becomes customer harm", "Protect identity, preserve transaction integrity, sustain minimum viable payments, and recover independently.", "summary", (
            "Identity is the largest declared shared dependency.",
            "Availability is not evidence that balances or journals are trustworthy.",
            "Recovery must work without production credentials, name resolution, or monitoring.",
            "Decision rights and alternates must be explicit before a timed crisis.",
        )),
        Slide(3, "Operating model", "Critical services depend on a concentrated set of shared control planes", f"{metrics['critical_service_count']} services are connected through declared business, technology, security, people, third-party, and recovery relationships.", "ecosystem", (
            "Customer access, money movement, financial control, and recovery form the board-level service groups.",
            "Enterprise identity and backup are the two largest declared critical-relationship concentrations.",
            "Every board item links back to a modeled node or relationship.",
        ), tuple(item["id"] for item in top)),
        Slide(4, "Concentration", "Enterprise identity is the largest explicitly modeled common-mode dependency", "The count reflects critical relationships in the synthetic model; it is not a probability or loss estimate.", "concentration", tuple(f"{item['name']}: {item['critical_relationships']} critical relationships" for item in top), tuple(item["id"] for item in top)),
        Slide(5, "Risk", "A trusted-looking payment can still be operationally unsafe", "The containment decision must balance channel availability against data-integrity uncertainty.", "risk", (
            "Customer harm rises as access and payment channels degrade.",
            "Settlement and liquidity decisions require independently reconciled positions.",
            "Weak signals do not establish nation-state attribution.",
        )),
        Slide(6, "Scenario", "Ambiguous warning becomes a timed integrity and containment dilemma", "Eight phases reveal only explicitly modeled service effects and decision deadlines.", "timeline", (
            "Normal operations establish the evidence baseline.",
            "Warning and pre-positioning reveal weak signals without automatic attribution.",
            "Disruption and integrity uncertainty create the containment decision.",
            "Recovery and stabilization require independent validation.",
        )),
        Slide(7, "Incident command", "Decision quality depends on evidence reaching the right owner before the deadline", f"The responsibility model contains {conflict_count} accountability conflicts and {alternate_gaps} missing alternates requiring review.", "decisions", (
            "Declare and activate crisis management.",
            "Isolate identity or suspend a payment channel.",
            "Approve a recovery point and validate ledger integrity.",
            "Communicate externally only after legal and jurisdictional review.",
        )),
        Slide(8, "Technology", "Tier 0 is a recovery and decision boundary—not a product label", f"{metrics['tier0_count']} synthetic dependencies are flagged Tier 0 with rationale and accountable ownership.", "technical", (
            "Control-plane authority can create common-mode failure.",
            "Monitoring coverage is qualified by telemetry, testing, and recovery availability.",
            "Every modeled propagation path carries assumptions and confidence.",
        )),
        Slide(9, "Recovery", "Production dependencies can follow the bank into recovery", "Clean-room recovery is credible only when identity, DNS, credentials, telemetry, and integrity validation are independent.", "recovery", (
            "Replication may reproduce corruption.",
            "Backup availability does not prove transaction integrity.",
            "Failover without monitoring can reduce confidence when it matters most.",
        )),
        Slide(10, "Investment", "The first investments should remove recovery common modes", "Priorities are qualitative and traceable to declared dependency paths; no false precision is applied.", "investment", (
            "Independent recovery identity and privileged workstations.",
            "Immutable backups plus offline integrity evidence.",
            "Independent name resolution and telecommunications diversity.",
            "Transaction-integrity validation and tested manual payments.",
        )),
        Slide(11, "Oversight", "Board measures should test resilience outcomes, not tool ownership", "Track evidence that controls are configured, receiving telemetry, tested, integrated, and visible during recovery.", "metrics", (
            "Tier 0 recovery tests completed with independent credentials.",
            "Time to disable privilege and establish minimum viable payments.",
            "Unreconciled transactions and integrity exceptions.",
            "Third-party substitution and alternate communications exercised.",
        )),
        Slide(12, "Decision", "Approve a sequenced program that makes recovery independent and evidence-led", "Management should return with accountable owners, bounded milestones, validation criteria, and residual-risk decisions.", "close", (
            "Approve the resilience priorities and ownership model.",
            "Require quarterly evidence against service tolerances.",
            "Revalidate Tier 0 after material architecture or provider change.",
        )),
    ]


def deck_payload(nodes, relationships, responsibilities, indicators, coverage) -> dict:
    return {
        "synthetic_label": SYNTHETIC_LABEL,
        "design": {"aspect_ratio": "16:9", "palette": PALETTE, "minimum_body_pt": 16},
        "metrics": executive_metrics(nodes, relationships, indicators, coverage),
        "slides": [asdict(slide) for slide in build_executive_deck(nodes, relationships, responsibilities, indicators, coverage)],
    }


def write_deck_payload(path: Path, nodes, relationships, responsibilities, indicators, coverage) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(deck_payload(nodes, relationships, responsibilities, indicators, coverage), indent=2), encoding="utf-8")
    return path


def ecosystem_svg(nodes, relationships, width: int = 1600, height: int = 900) -> str:
    metrics = executive_metrics(nodes, relationships, [], [])
    names = _name_map(nodes)
    top = metrics["top_concentrations"][:5]
    service_groups = [
        ("CUSTOMER ACCESS", ["CBS-01", "CBS-02", "CBS-14"]),
        ("MONEY MOVEMENT", ["CBS-04", "CBS-05", "CBS-06", "CBS-07", "CBS-08", "CBS-09"]),
        ("CONTROL & RECORD", ["CBS-03", "CBS-10", "CBS-11", "CBS-12", "CBS-13"]),
        ("CRISIS & RECOVERY", ["CBS-15", "CBS-16"]),
    ]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Shared control planes connect critical banking services</title>',
        '<desc id="desc">Four groups of critical services rely on five highlighted shared dependencies. Enterprise identity has the highest declared critical relationship count. All data is synthetic.</desc>',
        '<rect width="1600" height="900" fill="#F8FAFB"/>',
        '<rect x="0" y="0" width="1600" height="12" fill="#16867A"/>',
        '<text x="90" y="92" font-family="Arial" font-size="43" font-weight="700" fill="#11243A">Critical banking services rely on shared control planes</text>',
        '<text x="90" y="137" font-family="Arial" font-size="23" fill="#5C6B7A">Concentrated authority can create common-mode failure across otherwise separate services.</text>',
        '<text x="90" y="187" font-family="Arial" font-size="15" font-weight="700" letter-spacing="1.2" fill="#2B6F9E">CRITICAL BANKING SERVICES</text>',
    ]
    group_w, group_gap, x0 = 330, 32, 90
    for index, (label, ids) in enumerate(service_groups):
        x = x0 + index * (group_w + group_gap)
        lines.extend([
            f'<rect x="{x}" y="215" width="{group_w}" height="220" rx="16" fill="#FFFFFF" stroke="#C8D5DD" stroke-width="2"/>',
            f'<text x="{x + 24}" y="251" font-family="Arial" font-size="15" font-weight="700" letter-spacing=".8" fill="#2B6F9E">{escape(label)}</text>',
        ])
        for row, node_id in enumerate(ids):
            lines.append(f'<text x="{x + 24}" y="{287 + row * 26}" font-family="Arial" font-size="17" fill="#11243A">{escape(names[node_id])}</text>')
    lines.extend([
        '<path d="M255 435 V500 H1345 V435 M617 435 V500 M979 435 V500" fill="none" stroke="#6F8798" stroke-width="3"/>',
        '<path d="M800 500 V555" fill="none" stroke="#6F8798" stroke-width="3" marker-end="url(#arrow)"/>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#6F8798"/></marker></defs>',
        '<text x="90" y="585" font-family="Arial" font-size="15" font-weight="700" letter-spacing="1.2" fill="#2B6F9E">SHARED TIER 0 AND RECOVERY DEPENDENCIES</text>',
    ])
    dep_w, dep_gap = 258, 24
    for index, item in enumerate(top):
        x = 90 + index * (dep_w + dep_gap)
        accent = PALETTE["red"] if index == 0 else PALETTE["amber"]
        display_name = item["name"].replace(" environment", "")
        lines.extend([
            f'<rect x="{x}" y="615" width="{dep_w}" height="135" rx="14" fill="#FFFFFF" stroke="{accent}" stroke-width="{4 if index == 0 else 2}"/>',
            f'<text x="{x + 20}" y="654" font-family="Arial" font-size="18" font-weight="700" fill="#11243A">{escape(display_name)}</text>',
            f'<text x="{x + 20}" y="693" font-family="Arial" font-size="34" font-weight="700" fill="{accent}">{item["critical_relationships"]}</text>',
            f'<text x="{x + 62}" y="692" font-family="Arial" font-size="15" fill="#5C6B7A">critical relationships</text>',
            f'<text x="{x + 20}" y="724" font-family="Arial" font-size="14" fill="#5C6B7A">Declared in the synthetic model</text>',
        ])
    lines.extend([
        '<rect x="90" y="800" width="1420" height="48" rx="8" fill="#11243A"/>',
        '<text x="116" y="831" font-family="Arial" font-size="18" font-weight="700" fill="#FFFFFF">BOARD IMPLICATION</text>',
        '<text x="330" y="831" font-family="Arial" font-size="18" fill="#FFFFFF">Protect shared authority, validate integrity independently, and recover without production control planes.</text>',
        f'<text x="1510" y="879" text-anchor="end" font-family="Arial" font-size="13" fill="#5C6B7A">{escape(SYNTHETIC_LABEL)}</text>',
        '</svg>',
    ])
    return "".join(lines)


def write_board_pdf(path: Path, slides: list[Slide]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=landscape(letter), leftMargin=.7 * inch, rightMargin=.7 * inch, topMargin=.5 * inch, bottomMargin=.45 * inch)
    title_style = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=colors.HexColor(PALETTE["ink"]), spaceAfter=10)
    subtitle_style = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=12.5, leading=17, textColor=colors.HexColor(PALETTE["slate"]), spaceAfter=18)
    body_style = ParagraphStyle("body", fontName="Helvetica", fontSize=12, leading=17, textColor=colors.HexColor(PALETTE["ink"]), leftIndent=12, bulletIndent=0, alignment=TA_LEFT)
    label_style = ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=8.5, leading=10, textColor=colors.HexColor(PALETTE["blue"]), spaceAfter=8)
    story = []
    for index, slide in enumerate(slides):
        story.append(Paragraph(f"{slide.section.upper()} &nbsp;&nbsp; {index + 1:02d}", label_style))
        story.append(Paragraph(escape(slide.title), title_style))
        story.append(Paragraph(escape(slide.subtitle), subtitle_style))
        if slide.bullets:
            rows = [[Paragraph(f"<bullet>&#8226;</bullet>{escape(item)}", body_style)] for item in slide.bullets]
            table = Table(rows, colWidths=[9.1 * inch], rowHeights=None)
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(PALETTE["paper"])), ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CCD8DF")), ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DCE5EA")), ("LEFTPADDING", (0, 0), (-1, -1), 18), ("RIGHTPADDING", (0, 0), (-1, -1), 18), ("TOPPADDING", (0, 0), (-1, -1), 11), ("BOTTOMPADDING", (0, 0), (-1, -1), 11)]))
            story.append(table)
        else:
            story.append(Spacer(1, 2.8 * inch))
        story.append(Spacer(1, .16 * inch))
        story.append(Paragraph(escape(SYNTHETIC_LABEL), label_style))
        if index < len(slides) - 1:
            story.append(PageBreak())
    doc.build(story)
    return path
