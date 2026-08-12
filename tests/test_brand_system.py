import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def _pptx_parts(path: Path):
    with ZipFile(path) as archive:
        return archive.namelist()


def test_brand_tokens_are_complete_and_portable():
    tokens = json.loads((ROOT / "brand" / "brand-tokens.json").read_text(encoding="utf-8"))
    assert tokens["brand"]["name"] == "Continuum Resilience"
    assert tokens["brand"]["demonstration_client"] == "Harbor Ridge Bank"
    assert tokens["typography"]["font_family"] == "Aptos"
    assert tokens["typography"]["fallback"] == "Arial"
    assert tokens["typography"]["body"] >= 16
    assert tokens["accessibility"]["status_requires_text_or_pattern"] is True
    assert len(tokens["naming_candidates"]) == 3


def test_template_contains_master_and_requested_layouts():
    path = ROOT / "presentations" / "templates" / "resilience-platform-template.pptx"
    parts = _pptx_parts(path)
    layouts = [part for part in parts if part.startswith("ppt/slideLayouts/slideLayout") and part.endswith(".xml")]
    masters = [part for part in parts if part.startswith("ppt/slideMasters/slideMaster") and part.endswith(".xml")]
    assert len(layouts) >= 21
    assert masters


def test_completed_decks_have_expected_lengths_and_speaker_notes():
    expected = {
        ROOT / "presentations" / "board" / "executive-resilience-briefing.pptx": 12,
        ROOT / "presentations" / "technical" / "resilience-architecture-briefing.pptx": 11,
        ROOT / "presentations" / "tabletop" / "nation-state-exercise-facilitator.pptx": 14,
    }
    for path, count in expected.items():
        parts = _pptx_parts(path)
        slides = [part for part in parts if part.startswith("ppt/slides/slide") and part.endswith(".xml")]
        notes = [part for part in parts if part.startswith("ppt/notesSlides/notesSlide") and part.endswith(".xml")]
        assert len(slides) == count
        assert len(notes) == count


def test_verified_pdf_exports_exist():
    targets = [
        ROOT / "brand" / "brand-guide.pdf",
        ROOT / "presentations" / "templates" / "template-layout-catalog.pdf",
        ROOT / "presentations" / "board" / "executive-resilience-briefing.pdf",
        ROOT / "presentations" / "technical" / "resilience-architecture-briefing.pdf",
        ROOT / "presentations" / "tabletop" / "nation-state-exercise-facilitator.pdf",
    ]
    for target in targets:
        assert target.read_bytes().startswith(b"%PDF")
        assert target.stat().st_size > 20_000


def test_brand_assets_have_accessible_text():
    for path in (ROOT / "brand" / "assets").glob("*.svg"):
        svg = path.read_text(encoding="utf-8")
        assert "<title" in svg
        assert "<desc" in svg
