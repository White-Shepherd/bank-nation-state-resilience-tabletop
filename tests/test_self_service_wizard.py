import json
from pathlib import Path

import pytest

from harbor_resilience.assessment import (
    archive_record,
    delete_record,
    duplicate_record,
    load_assessment,
    new_assessment,
    save_assessment,
    upsert_record,
)
from harbor_resilience.assessment_import import TEMPLATE_SPECS, import_valid_rows, validate_csv
from harbor_resilience.record_editor import EDITOR_COLLECTIONS, is_unsaved


def service(identifier: str, name: str = "Test service") -> dict:
    return {
        "id": identifier,
        "name": name,
        "owner": "Unknown",
        "evidence": [],
        "confidence": "Requires review",
        "description": "Outcome delivered to a stakeholder",
        "stakeholders": ["Customer"],
        "technical_owner": "Unknown",
        "operating_entities": [],
        "geography": "Unknown",
        "operating_hours": "Unknown",
        "volume": "Unknown",
        "revenue_relationship": "Unknown",
        "payment_obligation": False,
        "harm_potential": "Requires review",
        "regulatory_significance": "Requires review",
        "rationale": "Requires owner review",
        "archived": False,
    }


def test_every_required_editor_is_registered():
    assert len(EDITOR_COLLECTIONS) == 16
    assert {
        "services",
        "impacts",
        "tolerances",
        "processes",
        "applications",
        "data_assets",
        "infrastructure",
        "control_planes",
        "security_capabilities",
        "internal_players",
        "third_parties",
        "workarounds",
        "recovery_capabilities",
        "evidence_items",
        "relationships",
        "approvals",
    } == set(EDITOR_COLLECTIONS.values())


def test_crud_duplicate_archive_and_confirmed_delete():
    assessment = new_assessment("crud-test", "CRUD", "Synthetic Org")
    assessment = upsert_record(assessment, "services", service("svc-one"))
    assessment = upsert_record(assessment, "services", service("svc-one", "Edited service"))
    assert assessment.services[0].name == "Edited service"
    assessment = duplicate_record(assessment, "services", "svc-one", "svc-two")
    assert len(assessment.services) == 2
    assessment = archive_record(assessment, "services", "svc-two")
    assert assessment.services[1].archived
    with pytest.raises(ValueError, match="confirmation"):
        delete_record(assessment, "services", "svc-two", False)
    assessment = delete_record(assessment, "services", "svc-two", True)
    assert [x.id for x in assessment.services] == ["svc-one"]


def test_invalid_relationship_is_rejected():
    assessment = new_assessment("relations", "Relationships", "Synthetic Org")
    assessment = upsert_record(assessment, "services", service("svc-one"))
    bad = {
        "id": "rel-one",
        "source": "svc-one",
        "destination": "missing",
        "relationship_type": "depends_on",
        "evidence": "Evidence unavailable",
        "confidence": "Requires review",
    }
    with pytest.raises(ValueError, match="unknown record"):
        upsert_record(assessment, "relationships", bad)


def test_atomic_write_failure_preserves_prior_file(tmp_path, monkeypatch):
    assessment = new_assessment("atomic-test", "Before", "Synthetic Org")
    path = save_assessment(assessment, tmp_path)
    before = path.read_bytes()
    assessment.title = "After"
    monkeypatch.setattr(
        "harbor_resilience.assessment.os.replace",
        lambda *_: (_ for _ in ()).throw(OSError("interrupted")),
    )
    with pytest.raises(OSError, match="interrupted"):
        save_assessment(assessment, tmp_path)
    assert path.read_bytes() == before


def test_restart_and_resume_uses_durable_file(tmp_path):
    assessment = new_assessment("resume-test", "Resume", "Synthetic Org")
    assessment = upsert_record(assessment, "services", service("svc-one"))
    path = save_assessment(assessment, tmp_path)
    del assessment
    resumed = load_assessment(path)
    assert resumed.services[0].id == "svc-one" and resumed.title == "Resume"


def test_version_history_after_record_submit(tmp_path):
    assessment = new_assessment("history-test", "History", "Synthetic Org")
    path = save_assessment(assessment, tmp_path)
    assessment = upsert_record(assessment, "services", service("svc-one"))
    save_assessment(assessment, tmp_path)
    assert load_assessment(path).version == 2
    assert (tmp_path / "history-test/versions/v0001.json").exists()


def test_all_template_imports_have_validation_workflows():
    assert len(TEMPLATE_SPECS) == 12
    assert all(Path(f"templates/assessment/{name}.csv").exists() for name in TEMPLATE_SPECS)


def test_csv_valid_invalid_preview_duplicate_and_reference_validation():
    assessment = new_assessment("import-test", "Import", "Synthetic Org")
    assessment = upsert_record(assessment, "services", service("svc-one"))
    content = "id,name,service_ids,owner,trigger,inputs,outputs,operating_window,manual_alternative,evidence\nproc-one,One,svc-one,Owner,T,I,O,24x7,None,EV-1\nproc-two,Two,missing,Owner,T,I,O,24x7,None,EV-2\nproc-one,Duplicate,svc-one,Owner,T,I,O,24x7,None,EV-3\n"
    valid, errors = validate_csv("business-processes", content, assessment)
    assert len(valid) == 1
    assert any("Unknown relationship" in x["error"] for x in errors)
    assert any("Duplicate identifier" in x["error"] for x in errors)


def test_import_confirmation_and_rollback_semantics():
    assessment = new_assessment("rollback-test", "Rollback", "Synthetic Org")
    before = assessment.model_dump_json()
    with pytest.raises(ValueError, match="confirmation"):
        import_valid_rows(assessment, "critical-services", [{"id": "svc-one"}], False)
    assert assessment.model_dump_json() == before
    imported = import_valid_rows(
        assessment, "critical-services", [{"id": "svc-one", "name": "One"}], True
    )
    assert imported.incomplete_records["critical-services"][0]["id"] == "svc-one"


def test_unsaved_state_is_semantic_and_survives_rerun_payload():
    original = json.dumps({"id": "svc-one", "name": "One"}, indent=2)
    reformatted = '{"name":"One", "id":"svc-one"}'
    changed = '{"name":"Two", "id":"svc-one"}'
    assert not is_unsaved(reformatted, original)
    assert is_unsaved(changed, original)


def test_telemetry_configuration_is_narrow_and_supported():
    config = Path(".streamlit/config.toml").read_text()
    assert "gatherUsageStats = false" in config
    assert "permission" not in config.lower()
