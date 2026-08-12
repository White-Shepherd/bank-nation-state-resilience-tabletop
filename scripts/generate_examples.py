import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harbor_resilience.data import load_services, load_tier0
from harbor_resilience.models import Decision
from harbor_resilience.reporting import after_action_markdown, board_markdown, write_pdf

decisions = [
    Decision(phase=phase, decision=decision, owner=owner, chosen_action=action,
             assumptions="Synthetic evidence is incomplete; attribution remains unresolved",
             dissent="Recorded for facilitator review",
             residual_risk="Residual service, integrity, or recovery uncertainty remains")
    for phase, decision, owner, action in [
        (0, "Raise threat posture", "Chief information security officer", "Enhance monitoring, freeze privileged changes, and validate independent backups"),
        (1, "Declare a cyber incident", "Incident commander", "Preserve evidence, correlate signals, hunt, and protect approved Tier 0 dependencies"),
        (2, "Invoke crisis management", "Chief executive officer", "Prioritize minimum viable payments and activate alternate communications"),
        (3, "Suspend selected posting", "Chief operations officer", "Hold uncertain transactions pending authoritative reconciliation"),
        (4, "Isolate identity infrastructure", "Chief information officer", "Use independent recovery credentials and controlled manual payment procedures"),
        (5, "Restore from a selected recovery point", "Incident commander", "Validate identity, configuration, transaction integrity, and reconciliation before staged restoration"),
    ]
]
services, tier0 = load_services(), load_tier0()
board = board_markdown(services, tier0, decisions)
board_dir = ROOT / "examples" / "board-packet"; exercise_dir = ROOT / "examples" / "completed-exercise"
board_dir.mkdir(parents=True, exist_ok=True); exercise_dir.mkdir(parents=True, exist_ok=True)
(board_dir / "board-packet.md").write_text(board, encoding="utf-8")
write_pdf(board, board_dir / "board-packet.pdf")
(exercise_dir / "after-action-report.md").write_text(after_action_markdown(["Chief risk officer", "Incident commander"], decisions), encoding="utf-8")
