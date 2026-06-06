"""Vital-signs endpoints (M:1 with an encounter)."""
from flask import Blueprint, Response, jsonify, request

from app.api._shared import current_user_id, session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.services.vital_signs.capture import capture_vitals
from app.services.vital_signs.query import list_vitals

bp = Blueprint("vital_signs", __name__, url_prefix="/api/encounters")


@bp.post("/<int:encounter_id>/vital-signs")
@require_role(Role.CLINICAL)
def create_vitals(encounter_id: int) -> tuple[Response, int]:
    s = session()
    body = request.get_json() or {}
    capture_vitals(
        s,
        encounter_id=encounter_id,
        user_id=current_user_id(),
        bp_systolic=body.get("bp_systolic"),
        bp_diastolic=body.get("bp_diastolic"),
        heart_rate=body.get("heart_rate"),
        respiratory_rate=body.get("respiratory_rate"),
        spo2=body.get("spo2"),
        temperature=body.get("temperature"),
        weight=body.get("weight"),
        height=body.get("height"),
    )
    s.commit()
    return jsonify(status="ok"), 201


@bp.get("/<int:encounter_id>/vital-signs")
@require_role(Role.ADMIN, Role.CLINICAL)
def get_vitals(encounter_id: int) -> Response:
    s = session()
    rows = list_vitals(s, encounter_id=encounter_id)
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