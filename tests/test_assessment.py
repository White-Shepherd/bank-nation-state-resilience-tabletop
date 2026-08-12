import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from harbor_resilience.assessment import (
    BRANCHING_RULES,
    SYNTHETIC_NOTICE,
    backup_assessment,
    board_packet_markdown,
    bulk_csv_rows,
    completeness,
    delete_draft,
    duplicate_assessment,
    generate_analysis,
    generate_tier0_candidates,
    import_assessment,
    integrity_digest,
    load_assessment,
    raci_conflicts,
    save_assessment,
    tolerance_conflicts,
)
from harbor_resilience.assessment_models import Assessment, CriticalService, ImpactProfile
from harbor_resilience.reporting import write_pdf

DEMO = Path("data/synthetic_assessments/harbor-ridge-2026.json")


@pytest.fixture
def assessment():
    return load_assessment(DEMO)


def test_all_models_validate_in_demonstration(assessment):
    assert Assessment.model_validate(assessment.model_dump())
    assert all(
        type(item).model_validate(item.model_dump())
        for name in type(assessment).model_fields
        for item in (
            getattr(assessment, name) if isinstance(getattr(assessment, name), list) else []
        )
    )


def test_assessment_creation_and_required_scale(assessment):
    assert len(assessment.services) >= 12 and len(assessment.processes) >= 20
    assert len(assessment.applications) + len(assessment.data_assets) >= 25
    assert len(assessment.infrastructure) >= 20 and len(assessment.security_capabilities) >= 12
    assert len(assessment.internal_players) >= 10 and len(assessment.third_parties) >= 8


def test_save_resume_version_backup_restore_and_integrity(tmp_path, assessment):
    assessment.id = "test-assessment"
    first = save_assessment(assessment, tmp_path)
    save_assessment(assessment, tmp_path)
    assert load_assessment(first).version == 2
    assert (tmp_path / assessment.id / "versions/v0001.json").exists()
    backup = backup_assessment(first)
    assert load_assessment(backup).id == assessment.id and len(integrity_digest(first)) == 64


def test_duplicate_archive_and_confirmed_delete(tmp_path, assessment):
    copy = duplicate_assessment(assessment, "copy-assessment")
    path = save_assessment(copy, tmp_path)
    with pytest.raises(ValueError):
        delete_draft(path, False)
    delete_draft(path, True)
    assert not path.exists()


def test_schema_migration_and_import(assessment):
    data = assessment.model_dump(mode="json")
    data["schema_version"] = "0.9.0"
    data.pop("current_step")
    imported = import_assessment(json.dumps(data).encode())
    assert imported.schema_version == "1.0.0" and imported.current_step == 1


def test_bulk_import_and_duplicate_rejection():
    assert bulk_csv_rows("id,name\na,One\n", {"id", "name"})[0]["id"] == "a"
    with pytest.raises(ValueError):
        bulk_csv_rows("id,name\na,One\na,Two\n", {"id", "name"})


def test_invalid_identifier_and_duplicate_records(assessment):
    payload = assessment.services[0].model_dump()
    payload["id"] = "INVALID ID"
    with pytest.raises(ValidationError):
        CriticalService.model_validate(payload)
    duplicate = assessment.model_dump()
    duplicate["services"].append(duplicate["services"][0])
    with pytest.raises(ValidationError):
        Assessment.model_validate(duplicate)


def test_high_impact_requires_rationale():
    with pytest.raises(ValidationError):
        ImpactProfile(service_id="svc-01", horizon="24 hours", dimensions={"customer_harm": 4})


def test_tolerance_conflicts_and_missing_owners(assessment):
    assert any("not been approved" in issue for issue in tolerance_conflicts(assessment))
    changed = assessment.model_copy(deep=True)
    changed.services[0].owner = "Unknown"
    assert completeness(changed)["Ownership"] < 100


def test_branching_rules_are_explicit():
    assert {
        "no_manual_workaround",
        "third_party_support",
        "production_identity_recovery",
        "payment_service",
        "unclear_authoritative_data",
        "deployed_untested_tool",
        "shared_dependency",
    } <= BRANCHING_RULES.keys()


def test_dependency_and_tier0_rules(assessment):
    endpoints = {
        r.id for r in assessment.services + assessment.infrastructure + assessment.control_planes
    }
    assert all(
        r.source in endpoints and r.destination in endpoints for r in assessment.relationships
    )
    candidates = generate_tier0_candidates(assessment)
    assert len(candidates) >= 8 and all(c.reviewer_decision == "Pending" for c in candidates)


def test_concentration_evidence_gaps_and_recovery_independence(assessment):
    findings, gaps = generate_analysis(assessment)
    assert any("concentration" in f.condition.lower() for f in findings)
    assert any("Recovery depends" in f.condition for f in findings)
    assert len(assessment.evidence_gaps) >= 6 and all(g.missing_evidence for g in gaps)


def test_raci_conflicts(assessment):
    changed = assessment.model_copy(deep=True)
    changed.responsibilities[0].accountable = []
    changed.responsibilities[1].alternate = "Unknown"
    issues = raci_conflicts(changed)
    assert any("no accountable" in x for x in issues) and any(
        "missing alternate" in x for x in issues
    )


def test_completeness_has_separate_dimensions(assessment):
    result = completeness(assessment)
    assert set(result) == {"Data entry", "Ownership", "Evidence", "Approval", "Testing"}
    assert len(set(result.values())) > 1


def test_report_and_pdf_generation(tmp_path, assessment):
    report = board_packet_markdown(assessment)
    assert (
        SYNTHETIC_NOTICE in report
        and "## Evidence limitations" in report
        and "universal" not in report.lower()
    )
    target = tmp_path / "packet.pdf"
    write_pdf(report, target)
    assert target.read_bytes().startswith(b"%PDF") and target.stat().st_size > 1000


def test_private_data_git_exclusion_and_synthetic_labeling(assessment):
    assert "data/private_assessments/" in Path(".gitignore").read_text()
    assert "Harbor Ridge" in assessment.organization.name and "SYN-EV" in DEMO.read_text()


def test_templates_and_accessibility_fallback():
    assert len(list(Path("templates/assessment").glob("*.csv"))) == 12
    ui = Path("src/harbor_resilience/assessment_ui.py").read_text()
    assert "Tabular accessibility fallback" in ui and "keyboard accessible" in ui
