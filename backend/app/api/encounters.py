"""Encounter endpoints: create (consent-gated), detail, close."""
import uuid

from flask import Blueprint, Response, jsonify, request

from app.api._shared import claims_facility_id, current_user_id, request_ctx, session
from app.core.exceptions.base import NotFoundError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.encounter import Encounter
from app.schemas.encounter import EncounterCreate, EncounterOut
from app.services.encounter.close import close_encounter
from app.services.encounter.create import create_encounter

bp = Blueprint("encounters", __name__, url_prefix="/api/encounters")


def encounter_to_out(e: Encounter) -> dict[str, object]:
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
    s = session()
    encounter = create_encounter(
        s,
        patient_id=uuid.UUID(data.patient_id),
        facility_id=claims_facility_id(),
        user_id=current_user_id(),
        encounter_type=data.encounter_type,
        chief_complaint=data.chief_complaint,
        **request_ctx(),
    )
    s.commit()
    return jsonify(encounter=encounter_to_out(encounter)), 201


@bp.get("/<int:encounter_id>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE)
def get_one(encounter_id: int) -> Response:
    s = session()
    encounter = s.get(Encounter, encounter_id)
    if encounter is None:
        raise NotFoundError(
            code="ENCOUNTER_NOT_FOUND",
            message_id="Kunjungan tidak ditemukan",
            message_en="Encounter not found",
        )
    return jsonify(**encounter_to_out(encounter))


@bp.patch("/<int:encounter_id>/close")
@require_role(Role.CLINICIAN, Role.NURSE)
def close(encounter_id: int) -> Response:
    s = session()
    close_encounter(s, encounter_id=encounter_id, user_id=current_user_id())
    s.commit()
    return jsonify(status="ok")