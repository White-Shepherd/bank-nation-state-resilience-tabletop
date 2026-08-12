from __future__ import annotations

from collections import Counter

from .models import CriticalService, TierZeroCandidate


def assess_tier_zero(candidate: TierZeroCandidate) -> tuple[bool, list[str]]:
    reasons = []
    if len(candidate.critical_services) >= 2:
        reasons.append("loss or corruption could stop multiple critical services")
    if candidate.broad_admin:
        reasons.append("grants broad administrative control")
    if candidate.recovery_dependency:
        reasons.append("required for trusted recovery")
    if candidate.integrity_critical:
        reasons.append("required for trustworthy financial reconciliation")
    return bool(reasons), reasons


def concentration_risks(services: list[CriticalService]) -> dict[str, list[str]]:
    counts = Counter(dep for service in services for dep in service.dependencies)
    return {
        dep: [service.id for service in services if dep in service.dependencies]
        for dep, count in counts.items()
        if count >= 2
    }


def impact_status(elapsed: int, service: CriticalService, backlog: int = 0,
                  uncertainty: int = 0) -> dict[str, object]:
    t = service.tolerance
    consumed = min(100, round(elapsed / t.mtd_minutes * 100))
    breached = elapsed > t.mtd_minutes or backlog > t.max_backlog or uncertainty > t.max_data_uncertainty_minutes
    if breached:
        rag = "Red"
    elif consumed >= 75:
        rag = "Amber"
    else:
        rag = "Green"
    return {"consumed_pct": consumed, "breached": breached, "rag": rag}


def validate_unique_ids(items) -> None:
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate identifiers")
    for item in items:
        owner = getattr(item, "owner", None) or getattr(item, "business_owner", None)
        if not owner:
            raise ValueError(f"missing owner: {item.id}")
        if hasattr(item, "evidence") and not item.evidence:
            raise ValueError(f"missing evidence: {item.id}")


def validate_transition(current: int, requested: int) -> None:
    if requested not in {current, current + 1} or requested > 5:
        raise ValueError("invalid scenario transition")

