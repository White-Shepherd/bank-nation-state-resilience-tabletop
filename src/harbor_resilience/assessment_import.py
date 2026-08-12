from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass

from pydantic import ValidationError

from .assessment import all_record_ids
from .assessment_models import Assessment

IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass(frozen=True)
class TemplateSpec:
    name: str
    collection: str
    required: tuple[str, ...]
    references: dict[str, str]
    integer_fields: tuple[str, ...] = ()
    boolean_fields: tuple[str, ...] = ()


TEMPLATE_SPECS = {
    "critical-services": TemplateSpec(
        "critical-services",
        "services",
        ("id", "name", "description", "business_owner", "technical_owner"),
        {},
    ),
    "impact-tolerances": TemplateSpec(
        "impact-tolerances",
        "tolerances",
        ("service_id", "mtd_minutes", "rto_minutes", "rpo_minutes"),
        {"service_id": "services"},
        (
            "mtd_minutes",
            "rto_minutes",
            "rpo_minutes",
            "data_uncertainty_minutes",
            "manual_workaround_minutes",
        ),
        ("approved", "tested"),
    ),
    "business-processes": TemplateSpec(
        "business-processes",
        "processes",
        ("id", "name", "service_ids", "owner"),
        {"service_ids": "services"},
    ),
    "applications": TemplateSpec(
        "applications",
        "applications",
        ("id", "name", "service_ids", "owner"),
        {"service_ids": "services", "process_ids": "processes"},
    ),
    "data-assets": TemplateSpec(
        "data-assets",
        "data_assets",
        ("id", "name", "service_ids", "owner"),
        {"service_ids": "services"},
    ),
    "infrastructure": TemplateSpec(
        "infrastructure",
        "infrastructure",
        ("id", "name", "service_ids", "owner"),
        {"service_ids": "services"},
        (),
        ("recovery_dependency", "separated_from_production"),
    ),
    "security-capabilities": TemplateSpec(
        "security-capabilities",
        "security_capabilities",
        ("id", "name", "dependency_ids", "owner"),
        {"dependency_ids": "infrastructure"},
        ("maturity",),
        ("available_during_recovery",),
    ),
    "people-and-roles": TemplateSpec(
        "people-and-roles", "internal_players", ("id", "name", "role_type", "owner"), {}
    ),
    "third-parties": TemplateSpec(
        "third-parties",
        "third_parties",
        ("id", "name", "service_ids", "contract_owner", "risk_owner"),
        {"service_ids": "services"},
        ("contractual_rto_minutes",),
        ("administrative_access",),
    ),
    "manual-workarounds": TemplateSpec(
        "manual-workarounds",
        "workarounds",
        ("id", "name", "service_id", "exists"),
        {"service_id": "services"},
        ("throughput_pct", "max_duration_minutes"),
        ("exists", "trained"),
    ),
    "recovery-capabilities": TemplateSpec(
        "recovery-capabilities",
        "recovery_capabilities",
        ("id", "name", "service_ids", "owner", "status"),
        {"service_ids": "services"},
        ("proven_duration_minutes",),
    ),
    "evidence-register": TemplateSpec(
        "evidence-register",
        "evidence_items",
        ("id", "subject_id", "evidence_type", "source", "owner"),
        {"subject_id": "all"},
    ),
}


def _values(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def validate_csv(
    template: str, content: str, assessment: Assessment
) -> tuple[list[dict], list[dict]]:
    spec = TEMPLATE_SPECS[template]
    reader = csv.DictReader(io.StringIO(content))
    headers = set(reader.fieldnames or [])
    missing = set(spec.required) - headers
    if missing:
        return [], [
            {
                "row": 1,
                "field": "header",
                "error": f"Missing required headers: {', '.join(sorted(missing))}",
            }
        ]
    valid, errors, seen = [], [], set()
    known = all_record_ids(assessment)
    for number, raw in enumerate(reader, 2):
        row = {k: (v or "").strip() for k, v in raw.items()}
        row_errors = []
        identifier = row.get("id") or f"{template}-{number}"
        if not IDENTIFIER.fullmatch(identifier):
            row_errors.append(
                ("id", "Use lowercase letters, digits, and hyphens; start with a letter.")
            )
        if identifier in seen:
            row_errors.append(("id", "Duplicate identifier in uploaded file."))
        seen.add(identifier)
        for field in spec.required:
            if not row.get(field):
                row_errors.append(
                    (field, "Required for import; use Unknown only where the template permits it.")
                )
        for field in spec.integer_fields:
            if row.get(field):
                try:
                    int(row[field])
                except ValueError:
                    row_errors.append((field, "Enter a whole number."))
        for field in spec.boolean_fields:
            if row.get(field).lower() not in {"", "true", "false", "unknown", "requires review"}:
                row_errors.append((field, "Use true, false, Unknown, or Requires review."))
        for field in spec.references:
            for reference in _values(row.get(field, "")):
                if reference not in known:
                    row_errors.append(
                        (
                            field,
                            f"Unknown relationship reference '{reference}'. Import its source record first.",
                        )
                    )
        if row_errors:
            errors.extend(
                {"row": number, "id": identifier, "field": field, "error": error}
                for field, error in row_errors
            )
        else:
            valid.append(row)
    return valid, errors


def import_valid_rows(
    assessment: Assessment, template: str, rows: list[dict], confirmed: bool
) -> Assessment:
    if not confirmed:
        raise ValueError("import confirmation required")
    before = assessment.model_copy(deep=True)
    try:
        staged = {k: list(v) for k, v in assessment.incomplete_records.items()}
        existing = {
            str(row.get("id") or row.get("service_id")): row for row in staged.get(template, [])
        }
        for row in rows:
            existing[str(row.get("id") or row.get("service_id"))] = row
        staged[template] = list(existing.values())
        return Assessment.model_validate(
            assessment.model_copy(update={"incomplete_records": staged}, deep=True)
        )
    except (TypeError, ValueError, ValidationError):
        return before


def export_template_rows(assessment: Assessment, template: str) -> str:
    path_rows = assessment.incomplete_records.get(template, [])
    if not path_rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(path_rows[0]))
    writer.writeheader()
    writer.writerows(path_rows)
    return output.getvalue()
