from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from . import SYNTHETIC_LABEL

SECTIONS = ["Executive summary", "Scenario", "Critical services", "Tier 0 methodology", "Tier 0 concentration risks", "Current preparedness", "Material control gaps", "Exercise decisions", "Impact-tolerance breaches", "Residual risk", "Investment alternatives", "Management recommendation", "Board decisions requested", "Ninety-day actions", "One-year resilience roadmap", "Metrics for board oversight"]


def board_markdown(services, tier0, decisions) -> str:
    lines = [f"# Harbor Ridge Bank Board Risk Packet\n\n**{SYNTHETIC_LABEL}**", ""]
    content = {
        "Executive summary": "A coordinated disruption could exceed service and data-integrity tolerances because identity, payments, telecommunications, and recovery have common-mode dependencies. This packet supports review; it does not make the board's decision.",
        "Scenario": "Geopolitical conflict drives ambiguous pre-positioning followed by identity, channel, payment, telecommunications, integrity, and recovery disruption.",
        "Critical services": f"{len(services)} services are modeled from customer authentication through technology recovery.",
        "Tier 0 methodology": "Begin with critical services and tolerances; map dependencies; identify common-mode failure; apply explicit rules; require accountable human approval. Tier 0 is Harbor Ridge terminology, not a regulatory designation or a NIST CSF Implementation Tier.",
        "Tier 0 concentration risks": ", ".join(x.name for x in tier0 if x.approved) + ".",
        "Current preparedness": "Synthetic baseline: partial immutable backup, manual payment, privileged access, and alternate communications capability; validation remains required.",
        "Material control gaps": "Recovery administration shares production identity; telecommunications and payment processors remain concentrated; recovery-point integrity validation is incomplete.",
        "Exercise decisions": f"{len(decisions)} decisions recorded. Empty outcomes are not presented as performance results.",
        "Impact-tolerance breaches": "Calculated from elapsed disruption, backlog, and data uncertainty; none are asserted before exercise inputs exist.",
        "Residual risk": "Material residual risk remains until clean-room recovery, independent credentials, reconciliation, and substitution plans are demonstrated.",
        "Investment alternatives": "Prioritize independent clean-room recovery; phishing-resistant administrative authentication; immutable, integrity-validated backups; telecommunications diversity; and third-party exit testing.",
        "Management recommendation": "Fund a sequenced resilience program that first removes recovery common modes, then expands detection, redundancy, and repeatable validation.",
        "Board decisions requested": "Approve appetite statements, investment envelope, accountable owners, and quarterly evidence-based oversight.",
        "Ninety-day actions": "Inventory and approve Tier 0; freeze unmanaged privilege; test clean credentials; validate immutable copies; rehearse minimum viable payments and alternate communications.",
        "One-year resilience roadmap": "Quarter 1: control-plane isolation. Quarter 2: clean-room exercise. Quarter 3: processor and carrier substitution. Quarter 4: enterprise reconciliation and board tolerance test.",
        "Metrics for board oversight": "Tested Tier 0 recovery; phishing-resistant admin MFA; isolation from production identity; manual-procedure coverage; concentration; privilege-disable time; clean-room time; unreconciled transactions; tolerance-meeting exercises; telemetry; critical findings; backup immutability; recovery-point integrity validation.",
    }
    for section in SECTIONS:
        lines += [f"## {section}", "", content[section], ""]
    return "\n".join(lines)


def after_action_markdown(participants, decisions) -> str:
    decision_lines = "\n".join(f"- Phase {d.phase}: {d.decision} - {d.chosen_action}" for d in decisions) or "- No decisions recorded; populate during the exercise."
    return f"""# Harbor Ridge Bank After-Action Report

**{SYNTHETIC_LABEL}**

## Exercise objectives
Recognize connected warning, protect critical services and Tier 0 dependencies, preserve payments and liquidity, protect integrity, communicate, and recover safely.

## Participants
{', '.join(participants) or 'To be recorded during the exercise.'}

## Scenario timeline
Six phases from strategic warning through trusted restoration. Actual timestamps are recorded by the application.

## Decisions
{decision_lines}

## Findings requiring facilitator entry
Strengths, gaps, contradictions, missed escalation opportunities, tolerance breaches, recovery weaknesses, third-party weaknesses, and communications gaps must be supported by observed exercise evidence. No performance result is invented here.

## Corrective-action plan
For each validated gap, record action, accountable owner, due date, validation criterion, dependency, and residual risk. Counsel and compliance review jurisdiction-dependent notifications.

## Lessons for the board
Review which tolerances were challenged, which common modes constrained decisions, and which investments reduce both disruption and untrustworthy recovery risk.
"""


def write_pdf(markdown: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles["BodyText"].fontSize = 8.5
    styles["BodyText"].leading = 9.5
    styles.add(ParagraphStyle(name="Label", parent=styles["Normal"], textColor=colors.HexColor("#A61B1B"), alignment=TA_CENTER, fontSize=9))
    story = []
    for line in markdown.splitlines():
        if line.startswith("# "):
            story.extend([Paragraph(line[2:], styles["Title"]), Spacer(1, 10)])
        elif line.startswith("## "):
            story.extend([Spacer(1, 8), Paragraph(line[3:], styles["Heading2"]), Spacer(1, 4)])
        elif line.startswith("**"):
            story.append(Paragraph(line.strip("*"), styles["Label"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + line[2:], styles["BodyText"]))
        elif line.strip():
            story.append(Paragraph(line, styles["BodyText"]))
    def footer(canvas, doc):
        canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.grey)
        canvas.drawString(0.65 * inch, 0.4 * inch, SYNTHETIC_LABEL)
        canvas.drawRightString(7.85 * inch, 0.4 * inch, f"Page {doc.page}"); canvas.restoreState()
    SimpleDocTemplate(str(path), pagesize=letter, rightMargin=0.65*inch, leftMargin=0.65*inch, topMargin=0.65*inch, bottomMargin=0.65*inch, title="Harbor Ridge Bank Board Risk Packet").build(story, onFirstPage=footer, onLaterPages=footer)
