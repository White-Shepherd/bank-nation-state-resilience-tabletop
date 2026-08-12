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
