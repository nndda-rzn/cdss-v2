"""Encounter endpoints: create (consent-gated), detail, close."""
import uuid
from typing import cast

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.clinical_context import ClinicalContext
from app.db.models.encounter import Encounter
from app.extensions import db
from app.schemas.encounter import EncounterCreate, EncounterOut
from app.services.clinical_context.writer import write_context
from app.services.encounter.close import close_encounter
from app.services.encounter.create import create_encounter
from app.services.vital_signs.capture import capture_vitals
from app.services.vital_signs.query import list_vitals

bp = Blueprint("encounters", __name__, url_prefix="/api/encounters")


def _session() -> Session:
    return cast(Session, db.session)


def _ctx() -> dict[str, str]:
    return {
        "ip_address": request.remote_addr or "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "request_id": getattr(g, "request_id", request.headers.get("X-Request-ID", "n/a")),
    }


def _user_id() -> int:
    from flask_jwt_extended import get_jwt_identity

    return int(get_jwt_identity())


def _claims_facility_id() -> int:
    from flask_jwt_extended import get_jwt

    return int(get_jwt()["facility_id"])


def _to_out(e: Encounter) -> dict[str, object]:
    return EncounterOut(
        id=e.id,
        patient_id=str(e.patient_id),
        facility_id=e.facility_id,
        attending_user_id=e.attending_user_id,
        encounter_type=e.encounter_type,
        status=e.status,
        chief_complaint=e.chief_complaint,
        started_at=e.started_at.isoformat(),
        ended_at=e.ended_at.isoformat() if e.ended_at else None,
    ).model_dump()


@bp.post("")
@require_role(Role.CLINICIAN, Role.NURSE)
def create() -> tuple[Response, int]:
    data = EncounterCreate(**(request.get_json() or {}))
    session = _session()
    encounter = create_encounter(
        session,
        patient_id=uuid.UUID(data.patient_id),
        facility_id=_claims_facility_id(),
        user_id=_user_id(),
        encounter_type=data.encounter_type,
        chief_complaint=data.chief_complaint,
        **_ctx(),
    )
    session.commit()
    return jsonify(encounter=_to_out(encounter)), 201


@bp.get("/<int:encounter_id>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE)
def get_one(encounter_id: int) -> Response:
    session = _session()
    encounter = session.get(Encounter, encounter_id)
    if encounter is None:
        raise NotFoundError(
            code="ENCOUNTER_NOT_FOUND",
            message_id="Kunjungan tidak ditemukan",
            message_en="Encounter not found",
        )
    return jsonify(**_to_out(encounter))


@bp.patch("/<int:encounter_id>/close")
@require_role(Role.CLINICIAN, Role.NURSE)
def close(encounter_id: int) -> Response:
    session = _session()
    close_encounter(session, encounter_id=encounter_id, user_id=_user_id())
    session.commit()
    return jsonify(status="ok")


@bp.post("/<int:encounter_id>/clinical-context")
@require_role(Role.CLINICIAN, Role.NURSE)
def create_context(encounter_id: int) -> tuple[Response, int]:
    session = _session()
    body = request.get_json() or {}
    write_context(
        session,
        encounter_id=encounter_id,
        user_id=_user_id(),
        symptom_chest_pain=body.get("symptom_chest_pain", False),
        symptom_dyspnea=body.get("symptom_dyspnea", False),
        symptom_palpitation=body.get("symptom_palpitation", False),
        symptom_syncope=body.get("symptom_syncope", False),
        symptom_other=body.get("symptom_other"),
        pain_onset_minutes=body.get("pain_onset_minutes"),
        pain_duration_minutes=body.get("pain_duration_minutes"),
    )
    session.commit()
    return jsonify(status="ok"), 201


@bp.get("/<int:encounter_id>/clinical-context")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE)
def get_context(encounter_id: int) -> Response:
    session = _session()
    ctx = session.scalar(
        select(ClinicalContext).where(
            ClinicalContext.encounter_id == encounter_id
        )
    )
    if ctx is None:
        raise NotFoundError(
            code="CLINICAL_CONTEXT_NOT_FOUND",
            message_id="Konteks klinis tidak ditemukan",
            message_en="Clinical context not found",
        )
    return jsonify(
        id=ctx.id,
        encounter_id=ctx.encounter_id,
        symptom_chest_pain=ctx.symptom_chest_pain,
        symptom_dyspnea=ctx.symptom_dyspnea,
        symptom_palpitation=ctx.symptom_palpitation,
        symptom_syncope=ctx.symptom_syncope,
        symptom_other=ctx.symptom_other,
        pain_onset_minutes=ctx.pain_onset_minutes,
        pain_duration_minutes=ctx.pain_duration_minutes,
    )


@bp.post("/<int:encounter_id>/vital-signs")
@require_role(Role.CLINICIAN, Role.NURSE)
def create_vitals(encounter_id: int) -> tuple[Response, int]:
    session = _session()
    body = request.get_json() or {}
    capture_vitals(
        session,
        encounter_id=encounter_id,
        user_id=_user_id(),
        bp_systolic=body.get("bp_systolic"),
        bp_diastolic=body.get("bp_diastolic"),
        heart_rate=body.get("heart_rate"),
        respiratory_rate=body.get("respiratory_rate"),
        spo2=body.get("spo2"),
        temperature=body.get("temperature"),
        weight=body.get("weight"),
        height=body.get("height"),
    )
    session.commit()
    return jsonify(status="ok"), 201


@bp.get("/<int:encounter_id>/vital-signs")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE)
def get_vitals(encounter_id: int) -> Response:
    session = _session()
    rows = list_vitals(session, encounter_id=encounter_id)
    items = [
        {
            "id": v.id,
            "measured_at": v.measured_at.isoformat(),
            "bp_systolic": v.bp_systolic,
            "bp_diastolic": v.bp_diastolic,
            "heart_rate": v.heart_rate,
            "respiratory_rate": v.respiratory_rate,
            "spo2": v.spo2,
            "temperature": v.temperature,
            "weight": v.weight,
            "height": v.height,
        }
        for v in rows
    ]
    return jsonify(items=items)
