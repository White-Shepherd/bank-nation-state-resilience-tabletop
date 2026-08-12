from harbor_resilience import SYNTHETIC_LABEL
from harbor_resilience.ecosystem import load_ecosystem
from harbor_resilience.presentation import (
    PALETTE,
    build_executive_deck,
    deck_payload,
    ecosystem_svg,
    executive_metrics,
    write_board_pdf,
    write_deck_payload,
)


def _data():
    return load_ecosystem()[:5]


def test_default_board_narrative_is_bounded_and_message_driven():
    nodes, relationships, responsibilities, indicators, coverage = _data()
    slides = build_executive_deck(nodes, relationships, responsibilities, indicators, coverage)
    assert 10 <= len(slides) <= 14
    assert [slide.number for slide in slides] == list(range(1, len(slides) + 1))
    assert all(len(slide.title.split()) >= 6 for slide in slides)
    assert slides[-1].section == "Decision"


def test_concentration_uses_declared_critical_relationships():
    nodes, relationships, _responsibilities, indicators, coverage = _data()
    metrics = executive_metrics(nodes, relationships, indicators, coverage)
    identity = metrics["top_concentrations"][0]
    expected = sum(
        relationship.destination == identity["id"] and relationship.criticality == "critical"
        for relationship in relationships
    )
    assert identity["name"] == "Enterprise identity provider"
    assert identity["critical_relationships"] == expected == 7


def test_payload_preserves_design_and_synthetic_label(tmp_path):
    data = _data()
    payload = deck_payload(*data)
    target = write_deck_payload(tmp_path / "deck.json", *data)
    assert payload["synthetic_label"] == SYNTHETIC_LABEL
    assert payload["design"]["aspect_ratio"] == "16:9"
    assert payload["design"]["minimum_body_pt"] >= 16
    assert {"ink", "teal", "amber", "red", "green"} <= PALETTE.keys()
    assert target.exists()


def test_executive_svg_has_text_alternative_and_no_hairball():
    nodes, relationships, _responsibilities, _indicators, _coverage = _data()
    svg = ecosystem_svg(nodes, relationships)
    assert "<title" in svg and "<desc" in svg
    assert SYNTHETIC_LABEL in svg
    assert "critical relationships" in svg
    assert svg.count("<path") < 10
    assert "risk score" not in svg.lower()


def test_board_pdf_is_generated_and_labeled(tmp_path):
    data = _data()
    slides = build_executive_deck(*data)
    target = write_board_pdf(tmp_path / "board.pdf", slides)
    assert target.read_bytes().startswith(b"%PDF")
    assert target.stat().st_size > 10_000


def test_slide_evidence_identifiers_are_declared_nodes():
    nodes, relationships, responsibilities, indicators, coverage = _data()
    known = {node.id for node in nodes}
    slides = build_executive_deck(nodes, relationships, responsibilities, indicators, coverage)
    assert all(set(slide.evidence_ids) <= known for slide in slides)
