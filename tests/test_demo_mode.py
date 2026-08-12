from pathlib import Path

from harbor_resilience.demo import CHECKPOINTS, DEMO_ASSESSMENT, demo_snapshot


def test_demo_has_ten_named_checkpoints():
    assert CHECKPOINTS == [
        "Overview",
        "Critical service",
        "Impact tolerance",
        "Dependency map",
        "Tier 0",
        "Concentration finding",
        "Scenario warning",
        "Integrity dilemma",
        "Recovery",
        "Board packet",
    ]


def test_demo_uses_only_canonical_synthetic_assessment():
    assert DEMO_ASSESSMENT == Path("data/synthetic_assessments/harbor-ridge-2026.json")
    assert "private_assessments" not in str(DEMO_ASSESSMENT)
    snapshot = demo_snapshot()
    assert snapshot["assessment"].organization.name == "Harbor Ridge Bank"
    assert snapshot["assessment"].services


def test_demo_analysis_is_computed_without_mutating_source():
    before = DEMO_ASSESSMENT.read_bytes()
    snapshot = demo_snapshot()
    assert snapshot["candidates"]
    assert snapshot["findings"] or snapshot["gaps"]
    assert DEMO_ASSESSMENT.read_bytes() == before


def test_video_package_has_all_scripts_and_storyboards():
    names = [
        "01-platform-overview.md",
        "02-critical-service-assessment.md",
        "03-tier0-dependency-analysis.md",
        "04-nation-state-tabletop.md",
        "05-recovery-resilience.md",
        "06-board-decisions.md",
        "portfolio-cut.md",
    ]
    for name in names:
        assert (Path("video/scripts") / name).exists()
        assert (Path("video/storyboards") / name).exists()


def test_recording_output_is_git_ignored():
    assert "video/recordings/" in Path(".gitignore").read_text(encoding="utf-8")
