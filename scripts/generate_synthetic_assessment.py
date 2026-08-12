from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harbor_resilience.assessment import generate_analysis, generate_tier0_candidates
from harbor_resilience.assessment_models import (
    Application,
    Approval,
    Assessment,
    BusinessProcess,
    ControlPlane,
    CorrectiveAction,
    CriticalService,
    DataAsset,
    EvidenceGap,
    ImpactProfile,
    ImpactTolerance,
    InfrastructureDependency,
    InternalPlayer,
    ManualWorkaround,
    Organization,
    RecoveryCapability,
    Relationship,
    Responsibility,
    ScenarioRecommendation,
    SecurityCapability,
    ThirdParty,
)

SERVICE_NAMES = [
    "Customer authentication",
    "Account inquiry",
    "Core deposit processing",
    "ACH",
    "Wire transfers",
    "Card authorization",
    "Card settlement",
    "ATM withdrawals",
    "Treasury management",
    "Fraud monitoring",
    "Liquidity reporting",
    "Regulatory reporting",
]
PROCESS_NAMES = [
    "Customer verification",
    "Account lookup",
    "Deposit posting",
    "Payment initiation",
    "Payment approval",
    "Sanctions screening",
    "Fraud review",
    "Transaction posting",
    "End-of-day reconciliation",
    "Liquidity calculation",
    "Exception handling",
    "Manual payment processing",
    "Customer notification",
    "Incident escalation",
    "Recovery authorization",
    "Card authorization routing",
    "ATM cash approval",
    "Treasury file intake",
    "Regulatory data aggregation",
    "Ledger validation",
]
APP_NAMES = [
    "Online banking application",
    "Mobile banking application",
    "Core banking platform",
    "Payment gateway",
    "ACH processing platform",
    "Wire-transfer platform",
    "Card-management platform",
    "Fraud analytics",
    "Customer identity platform",
    "General ledger",
    "Customer communications platform",
    "Regulatory reporting platform",
    "API gateway",
]
DATA_NAMES = [
    "Customer identity register",
    "Customer account database",
    "Transaction journal",
    "Payment instruction store",
    "General-ledger records",
    "Reconciliation database",
    "Configuration repository",
    "Recovery-state catalog",
    "Liquidity warehouse",
    "Sanctions reference data",
    "Fraud case store",
    "Regulatory submission archive",
]
INFRA = [
    ("enterprise-identity", "Enterprise identity", "Identity"),
    ("directory", "Directory services", "Directory"),
    ("pam", "Privileged-access management", "Privileged access"),
    ("dns", "Domain Name System", "DNS"),
    ("time", "Time synchronization", "Time"),
    ("certificates", "Certificate and key management", "Certificates"),
    ("cloud-control", "Cloud-management plane", "Cloud management"),
    ("network-control", "Network-management plane", "Network management"),
    ("virtualization", "Virtualization management", "Virtualization"),
    ("database-control", "Database administration", "Database"),
    ("backup", "Backup platform", "Backup"),
    ("recovery", "Recovery orchestration", "Recovery"),
    ("telecom-a", "Primary telecommunications", "Telecommunications"),
    ("dc-primary", "Primary data center", "Data center"),
    ("cloud-region", "Synthetic cloud region", "Cloud region"),
    ("admin-endpoints", "Administrative endpoints", "Endpoint"),
    ("logging", "Logging infrastructure", "Logging"),
    ("security-console", "Security-management consoles", "Security"),
    ("clean-room", "Clean-room recovery environment", "Recovery"),
    ("offline-vault", "Offline recovery data vault", "Recovery"),
]


def record_kwargs(i: int) -> dict:
    return {
        "owner": ["Payments Operations", "Technology Operations", "Risk Management"][i % 3],
        "evidence": [f"SYN-EV-{i + 1:03d}"],
        "confidence": "Confirmed",
    }


def build() -> Assessment:
    org = Organization(
        name="Harbor Ridge Bank",
        industry="Fictional regional banking",
        size="$35B synthetic assets",
        geographic_footprint="Fictional multi-state U.S. footprint",
        customer_types=["Consumers", "Businesses"],
        products_services=SERVICE_NAMES,
        legal_entities=["Harbor Ridge Bank, N.A. (fictional)"],
        primary_regulators=["Jurisdiction-specific review required"],
        operating_model="Federated business ownership",
        technology_model="Hybrid synthetic environment",
        outsourcing_model="Selective managed services",
        assessment_owner="Chief Risk Officer",
        executive_sponsor="Chief Executive Officer",
        assessment_date=date(2026, 8, 12),
        review_date=date(2027, 2, 12),
        classification="Internal",
    )
    services = [
        CriticalService(
            id=f"svc-{i + 1:02d}",
            name=name,
            description=f"Delivers the {name.lower()} outcome.",
            stakeholders=["Customers", "Operations"],
            technical_owner="Chief Information Officer",
            operating_entities=["Harbor Ridge Bank, N.A. (fictional)"],
            geography="Synthetic U.S. footprint",
            operating_hours="24x7" if i < 9 else "Business day",
            volume=f"Synthetic band {i % 3 + 1}",
            revenue_relationship="Indirect customer relationship",
            payment_obligation=i in {3, 4, 5, 6, 7},
            harm_potential="Material after tolerance",
            regulatory_significance="Review with Legal and Compliance",
            manual_alternative="Documented constrained procedure" if i % 3 else "None",
            criticality="Critical",
            rationale="Outcome disruption can harm customers or market obligations.",
            **record_kwargs(i),
        )
        for i, name in enumerate(SERVICE_NAMES)
    ]
    tolerances = [
        ImpactTolerance(
            service_id=s.id,
            mtd_minutes=240 if i < 8 else 480,
            rto_minutes=120 if i < 8 else 240,
            rpo_minutes=15,
            minimum_viable_service="25% priority throughput",
            data_uncertainty_minutes=30,
            transaction_backlog=5000,
            manual_workaround_minutes=240,
            thresholds={
                "customer_harm": "500 delayed customers",
                "financial_loss": "Board-approved band",
                "payment": "One missed settlement",
                "liquidity": "Treasury escalation band",
                "escalation": "75% of MTD",
            },
            accountable_owner=s.owner,
            approved=i < 8,
            tested=i % 3 != 0,
        )
        for i, s in enumerate(services)
    ]
    horizons = ["15 minutes", "1 hour", "4 hours", "8 hours", "24 hours", "72 hours", "7 days"]
    impacts = [
        ImpactProfile(
            service_id=s.id,
            horizon=h,
            dimensions={
                d: min(5, 1 + j // 2 + i // 4)
                for d in [
                    "customer_harm",
                    "financial_loss",
                    "payment_settlement",
                    "liquidity",
                    "data_integrity",
                    "regulatory",
                    "legal",
                    "backlog",
                    "market",
                    "safety",
                    "strategic",
                ]
            },
            rationale="High impacts reflect synthetic prolonged disruption assumptions."
            if j >= 4
            else "Synthetic ordinal assessment.",
        )
        for i, s in enumerate(services)
        for j, h in enumerate(horizons)
    ]
    processes = [
        BusinessProcess(
            id=f"proc-{i + 1:02d}",
            name=name,
            description=f"Synthetic {name.lower()} process.",
            service_ids=[services[i % 12].id, services[(i + 4) % 12].id],
            trigger="Customer or scheduled event",
            inputs=["Validated instruction"],
            outputs=["Recorded outcome"],
            operating_window="Required service window",
            manual_alternative="Constrained procedure",
            max_backlog="5,000 items",
            recovery_priority=str(i % 4 + 1),
            **record_kwargs(i),
        )
        for i, name in enumerate(PROCESS_NAMES)
    ]
    apps = [
        Application(
            id=f"app-{i + 1:02d}",
            name=name,
            type="Application",
            description=f"Synthetic {name.lower()}.",
            operator="Application Operations",
            hosting_model="Hybrid",
            environments=["Production", "Recovery"],
            service_ids=[services[i % 12].id, services[(i + 3) % 12].id],
            process_ids=[processes[i % 20].id],
            authority="Derived",
            classification="Confidential",
            availability="Per service RTO",
            integrity="Reconciled",
            confidentiality="Restricted access",
            recovery_method="Clean restore and validation",
            last_recovery_test="2026-Q1 synthetic exercise",
            **record_kwargs(i),
        )
        for i, name in enumerate(APP_NAMES)
    ]
    data = [
        DataAsset(
            id=f"data-{i + 1:02d}",
            name=name,
            type="Data asset",
            description=f"Synthetic {name.lower()}.",
            operator="Data Operations",
            hosting_model="Hybrid",
            environments=["Production", "Recovery"],
            service_ids=[services[i % 12].id],
            process_ids=[processes[(i + 2) % 20].id],
            authority="Authoritative" if i < 8 else ("Unknown" if i in {9, 11} else "Derived"),
            classification="Restricted",
            availability="Per service RTO",
            integrity="Authoritative reconciliation required",
            confidentiality="Restricted access",
            recovery_method="Validated immutable snapshot",
            last_recovery_test="2026-Q1 synthetic exercise",
            **record_kwargs(i + 20),
        )
        for i, name in enumerate(DATA_NAMES)
    ]
    infrastructure = [
        InfrastructureDependency(
            id=ident,
            name=name,
            type=kind,
            service_ids=[s.id for s in services]
            if i < 6
            else [services[i % 12].id, services[(i + 2) % 12].id],
            administrative_authority="Enterprise" if i < 10 else "Limited",
            failure_consequence="Multiple services degraded or unavailable",
            compromise_consequence="Trust and integrity review required",
            recovery_dependency=i in {0, 1, 2, 3, 4, 5, 10, 11, 18, 19},
            identity_dependency="enterprise-identity"
            if i
            else "Independent recovery identity planned",
            network_dependency="network-control",
            alternate="None" if i < 8 else "Documented alternate",
            separated_from_production=i in {18, 19},
            monitoring_coverage="Tested" if i % 3 else "Deployed, untested",
            recovery_validated=i in {18, 19},
            **record_kwargs(i + 40),
        )
        for i, (ident, name, kind) in enumerate(INFRA)
    ]
    control_planes = [
        ControlPlane(**{**d.model_dump(), "id": f"cp-{d.id}", "name": f"Control plane - {d.name}"})
        for d in infrastructure[:10]
    ]
    security = [
        SecurityCapability(
            id=f"sec-{i + 1:02d}",
            name=name,
            dependency_ids=[infrastructure[i % 20].id],
            preventive_control="Access control",
            detective_control="Behavioral detection",
            response_procedure="Triage and escalation",
            recovery_control="Recovery telemetry check",
            data_source=f"Synthetic telemetry source {i + 1}",
            monitoring_tool="Generic monitoring capability",
            monitoring_team="Security Operations",
            alert_threshold="Risk-reviewed threshold",
            escalation_path="SOC to incident commander",
            maturity=(i % 8) + 1,
            limitation="Coverage and testing vary; tool ownership does not guarantee effectiveness.",
            available_during_recovery=i % 3 != 0,
            **record_kwargs(i + 60),
        )
        for i, name in enumerate(
            [
                "Security event monitoring",
                "Endpoint detection",
                "Network detection",
                "Identity threat detection",
                "Fraud detection",
                "Data-integrity monitoring",
                "Database activity monitoring",
                "Privileged-session monitoring",
                "Cloud monitoring",
                "Vulnerability management",
                "Backup-integrity validation",
                "Configuration monitoring",
            ]
        )
    ]
    players = [
        InternalPlayer(
            id=f"role-{i + 1:02d}",
            name=name,
            role_type="Decision or operating role",
            alternate=f"Alternate {name}",
            **record_kwargs(i + 80),
        )
        for i, name in enumerate(
            [
                "Chief Executive Officer",
                "Chief Risk Officer",
                "Chief Information Security Officer",
                "Chief Information Officer",
                "Chief Operations Officer",
                "Incident Commander",
                "Security Operations",
                "Payment Operations",
                "Business Continuity",
                "Disaster Recovery",
            ]
        )
    ]
    parties = [
        ThirdParty(
            id=f"tp-{i + 1:02d}",
            name=name,
            service_provided=f"Synthetic {name.lower()} service",
            service_ids=[services[i % 12].id, services[(i + 2) % 12].id],
            contract_owner="Third-Party Risk",
            risk_owner="Chief Risk Officer",
            data_exchanged="Minimum operational records",
            connectivity="Private API",
            administrative_access=i in {0, 3, 4},
            geographic_concentration="Single synthetic region"
            if i % 2
            else "Diversified synthetic regions",
            subcontractor_reliance="Evidence unavailable" if i % 3 == 0 else "Reviewed",
            recovery_commitment="Contract evidence required",
            contractual_rto_minutes=480 if i % 2 else 120,
            tested_recovery="Never" if i % 3 == 0 else "2026 synthetic test",
            exit_plan="Documented" if i % 2 else "Unknown",
            alternate_provider="None" if i < 4 else "Synthetic alternate",
            manual_substitute="Limited",
            **record_kwargs(i + 100),
        )
        for i, name in enumerate(
            [
                "Core service provider",
                "Payment processor",
                "Cloud provider",
                "Telecommunications provider",
                "Managed security provider",
                "Card network liaison",
                "ACH operator liaison",
                "Recovery support firm",
            ]
        )
    ]
    workarounds = [
        ManualWorkaround(
            id=f"work-{i + 1:02d}",
            name=f"{s.name} manual continuity",
            service_id=s.id,
            exists=i % 4 != 0,
            description="Priority items processed with dual control",
            activation_authority="Chief Operations Officer",
            required_people=["Payment Operations"],
            dependencies=["Offline recovery data"],
            throughput_pct=25 if i % 4 != 0 else 0,
            max_duration_minutes=240,
            error_rate="Elevated; reconciliation required",
            reconciliation="Dual-control journal",
            fraud_implications="Additional review required",
            last_test="Never" if i % 3 == 0 else "2026 synthetic drill",
            test_result="Requires improvement",
            trained=i % 3 != 0,
            **record_kwargs(i + 120),
        )
        for i, s in enumerate(services)
    ]
    recovery = [
        RecoveryCapability(
            id=f"rec-{i + 1:02d}",
            name=f"{s.name} recovery",
            service_ids=[s.id],
            independence_checks={
                "identity": i % 3 != 0,
                "credentials": True,
                "clean_workstations": True,
                "dns": i % 4 != 0,
                "monitoring": i % 3 != 0,
            },
            last_exercise="2026 synthetic recovery exercise",
            proven_duration_minutes=180 if i % 2 else None,
            status="service-within-tolerance" if i % 3 == 1 else "restore-tested",
            **record_kwargs(i + 140),
        )
        for i, s in enumerate(services)
    ]
    responsibilities = [
        Responsibility(
            activity=a,
            responsible=["Technology Operations"],
            accountable=["Chief Operations Officer"],
            consulted=["Chief Risk Officer"],
            informed=["Executive Sponsor"],
            deadline="Before 75% of MTD",
            escalation_authority="Chief Executive Officer",
            alternate="Alternate Chief Operations Officer",
        )
        for a in [
            "Service suspension",
            "Manual operations",
            "Third-party disconnection",
            "Identity isolation",
            "Failover",
            "Recovery-point selection",
            "Data reconciliation",
            "Service restoration",
            "Customer communication",
            "Regulatory escalation",
            "Residual-risk acceptance",
        ]
    ]
    scenarios = [
        ScenarioRecommendation(
            id=f"scenario-{i + 1}",
            name=name,
            reason="Applies to synthetic shared dependencies and evidence-based gaps.",
            service_ids=[s.id for s in services[:4]],
            tier0_dependency_ids=[infrastructure[i].id],
            decisions=["Containment", "Recovery point approval"],
            participants=["Incident Commander", "Chief Risk Officer", "Technology Operations"],
            warning_indicators=["Correlated synthetic telemetry"],
            expected_evidence=[f"SYN-EV-{i + 1:03d}"],
            objectives=["Exercise decision authority and recovery independence"],
            success_criteria=["Decision made before tolerance threshold with evidence recorded"],
        )
        for i, name in enumerate(
            [
                "Enterprise identity compromise",
                "Payment processor outage",
                "Cloud-region failure",
                "Data-integrity uncertainty",
                "Backup compromise",
            ]
        )
    ]
    assessment = Assessment(
        id="harbor-ridge-2026",
        version=1,
        title="Harbor Ridge Critical-Service Assessment",
        organization=org,
        current_step=16,
        services=services,
        impacts=impacts,
        tolerances=tolerances,
        processes=processes,
        applications=apps,
        data_assets=data,
        infrastructure=infrastructure,
        control_planes=control_planes,
        security_capabilities=security,
        internal_players=players,
        third_parties=parties,
        workarounds=workarounds,
        recovery_capabilities=recovery,
        responsibilities=responsibilities,
        scenarios=scenarios,
        relationships=[
            Relationship(
                id=f"rel-{i + 1:02d}",
                source=s.id,
                destination=infrastructure[i % 20].id,
                relationship_type="depends_on",
                evidence=f"SYN-EV-{i + 1:03d}",
                confidence="Confirmed",
            )
            for i, s in enumerate(services)
        ],
        approvals=[
            Approval(role=r, approver=f"Synthetic {r}", status="Approved")
            for r in [
                "Business owner",
                "Technology owner",
                "Risk owner",
                "Business continuity",
                "Cybersecurity",
                "Compliance",
                "Executive sponsor",
            ]
        ],
    )
    assessment.tier0_candidates = generate_tier0_candidates(assessment)
    assessment.findings, assessment.evidence_gaps = generate_analysis(assessment)
    for i, subject in enumerate(
        ["enterprise-identity", "dns", "backup", "tp-01", "work-01", "data-10"], 1
    ):
        if not any(g.subject_id == subject for g in assessment.evidence_gaps):
            assessment.evidence_gaps.append(
                EvidenceGap(
                    id=f"eg-demo-{i:02d}",
                    subject_id=subject,
                    missing_evidence="Synthetic validation evidence is unavailable",
                    consequence="The control or recovery conclusion remains uncertain.",
                    owner="Assessment Owner",
                )
            )
    assessment.corrective_actions = [
        CorrectiveAction(
            id=f"ca-{i + 1:02d}",
            finding_id=f.id,
            action=f.recommendation,
            owner=f.owner,
            priority=f.priority,
            target_date=date(2027, 3, 31),
        )
        for i, f in enumerate(assessment.findings)
    ]
    return assessment


if __name__ == "__main__":
    target = ROOT / "data/synthetic_assessments/harbor-ridge-2026.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build().model_dump_json(indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "path": str(target),
                "services": 12,
                "processes": 20,
                "applications_data": 25,
                "infrastructure": 20,
                "security": 12,
                "roles": 10,
                "third_parties": 8,
                "tier0": len(build().tier0_candidates),
                "findings": len(build().findings),
                "gaps": len(build().evidence_gaps),
            },
            indent=2,
        )
    )
