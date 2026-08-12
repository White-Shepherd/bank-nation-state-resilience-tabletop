from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import ValidationError

from .assessment_models import Assessment, EvidenceGap, Finding, Organization, Tier0Candidate

SYNTHETIC_NOTICE = "SYNTHETIC DEMONSTRATION DATA - NOT A REAL BANK ASSESSMENT"
SCHEMA_VERSION = "1.0.0"
PRIVATE_ROOT = Path("data/private_assessments")
SYNTHETIC_ROOT = Path("data/synthetic_assessments")

STEPS = [
    "Organization profile",
    "Critical-service identification",
    "Impact assessment",
    "Impact tolerances",
    "Business-process mapping",
    "Application and data mapping",
    "Infrastructure and control-plane mapping",
    "People and decision authority",
    "Third-party dependencies",
    "Security-capability coverage",
    "Manual-workaround assessment",
    "Recovery assessment",
    "Tier 0 candidate analysis",
    "Gap and concentration analysis",
    "Scenario recommendation",
    "Review and approval",
]

BRANCHING_RULES = {
    "no_manual_workaround": "Skip workaround detail and create an evidence-based resilience gap.",
    "third_party_support": "Request provider, access, recovery, contract and substitution evidence.",
    "production_identity_recovery": "Trigger recovery-independence review.",
    "payment_service": "Request settlement, payment and liquidity tolerances.",
    "unclear_authoritative_data": "Create a data-authority evidence gap.",
    "deployed_untested_tool": "Request validation evidence; do not credit effective coverage.",
    "shared_dependency": "Trigger concentration review when multiple services are supported.",
}


def new_assessment(identifier: str, title: str, organization_name: str) -> Assessment:
    today = datetime.now(timezone.utc).date()
    return Assessment(
        id=identifier,
        version=1,
        title=title,
        organization=Organization(
            name=organization_name,
            industry="Unknown",
            size="Unknown",
            geographic_footprint="Unknown",
            customer_types=[],
            products_services=[],
            legal_entities=[],
            primary_regulators=[],
            operating_model="Requires review",
            technology_model="Requires review",
            outsourcing_model="Requires review",
            assessment_owner="Unknown",
            executive_sponsor="Unknown",
            assessment_date=today,
            review_date=today + timedelta(days=180),
            classification="Internal",
        ),
    )


def load_assessment(path: Path) -> Assessment:
    return Assessment.model_validate_json(path.read_text(encoding="utf-8"))


def save_assessment(assessment: Assessment, root: Path = PRIVATE_ROOT) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    assessment.updated_at = datetime.now(timezone.utc)
    target = root / f"{assessment.id}.json"
    if target.exists():
        history = root / assessment.id / "versions"
        history.mkdir(parents=True, exist_ok=True)
        prior = load_assessment(target)
        shutil.copy2(target, history / f"v{prior.version:04d}.json")
        assessment.version = prior.version + 1
    payload = assessment.model_dump_json(indent=2)
    handle, temporary = tempfile.mkstemp(prefix=f".{assessment.id}-", suffix=".tmp", dir=root)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        Assessment.model_validate_json(Path(temporary).read_text(encoding="utf-8"))
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return target


COLLECTION_MODELS = {
    "services": "CriticalService",
    "impacts": "ImpactProfile",
    "tolerances": "ImpactTolerance",
    "processes": "BusinessProcess",
    "applications": "Application",
    "data_assets": "DataAsset",
    "infrastructure": "InfrastructureDependency",
    "control_planes": "ControlPlane",
    "security_capabilities": "SecurityCapability",
    "internal_players": "InternalPlayer",
    "third_parties": "ThirdParty",
    "workarounds": "ManualWorkaround",
    "recovery_capabilities": "RecoveryCapability",
    "evidence_items": "EvidenceItem",
    "relationships": "Relationship",
    "approvals": "Approval",
}


def record_id(record) -> str:
    return getattr(record, "id", "")


def upsert_record(assessment: Assessment, collection: str, payload: dict) -> Assessment:
    if collection not in COLLECTION_MODELS:
        raise ValueError("unsupported assessment collection")
    from . import assessment_models

    model = getattr(assessment_models, COLLECTION_MODELS[collection])
    record = model.model_validate(payload)
    if collection == "approvals" and getattr(record, "status", "") == "Approved":
        blockers = approval_blockers(assessment)
        if blockers:
            raise ValueError("approval blocked: " + "; ".join(blockers))
    records = list(getattr(assessment, collection))
    match = next(
        (i for i, item in enumerate(records) if record_id(item) == record_id(record)), None
    )
    if match is None:
        records.append(record)
    else:
        records[match] = record
    updated = assessment.model_copy(update={collection: records}, deep=True)
    validate_references(updated)
    return updated


def duplicate_record(
    assessment: Assessment, collection: str, source_id: str, new_id: str
) -> Assessment:
    source = next((x for x in getattr(assessment, collection) if record_id(x) == source_id), None)
    if source is None:
        raise ValueError(f"record not found: {source_id}")
    payload = source.model_dump()
    payload["id"] = new_id
    payload["archived"] = False
    if "name" in payload:
        payload["name"] = f"Copy of {payload['name']}"
    return upsert_record(assessment, collection, payload)


def archive_record(assessment: Assessment, collection: str, identifier: str) -> Assessment:
    records = list(getattr(assessment, collection))
    found = False
    for i, item in enumerate(records):
        if record_id(item) == identifier:
            records[i] = item.model_copy(update={"archived": True})
            found = True
    if not found:
        raise ValueError(f"record not found: {identifier}")
    return assessment.model_copy(update={collection: records}, deep=True)


def delete_record(
    assessment: Assessment, collection: str, identifier: str, confirmed: bool
) -> Assessment:
    if not confirmed:
        raise ValueError("explicit confirmation required")
    referenced = [
        r.id
        for r in assessment.relationships
        if not r.archived and identifier in {r.source, r.destination}
    ]
    if referenced and collection != "relationships":
        raise ValueError(f"record is referenced by relationships: {', '.join(referenced)}")
    records = [x for x in getattr(assessment, collection) if record_id(x) != identifier]
    if len(records) == len(getattr(assessment, collection)):
        raise ValueError(f"record not found: {identifier}")
    return assessment.model_copy(update={collection: records}, deep=True)


def all_record_ids(assessment: Assessment) -> set[str]:
    ids = {assessment.id}
    for collection in COLLECTION_MODELS:
        ids.update(record_id(x) for x in getattr(assessment, collection) if record_id(x))
    return ids


def validate_references(assessment: Assessment) -> None:
    endpoints = all_record_ids(assessment)
    errors = []
    for relationship in assessment.relationships:
        if relationship.source not in endpoints:
            errors.append(f"{relationship.id}.source: unknown record {relationship.source}")
        if relationship.destination not in endpoints:
            errors.append(
                f"{relationship.id}.destination: unknown record {relationship.destination}"
            )
    service_ids = {x.id for x in assessment.services}
    for process in assessment.processes:
        for value in process.service_ids:
            if value not in service_ids:
                errors.append(f"{process.id}.service_ids: unknown service {value}")
    if errors:
        raise ValueError("; ".join(errors))


def approval_blockers(assessment: Assessment) -> list[str]:
    blockers = tolerance_conflicts(assessment)
    blockers.extend(
        f"{service.id}: missing business owner"
        for service in assessment.services
        if service.owner in {"", "Unknown"}
    )
    try:
        validate_references(assessment)
    except ValueError as exc:
        blockers.append(str(exc))
    return blockers


def field_errors(model, payload: dict) -> dict[str, str]:
    try:
        model.model_validate(payload)
        return {}
    except ValidationError as exc:
        return {
            ".".join(
                str(x) for x in error["loc"]
            ): f"{error['msg']}. Correct this field or retain the record as an incomplete draft."
            for error in exc.errors()
        }


def duplicate_assessment(assessment: Assessment, new_id: str) -> Assessment:
    data = assessment.model_dump()
    data.update(id=new_id, version=1, title=f"Copy of {assessment.title}", status="Draft")
    return Assessment.model_validate(data)


def archive_assessment(assessment: Assessment) -> Assessment:
    return assessment.model_copy(update={"status": "Archived"})


def delete_draft(path: Path, confirmed: bool) -> None:
    if not confirmed:
        raise ValueError("explicit confirmation required")
    assessment = load_assessment(path)
    if assessment.status != "Draft":
        raise ValueError("only local drafts can be deleted")
    path.unlink()


def backup_assessment(path: Path) -> Path:
    target = path.with_suffix(".backup.json")
    shutil.copy2(path, target)
    return target


def integrity_digest(path: Path) -> str:
    load_assessment(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migrate_payload(payload: dict) -> dict:
    version = payload.get("schema_version", "0.9.0")
    if version == SCHEMA_VERSION:
        return payload
    migrated = dict(payload)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated.setdefault("current_step", 1)
    migrated.setdefault("evidence_gaps", [])
    return migrated


def import_assessment(content: bytes) -> Assessment:
    return Assessment.model_validate(migrate_payload(json.loads(content)))


def tolerance_conflicts(assessment: Assessment) -> list[str]:
    conflicts: list[str] = []
    for item in assessment.tolerances:
        if item.rto_minutes > item.mtd_minutes:
            conflicts.append(f"{item.service_id}: RTO exceeds maximum tolerable disruption")
        if item.manual_workaround_minutes and item.manual_workaround_minutes < item.rto_minutes:
            conflicts.append(f"{item.service_id}: workaround duration is shorter than RTO")
        if item.rpo_minutes > item.data_uncertainty_minutes:
            conflicts.append(f"{item.service_id}: RPO exceeds data uncertainty tolerance")
        if not item.minimum_viable_service.strip():
            conflicts.append(f"{item.service_id}: minimum viable service is undefined")
        if item.accountable_owner in {"", "Unknown"}:
            conflicts.append(f"{item.service_id}: tolerance lacks accountable owner")
        if not item.approved:
            conflicts.append(f"{item.service_id}: tolerance has not been approved")
        if not item.tested:
            conflicts.append(f"{item.service_id}: tolerance has not been tested")
    return conflicts


def raci_conflicts(assessment: Assessment) -> list[str]:
    issues = []
    for row in assessment.responsibilities:
        if not row.accountable:
            issues.append(f"{row.activity}: no accountable owner")
        if len(row.accountable) > 1:
            issues.append(f"{row.activity}: conflicting accountable owners")
        if row.alternate in {"", "Unknown"}:
            issues.append(f"{row.activity}: missing alternate")
    return issues


def generate_tier0_candidates(assessment: Assessment) -> list[Tier0Candidate]:
    candidates = []
    for dep in assessment.infrastructure + assessment.control_planes:
        rules = []
        if len(dep.service_ids) > 1:
            rules.append("supports-multiple-critical-services")
        if dep.administrative_authority.lower() not in {"none", "limited", "unknown"}:
            rules.append("broad-administrative-authority")
        if dep.type.lower() in {
            "identity",
            "directory",
            "privileged access",
            "network management",
            "cloud management",
        }:
            rules.append("control-plane-authority")
        if dep.recovery_dependency:
            rules.append("trustworthy-recovery-dependency")
        if dep.alternate in {"", "Unknown", "None"}:
            rules.append("no-practical-substitute")
        if not rules:
            continue
        candidates.append(
            Tier0Candidate(
                id=f"t0-{dep.id}",
                dependency_id=dep.id,
                service_ids=dep.service_ids,
                triggered_rules=rules,
                evidence=dep.evidence,
                missing_evidence=[] if dep.evidence else ["Reviewer evidence required"],
                concentration_risk=dep.failure_consequence,
                recovery_dependency=dep.recovery_dependency,
                preliminary_rationale="; ".join(rules),
                arguments_against="Alternate or scope evidence may reduce classification; reviewer judgment required.",
            )
        )
    return candidates


def generate_analysis(assessment: Assessment) -> tuple[list[Finding], list[EvidenceGap]]:
    findings, gaps = [], []

    def finding(
        fid: str, condition: str, services: list[str], evidence: list[str], recommendation: str
    ):
        if evidence:
            findings.append(
                Finding(
                    id=fid,
                    condition=condition,
                    service_ids=services,
                    evidence=evidence,
                    confidence="Confirmed",
                    consequence="Disruption or compromise may exceed a service tolerance.",
                    recommendation=recommendation,
                    owner="Chief Risk Officer",
                    priority="High",
                    validation_method="Owner review and resilience exercise",
                    residual_uncertainty="Exercise outcome pending",
                )
            )
        else:
            gaps.append(
                EvidenceGap(
                    id=f"eg-{fid}",
                    subject_id=services[0] if services else assessment.id,
                    missing_evidence=condition,
                    consequence="Risk cannot be concluded without evidence.",
                    owner="Assessment Owner",
                )
            )

    for dep in assessment.infrastructure:
        if len(dep.service_ids) > 1:
            finding(
                f"f-{dep.id}",
                f"Shared {dep.type} concentration",
                dep.service_ids,
                dep.evidence,
                "Validate separation and an alternate capability.",
            )
        if dep.recovery_dependency and not dep.separated_from_production:
            finding(
                f"f-recovery-{dep.id}",
                "Recovery depends on production control",
                dep.service_ids,
                dep.evidence,
                "Establish and test independent recovery control.",
            )
        if "untested" in dep.monitoring_coverage.lower():
            gaps.append(
                EvidenceGap(
                    id=f"eg-monitoring-{dep.id}",
                    subject_id=dep.id,
                    missing_evidence="Monitoring detection has not been tested",
                    consequence="Deployed tooling cannot be credited as effective coverage.",
                    owner=dep.owner,
                )
            )
    for party in assessment.third_parties:
        if len(party.service_ids) > 1 and party.alternate_provider in {"Unknown", "None"}:
            finding(
                f"f-{party.id}",
                "Third-party concentration without substitution",
                party.service_ids,
                party.evidence,
                "Test exit, substitution, or manual continuity.",
            )
    for workaround in assessment.workarounds:
        if not workaround.exists or workaround.last_test in {"Unknown", "Never"}:
            finding(
                f"f-{workaround.id}",
                "Manual workaround absent or untested",
                [workaround.service_id],
                workaround.evidence,
                "Exercise the minimum viable manual service and reconciliation.",
            )
    for asset in assessment.data_assets:
        if asset.authority == "Unknown":
            gaps.append(
                EvidenceGap(
                    id=f"eg-{asset.id}",
                    subject_id=asset.id,
                    missing_evidence="Authoritative-data status is unclear",
                    consequence="Recovery point and integrity cannot be approved.",
                    owner=asset.owner,
                )
            )
    return findings, gaps


def completeness(assessment: Assessment) -> dict[str, int]:
    services = max(1, len(assessment.services))
    owned = sum(
        s.owner != "Unknown" and s.technical_owner != "Unknown" for s in assessment.services
    )
    evidenced_records = (
        assessment.services
        + assessment.processes
        + assessment.applications
        + assessment.data_assets
        + assessment.infrastructure
    )
    approvals = sum(a.status == "Approved" for a in assessment.approvals)
    tested = sum(t.tested for t in assessment.tolerances) + sum(
        r.status in {"restore-tested", "data-validated", "service-within-tolerance"}
        for r in assessment.recovery_capabilities
    )
    return {
        "Data entry": min(100, round(100 * len(assessment.tolerances) / services)),
        "Ownership": round(100 * owned / services),
        "Evidence": round(
            100 * sum(bool(r.evidence) for r in evidenced_records) / max(1, len(evidenced_records))
        ),
        "Approval": round(100 * approvals / max(1, len(assessment.approvals))),
        "Testing": round(
            100
            * tested
            / max(1, len(assessment.tolerances) + len(assessment.recovery_capabilities))
        ),
    }


def board_packet_markdown(assessment: Assessment) -> str:
    sections = [
        (
            "Executive summary",
            f"{assessment.title} identifies {len(assessment.services)} critical services. Automated analysis recommends candidates and findings for accountable human review; it does not replace business, risk, legal, compliance, audit, or board judgment.",
        ),
        (
            "Assessment scope",
            f"{assessment.organization.name}; {assessment.organization.industry}; classification: {assessment.organization.classification}.",
        ),
        ("Critical services", "\n".join(f"- {s.name}: {s.rationale}" for s in assessment.services)),
        (
            "Approved impact tolerances",
            "\n".join(
                f"- {t.service_id}: MTD {t.mtd_minutes}m; RTO {t.rto_minutes}m; RPO {t.rpo_minutes}m; approved={t.approved}"
                for t in assessment.tolerances
            ),
        ),
        (
            "Tier 0 candidates",
            "\n".join(
                f"- {c.dependency_id}: {', '.join(c.triggered_rules)}; decision={c.reviewer_decision}"
                for c in assessment.tier0_candidates
            ),
        ),
        (
            "Material concentrations",
            "\n".join(
                f"- {f.condition}"
                for f in assessment.findings
                if "concentration" in f.condition.lower()
            ),
        ),
        (
            "Recovery-readiness findings",
            "\n".join(
                f"- {f.condition}"
                for f in assessment.findings
                if "recovery" in f.condition.lower() or "workaround" in f.condition.lower()
            ),
        ),
        (
            "Third-party dependencies",
            "\n".join(
                f"- {p.name}: {p.service_provided}; recovery evidence: {p.tested_recovery}"
                for p in assessment.third_parties
            ),
        ),
        (
            "Security-coverage gaps",
            "\n".join(
                f"- {c.name}: maturity {c.maturity}/8; limitation: {c.limitation}"
                for c in assessment.security_capabilities
                if c.maturity < 6
            ),
        ),
        (
            "Manual-workaround limitations",
            "\n".join(
                f"- {w.name}: throughput {w.throughput_pct}%; test: {w.test_result}"
                for w in assessment.workarounds
            ),
        ),
        (
            "Recommended tabletop scenarios",
            "\n".join(f"- {s.name}: {s.reason}" for s in assessment.scenarios),
        ),
        (
            "Corrective-action roadmap",
            "\n".join(
                f"- [{a.priority}] {a.action} ({a.owner})" for a in assessment.corrective_actions
            ),
        ),
        (
            "Decisions required",
            "\n".join(
                f"- Review {c.dependency_id} Tier 0 classification"
                for c in assessment.tier0_candidates
                if c.reviewer_decision == "Pending"
            ),
        ),
        (
            "Residual uncertainties",
            "\n".join(f"- {f.residual_uncertainty}" for f in assessment.findings),
        ),
        (
            "Evidence limitations",
            "\n".join(f"- {g.subject_id}: {g.missing_evidence}" for g in assessment.evidence_gaps),
        ),
    ]
    return f"# {SYNTHETIC_NOTICE}\n\n# Board assessment packet\n\n" + "\n\n".join(
        f"## {h}\n\n{b or 'No supported conclusion; review required.'}" for h, b in sections
    )


def responsibility_csv(assessment: Assessment) -> str:
    out = io.StringIO()
    fields = [
        "synthetic_label",
        "activity",
        "responsible",
        "accountable",
        "consulted",
        "informed",
        "deadline",
        "escalation_authority",
        "alternate",
    ]
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    for row in assessment.responsibilities:
        data = row.model_dump()
        data = {k: "; ".join(v) if isinstance(v, list) else v for k, v in data.items()}
        writer.writerow({"synthetic_label": SYNTHETIC_NOTICE, **data})
    return out.getvalue()


def bulk_csv_rows(content: str, required: set[str]) -> list[dict[str, str]]:
    rows = list(csv.DictReader(io.StringIO(content)))
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"missing required CSV fields: {sorted(required)}")
    identifiers = [row.get("id") or row.get("service_id") for row in rows]
    if any(not value for value in identifiers) or len(identifiers) != len(set(identifiers)):
        raise ValueError("missing or duplicate CSV identifier")
    return rows
