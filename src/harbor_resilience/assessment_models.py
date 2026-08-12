from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Classification = Literal["Public", "Internal", "Confidential", "Restricted"]
ReviewState = Literal["Unknown", "Evidence unavailable", "Requires review", "Confirmed"]


class Record(BaseModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    name: str = Field(min_length=1)
    owner: str = "Unknown"
    evidence: list[str] = []
    confidence: ReviewState = "Unknown"


class Organization(BaseModel):
    name: str
    industry: str
    size: str
    geographic_footprint: str
    customer_types: list[str]
    products_services: list[str]
    legal_entities: list[str]
    primary_regulators: list[str]
    operating_model: str
    technology_model: str
    outsourcing_model: str
    assessment_owner: str
    executive_sponsor: str
    assessment_date: date
    review_date: date
    classification: Classification = "Internal"


class ImpactProfile(BaseModel):
    service_id: str
    horizon: str
    dimensions: dict[str, int]
    rationale: str = ""

    @model_validator(mode="after")
    def severe_needs_rationale(self):
        if any(value >= 4 for value in self.dimensions.values()) and not self.rationale:
            raise ValueError("high or severe impact requires narrative rationale")
        return self


class ImpactTolerance(BaseModel):
    service_id: str
    mtd_minutes: int = Field(gt=0)
    rto_minutes: int = Field(gt=0)
    rpo_minutes: int = Field(ge=0)
    minimum_viable_service: str
    data_uncertainty_minutes: int = Field(ge=0)
    transaction_backlog: int = Field(ge=0)
    manual_workaround_minutes: int = Field(ge=0)
    thresholds: dict[str, str]
    accountable_owner: str
    approved: bool = False
    tested: bool = False


class CriticalService(Record):
    description: str
    stakeholders: list[str]
    technical_owner: str
    operating_entities: list[str]
    geography: str
    operating_hours: str
    volume: str
    revenue_relationship: str
    payment_obligation: bool
    harm_potential: str
    regulatory_significance: str
    upstream_services: list[str] = []
    downstream_services: list[str] = []
    substitute_service: str = "Unknown"
    manual_alternative: str = "Unknown"
    criticality: str = "Requires review"
    rationale: str


class BusinessProcess(Record):
    description: str
    service_ids: list[str]
    trigger: str
    inputs: list[str]
    outputs: list[str]
    application_ids: list[str] = []
    data_asset_ids: list[str] = []
    teams: list[str] = []
    third_party_ids: list[str] = []
    facilities: list[str] = []
    operating_window: str
    manual_alternative: str
    max_backlog: str
    recovery_priority: str
    bottlenecks: list[str] = []


class TechnicalAsset(Record):
    type: str
    description: str
    operator: str
    hosting_model: str
    environments: list[str]
    service_ids: list[str]
    process_ids: list[str]
    authority: str
    classification: Classification
    availability: str
    integrity: str
    confidentiality: str
    recovery_method: str
    last_recovery_test: str
    end_of_life: bool = False


class Application(TechnicalAsset):
    pass


class DataAsset(TechnicalAsset):
    pass


class InfrastructureDependency(Record):
    type: str
    service_ids: list[str]
    administrative_authority: str
    failure_consequence: str
    compromise_consequence: str
    recovery_dependency: bool
    identity_dependency: str
    network_dependency: str
    third_party_id: str = ""
    alternate: str = "Unknown"
    separated_from_production: bool = False
    monitoring_coverage: str = "Unknown"
    recovery_validated: bool = False


class ControlPlane(InfrastructureDependency):
    pass


class SecurityCapability(Record):
    dependency_ids: list[str]
    preventive_control: str
    detective_control: str
    response_procedure: str
    recovery_control: str
    data_source: str
    monitoring_tool: str
    monitoring_team: str
    alert_threshold: str
    escalation_path: str
    maturity: int = Field(ge=1, le=8)
    limitation: str
    available_during_recovery: bool


class InternalPlayer(Record):
    role_type: str
    alternate: str = "Unknown"


class ThirdParty(Record):
    service_provided: str
    service_ids: list[str]
    contract_owner: str
    risk_owner: str
    data_exchanged: str
    connectivity: str
    administrative_access: bool
    geographic_concentration: str
    subcontractor_reliance: str
    recovery_commitment: str
    contractual_rto_minutes: int | None = None
    tested_recovery: str = "Unknown"
    exit_plan: str = "Unknown"
    alternate_provider: str = "Unknown"
    manual_substitute: str = "Unknown"
    notification_terms: str = "Evidence unavailable"


class ManualWorkaround(Record):
    service_id: str
    exists: bool
    description: str
    activation_authority: str
    required_people: list[str]
    dependencies: list[str]
    throughput_pct: int = Field(ge=0, le=100)
    max_duration_minutes: int = Field(ge=0)
    error_rate: str
    reconciliation: str
    fraud_implications: str
    last_test: str
    test_result: str
    trained: bool


class RecoveryCapability(Record):
    service_ids: list[str]
    independence_checks: dict[str, bool]
    last_exercise: str
    proven_duration_minutes: int | None = None
    status: Literal[
        "backup-exists",
        "immutable",
        "restorable",
        "restore-tested",
        "data-validated",
        "service-within-tolerance",
    ]


class Relationship(BaseModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    source: str
    destination: str
    relationship_type: str
    evidence: str
    confidence: ReviewState


class Responsibility(BaseModel):
    activity: str
    responsible: list[str]
    accountable: list[str]
    consulted: list[str]
    informed: list[str]
    deadline: str
    escalation_authority: str
    alternate: str


class Tier0Candidate(BaseModel):
    id: str
    dependency_id: str
    service_ids: list[str]
    triggered_rules: list[str]
    evidence: list[str]
    missing_evidence: list[str]
    concentration_risk: str
    recovery_dependency: bool
    preliminary_rationale: str
    arguments_against: str
    reviewer_decision: Literal["Pending", "Approved", "Rejected"] = "Pending"
    approval_record: str = ""


class Finding(BaseModel):
    id: str
    condition: str
    service_ids: list[str]
    evidence: list[str]
    confidence: ReviewState
    consequence: str
    recommendation: str
    owner: str
    priority: str
    validation_method: str
    residual_uncertainty: str


class EvidenceGap(BaseModel):
    id: str
    subject_id: str
    missing_evidence: str
    consequence: str
    owner: str


class Approval(BaseModel):
    role: str
    approver: str
    status: Literal["Pending", "Approved", "Changes requested"]
    timestamp: datetime | None = None
    note: str = "Synthetic demonstration approval; not an electronic signature"


class ScenarioRecommendation(BaseModel):
    id: str
    name: str
    reason: str
    service_ids: list[str]
    tier0_dependency_ids: list[str]
    decisions: list[str]
    participants: list[str]
    warning_indicators: list[str]
    expected_evidence: list[str]
    objectives: list[str]
    success_criteria: list[str]


class CorrectiveAction(BaseModel):
    id: str
    finding_id: str
    action: str
    owner: str
    priority: str
    target_date: date
    status: str = "Open"


class Assessment(BaseModel):
    schema_version: str = "1.0.0"
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    version: int = Field(ge=1)
    title: str
    organization: Organization
    status: Literal["Draft", "Review", "Approved", "Archived"] = "Draft"
    current_step: int = Field(ge=1, le=16, default=1)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    services: list[CriticalService] = []
    impacts: list[ImpactProfile] = []
    tolerances: list[ImpactTolerance] = []
    processes: list[BusinessProcess] = []
    applications: list[Application] = []
    data_assets: list[DataAsset] = []
    infrastructure: list[InfrastructureDependency] = []
    control_planes: list[ControlPlane] = []
    security_capabilities: list[SecurityCapability] = []
    internal_players: list[InternalPlayer] = []
    third_parties: list[ThirdParty] = []
    workarounds: list[ManualWorkaround] = []
    recovery_capabilities: list[RecoveryCapability] = []
    relationships: list[Relationship] = []
    responsibilities: list[Responsibility] = []
    tier0_candidates: list[Tier0Candidate] = []
    findings: list[Finding] = []
    evidence_gaps: list[EvidenceGap] = []
    approvals: list[Approval] = []
    scenarios: list[ScenarioRecommendation] = []
    corrective_actions: list[CorrectiveAction] = []

    @model_validator(mode="after")
    def identifiers_are_unique(self):
        records = (
            self.services
            + self.processes
            + self.applications
            + self.data_assets
            + self.infrastructure
            + self.control_planes
        )
        ids = [record.id for record in records]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate record identifier")
        return self
