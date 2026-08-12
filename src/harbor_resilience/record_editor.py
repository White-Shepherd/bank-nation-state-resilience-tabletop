from __future__ import annotations

import json
from datetime import date, datetime, timezone
from types import UnionType
from typing import get_args, get_origin

import streamlit as st
from pydantic_core import PydanticUndefined

from . import assessment_models
from .assessment import (
    COLLECTION_MODELS,
    all_record_ids,
    archive_record,
    delete_record,
    duplicate_record,
    field_errors,
    record_id,
    save_assessment,
    upsert_record,
)
from .assessment_models import Assessment

EDITOR_COLLECTIONS = {
    "Critical services": "services",
    "Impact profiles": "impacts",
    "Impact tolerances": "tolerances",
    "Business processes": "processes",
    "Applications": "applications",
    "Data assets": "data_assets",
    "Infrastructure dependencies": "infrastructure",
    "Control planes": "control_planes",
    "Security capabilities": "security_capabilities",
    "Internal roles": "internal_players",
    "Third parties": "third_parties",
    "Manual workarounds": "workarounds",
    "Recovery capabilities": "recovery_capabilities",
    "Evidence items": "evidence_items",
    "Relationships": "relationships",
    "Approvals": "approvals",
}


def is_unsaved(current: str, persisted: str) -> bool:
    try:
        return json.loads(current) != json.loads(persisted)
    except json.JSONDecodeError:
        return current.strip() != persisted.strip()


def _value(annotation, name: str, assessment: Assessment):
    origin, args = get_origin(annotation), get_args(annotation)
    if origin is list:
        return []
    if origin is dict:
        return {}
    if origin in {UnionType, getattr(__import__("typing"), "Union", object)}:
        useful = [x for x in args if x is not type(None)]
        return _value(useful[0], name, assessment) if useful else None
    if origin is not None and str(origin).endswith("Literal"):
        return args[0]
    if annotation is bool:
        return False
    if annotation is int:
        return 1
    if annotation is date:
        return datetime.now(timezone.utc).date().isoformat()
    if name == "id":
        return "new-record"
    if name.endswith("service_id") and assessment.services:
        return assessment.services[0].id
    return "Unknown"


def blank_payload(collection: str, assessment: Assessment) -> dict:
    model = getattr(assessment_models, COLLECTION_MODELS[collection])
    result = {}
    for name, field in model.model_fields.items():
        if field.default is not PydanticUndefined:
            result[name] = field.default
        elif field.default_factory is not None:
            result[name] = field.default_factory()
        else:
            result[name] = _value(field.annotation, name, assessment)
    if "name" in result:
        result["name"] = "New record"
    return result


def render_record_editor(assessment: Assessment, step: int) -> Assessment:
    st.subheader("Interactive record editors")
    options = list(EDITOR_COLLECTIONS)
    collection_label = st.selectbox("Record type", options, key=f"editor-type-{step}")
    collection = EDITOR_COLLECTIONS[collection_label]
    records = list(getattr(assessment, collection))
    show_archived = st.checkbox("Show archived records", key=f"archived-{collection}")
    visible = [x for x in records if show_archived or not getattr(x, "archived", False)]
    choices = ["Create new"] + [record_id(x) for x in visible]
    selected = st.selectbox("Record", choices, key=f"record-choice-{collection}")
    current = (
        None if selected == "Create new" else next(x for x in visible if record_id(x) == selected)
    )
    payload = (
        blank_payload(collection, assessment)
        if current is None
        else current.model_dump(mode="json")
    )
    editor_key = f"record-json-{collection}-{selected}"
    initial = json.dumps(payload, indent=2)
    if st.session_state.get(f"editor-origin-{editor_key}") != initial:
        st.session_state[editor_key] = initial
        st.session_state[f"editor-origin-{editor_key}"] = initial
    st.caption(
        "Edit the named fields below as JSON. Lists define relationship selections; retain Unknown or Requires review rather than fabricating information."
    )
    raw = st.text_area("Record fields", height=360, key=editor_key)
    dirty = is_unsaved(raw, initial)
    st.session_state.wizard_unsaved = dirty
    st.warning(
        "Unsaved changes - submit or discard before leaving this step."
    ) if dirty else st.success("Current record is saved")
    st.caption("Available relationship IDs: " + ", ".join(sorted(all_record_ids(assessment))))
    st.caption(
        "Evidence attachment references: "
        + (", ".join(e.id for e in assessment.evidence_items) or "None recorded")
    )
    try:
        candidate = json.loads(raw)
        parse_error = ""
    except json.JSONDecodeError as exc:
        candidate = {}
        parse_error = f"JSON line {exc.lineno}, column {exc.colno}: {exc.msg}. Correct the highlighted structure."
    model = getattr(assessment_models, COLLECTION_MODELS[collection])
    errors = {"record": parse_error} if parse_error else field_errors(model, candidate)
    if errors:
        for field, message in errors.items():
            st.error(f"{field}: {message}")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Submit record", disabled=bool(errors), key=f"submit-{collection}-{selected}"):
        try:
            assessment = upsert_record(assessment, collection, candidate)
            save_assessment(assessment)
            st.session_state.wizard_assessment = assessment.model_dump(mode="json")
            st.session_state.wizard_last_save = assessment.updated_at.isoformat()
            st.session_state.wizard_unsaved = False
            st.session_state.pop(f"editor-origin-{editor_key}", None)
            st.success("Record validated and durably saved to the active draft.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    duplicate_id = c2.text_input(
        "Duplicate ID",
        value=f"{selected}-copy" if current else "new-record-copy",
        key=f"dup-id-{collection}",
    )
    if c2.button("Duplicate record", disabled=current is None, key=f"dup-{collection}"):
        try:
            assessment = duplicate_record(assessment, collection, selected, duplicate_id)
            save_assessment(assessment)
            st.session_state.wizard_assessment = assessment.model_dump(mode="json")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    if c3.button("Archive record", disabled=current is None, key=f"archive-{collection}"):
        assessment = archive_record(assessment, collection, selected)
        save_assessment(assessment)
        st.session_state.wizard_assessment = assessment.model_dump(mode="json")
        st.rerun()
    confirm = c4.checkbox("Confirm delete", key=f"confirm-delete-{collection}")
    if c4.button(
        "Delete record", disabled=current is None or not confirm, key=f"delete-{collection}"
    ):
        try:
            assessment = delete_record(assessment, collection, selected, True)
            save_assessment(assessment)
            st.session_state.wizard_assessment = assessment.model_dump(mode="json")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
    return assessment
