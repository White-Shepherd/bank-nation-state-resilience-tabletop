from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ImpactTolerance(BaseModel):
    mtd_minutes: int = Field(gt=0)
    rto_minutes: int = Field(gt=0)
    rpo_minutes: int = Field(ge=0)
    minimum_service_pct: int = Field(ge=0, le=100)
    max_data_uncertainty_minutes: int = Field(ge=0)
    max_backlog: int = Field(ge=0)
    customer_harm_threshold: str
    financial_loss_threshold_usd: int = Field(gt=0)
    liquidity_consequence: str
    regulatory_consequence: str
    manual_workaround_minutes: int = Field(ge=0)

    @model_validator(mode="after")
    def rto_must_not_exceed_mtd(self):
        if self.rto_minutes > self.mtd_minutes:
            raise ValueError("RTO cannot exceed maximum tolerable disruption")
        return self


class CriticalService(BaseModel):
    id: str
    name: str
    owner: str = Field(min_length=1)
    tolerance: ImpactTolerance
    dependencies: list[str]


class TierZeroCandidate(BaseModel):
    id: str
    name: str
    type: str
    business_owner: str = Field(min_length=1)
    technical_owner: str = Field(min_length=1)
    critical_services: list[str]
    broad_admin: bool = False
    recovery_dependency: bool = False
    integrity_critical: bool = False
    evidence: list[str] = Field(min_length=1)
    approved: bool | None = None


class Decision(BaseModel):
    phase: int = Field(ge=0, le=5)
    decision: str
    owner: str
    chosen_action: str
    assumptions: str = ""
    dissent: str = ""
    residual_risk: str


class EcosystemNode(BaseModel):
    id: str
    name: str
    layer: str
    node_type: str
    description: str
    owner: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    decision_authority: str = Field(min_length=1)
    critical_services: list[str] = []
    tier0: bool = False
    tier0_rationale: str = "Not designated Tier 0"
    recovery_capability: bool = False
    single_point: bool = False
    third_party: bool = False
    monitoring: list[str] = []
    warning_indicators: list[str] = []
    controls: list[str] = []
    limitations: list[str] = []
    recovery_method: str = "Owner-approved service recovery procedure"
    recovery_objective: str = "Defined by supported critical-service tolerance"
    accessibility_label: str = Field(min_length=1)

    @model_validator(mode="after")
    def tier0_has_rationale(self):
        if self.tier0 and self.tier0_rationale == "Not designated Tier 0":
            raise ValueError("Tier 0 node requires rationale")
        return self


class EcosystemRelationship(BaseModel):
    id: str
    source: str
    destination: str
    relationship_type: str
    description: str
    criticality: str
    confidence: str
    evidence: str
    normal_state: str
    incident_state: str
    recovery_state: str
    propagation: bool = False
    trigger: str = ""
    effect: str = ""
    assumptions: str = ""
    compensating_control: str = ""


class Responsibility(BaseModel):
    activity: str
    responsible: list[str]
    accountable: list[str]
    consulted: list[str]
    informed: list[str]
    deadline_minutes: int = Field(gt=0)
    escalation_authority: str
    alternate: str = Field(min_length=1)
    technical_action: bool = False
    business_approval: str = ""
    evidence_required: bool = True


class WarningIndicator(BaseModel):
    id: str
    signal: str
    category: str
    data_source: str = Field(min_length=1)
    tool: str
    monitoring_team: str
    tier0_dependency: str
    critical_service: str
    escalation_threshold: str
    possible_benign_cause: str
    confidence: str


class ToolCoverage(BaseModel):
    capability_id: str
    target_id: str
    data_source: str = Field(min_length=1)
    deployed: bool
    configured: bool
    telemetry_received: bool
    detection_tested: bool
    response_integrated: bool
    recovery_visibility_validated: bool
    independent_investigation: bool
    limitation: str


class ScenarioNodeState(BaseModel):
    phase: int = Field(ge=0, le=7)
    node_id: str
    status: str
    indicator_ids: list[str] = []
    decision: str = ""
    deadline_minutes: int | None = None
    recovery_prerequisite: str = ""
