from pathlib import Path

import yaml

from .models import CriticalService, TierZeroCandidate

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative: str):
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_services() -> list[CriticalService]:
    return [CriticalService.model_validate(x) for x in load_yaml("data/critical_services/services.yaml")]


def load_tier0() -> list[TierZeroCandidate]:
    return [TierZeroCandidate.model_validate(x) for x in load_yaml("data/tier0/registry.yaml")]

