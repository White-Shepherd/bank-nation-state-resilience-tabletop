from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harbor_resilience.assessment import (
    board_packet_markdown,
    load_assessment,
    responsibility_csv,
)
from harbor_resilience.reporting import write_pdf


def main() -> None:
    assessment = load_assessment(ROOT / "data/synthetic_assessments/harbor-ridge-2026.json")
    output = ROOT / "examples/assessment-exports"
    output.mkdir(parents=True, exist_ok=True)
    markdown = board_packet_markdown(assessment)
    (output / "harbor-ridge-board-assessment.md").write_text(markdown, encoding="utf-8")
    (output / "harbor-ridge-responsibility-matrix.csv").write_text(
        responsibility_csv(assessment), encoding="utf-8"
    )
    (output / "harbor-ridge-assessment.json").write_text(
        assessment.model_dump_json(indent=2), encoding="utf-8"
    )
    write_pdf(markdown, ROOT / "output/pdf/harbor-ridge-board-assessment.pdf")
    print("Generated synthetic assessment JSON, CSV, Markdown, and PDF exports")


if __name__ == "__main__":
    main()
