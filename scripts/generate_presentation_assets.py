import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harbor_resilience.ecosystem import load_ecosystem
from harbor_resilience.presentation import (
    build_executive_deck,
    ecosystem_svg,
    write_board_pdf,
    write_deck_payload,
)


def main():
    nodes, relationships, responsibilities, indicators, coverage, _states = load_ecosystem()
    payload = ROOT / "tmp" / "presentation-build" / "executive-deck.json"
    svg = ROOT / "docs" / "images" / "high-level-banking-ecosystem.svg"
    pdf = ROOT / "output" / "pdf" / "harbor-ridge-executive-resilience-briefing.pdf"
    write_deck_payload(payload, nodes, relationships, responsibilities, indicators, coverage)
    svg.write_text(ecosystem_svg(nodes, relationships), encoding="utf-8")
    write_board_pdf(pdf, build_executive_deck(nodes, relationships, responsibilities, indicators, coverage))
    print(payload)
    print(svg)
    print(pdf)


if __name__ == "__main__":
    main()
