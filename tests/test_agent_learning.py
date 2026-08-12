from pathlib import Path

from scripts.validate_agent_learning import ALLOWED_STATUSES, metadata, validate

ROOT = Path(__file__).resolve().parents[1]


def test_agent_learning_framework_is_valid():
    assert validate(ROOT) == []


def test_status_schema_is_bounded():
    assert ALLOWED_STATUSES == {"proposed", "validated", "rejected", "superseded"}


def test_metadata_parser_reads_record_fields():
    fields = metadata("## Metadata\n\n- Agent role: Builder\n- Status: proposed\n")
    assert fields == {"Agent role": "Builder", "Status": "proposed"}


def test_validator_detects_missing_metadata_and_secret(tmp_path):
    record = tmp_path / "docs/agent-learning/lessons/builder/2026-08-12-1803-example.md"
    record.parent.mkdir(parents=True)
    record.write_text(
        "# Agent Lesson Record\n\n## Metadata\n\n- Agent role: Builder\n"
        "- Status: invalid\n\npassword = \"not-a-real-secret-value\"\n",
        encoding="utf-8",
    )
    errors = validate(tmp_path)
    assert any("missing metadata 'Task'" in error for error in errors)
    assert any("invalid status" in error for error in errors)
    assert any("credential assignment" in error for error in errors)


def test_validator_detects_broken_links_and_paths(tmp_path):
    root = tmp_path
    record = root / "docs/agent-learning/lessons/builder/2026-08-12-1803-example.md"
    record.parent.mkdir(parents=True)
    record.write_text(
        "# Agent Lesson Record\n\n## Metadata\n\n"
        "- Agent role: Builder\n- Task: Test\n- Branch: test\n"
        "- Commit reviewed or produced: abc\n- Date: 2026-08-12\n- Status: proposed\n\n"
        "[missing](missing.md) and `docs/not-present.md`\n",
        encoding="utf-8",
    )
    errors = validate(root)
    assert any("broken internal link" in error for error in errors)
    assert any("missing repository path" in error for error in errors)
