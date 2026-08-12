from pathlib import Path

import pytest
from pydantic import ValidationError

from harbor_resilience import SYNTHETIC_LABEL
from harbor_resilience.data import load_services, load_tier0
from harbor_resilience.engine import (
    assess_tier_zero,
    concentration_risks,
    impact_status,
    validate_transition,
    validate_unique_ids,
)
from harbor_resilience.exercise import PHASES
from harbor_resilience.models import CriticalService, Decision, ImpactTolerance, TierZeroCandidate
from harbor_resilience.reporting import SECTIONS, after_action_markdown, board_markdown, write_pdf


def test_critical_service_model_and_tolerances():
    services = load_services(); assert len(services) == 16; validate_unique_ids(services)
    assert all(x.owner and x.dependencies for x in services)
    with pytest.raises(ValidationError): ImpactTolerance(mtd_minutes=30, rto_minutes=60, rpo_minutes=0, minimum_service_pct=50, max_data_uncertainty_minutes=0, max_backlog=0, customer_harm_threshold="x", financial_loss_threshold_usd=1, liquidity_consequence="x", regulatory_consequence="x", manual_workaround_minutes=0)


def test_tier0_rules_and_human_review():
    items = load_tier0(); validate_unique_ids(items)
    qualified, reasons = assess_tier_zero(items[0]); assert qualified and reasons and items[0].approved is True
    monitoring = next(x for x in items if x.id == "T0-11")
    assert assess_tier_zero(monitoring)[0] and monitoring.approved is False


def test_dependency_mapping_and_concentration():
    risks = concentration_risks(load_services())
    assert "enterprise-identity" in risks and len(risks["enterprise-identity"]) > 5


def test_impact_tolerance_calculation_and_defined_rag():
    service = load_services()[0]
    assert impact_status(30, service)["rag"] == "Green"
    assert impact_status(100, service)["rag"] == "Amber"
    assert impact_status(121, service)["rag"] == "Red"
    assert impact_status(0, service, backlog=10001)["breached"]


def test_inject_sequence_and_transitions():
    assert [x[0] for x in PHASES] == list(range(6)); assert sum(len(x[2]) for x in PHASES) == 30
    validate_transition(0, 1)
    with pytest.raises(ValueError): validate_transition(1, 3)


def test_decision_logging():
    d = Decision(phase=4, decision="Isolate identity", owner="CIO", chosen_action="Isolate", residual_risk="Payments delayed")
    assert d.phase == 4


def test_duplicate_missing_owner_and_evidence():
    item = load_services()[0]
    with pytest.raises(ValueError): validate_unique_ids([item, item])
    with pytest.raises(ValidationError): CriticalService(id="x", name="x", owner="", tolerance=item.tolerance, dependencies=[])
    with pytest.raises(ValidationError): TierZeroCandidate(id="x", name="x", type="x", business_owner="x", technical_owner="x", critical_services=[], evidence=[])


def test_reports_complete_and_synthetic(tmp_path):
    services, tier0 = load_services(), load_tier0()
    md = board_markdown(services, tier0, [])
    assert all(f"## {section}" in md for section in SECTIONS)
    assert SYNTHETIC_LABEL in md and "No performance result" not in md
    aar = after_action_markdown([], []); assert "No decisions recorded" in aar and SYNTHETIC_LABEL in aar
    target = tmp_path / "packet.pdf"; write_pdf(md, target); assert target.exists() and target.stat().st_size > 2000


def test_all_data_files_are_synthetic_labeled():
    root = Path(__file__).resolve().parents[1]
    for path in list((root / "data").rglob("*.yaml")) + list((root / "templates").glob("*.csv")):
        assert "SYNTHETIC EXERCISE DATA" in path.read_text(encoding="utf-8"), path
