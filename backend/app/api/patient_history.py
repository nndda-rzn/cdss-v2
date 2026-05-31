"""Patient medical-history endpoints (append / list)."""
import uuid

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select

from app.api._shared import current_user_id, session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.patient_history import PatientHistory
from app.services.patient_history.writer import add_history

bp = Blueprint("patient_history", __name__, url_prefix="/api/patients")


@bp.post("/<patient_id>/history")
@require_role(Role.CLINICIAN, Role.NURSE)
def add_patient_history(patient_id: str) -> tuple[Response, int]:
    s = session()
    body = request.get_json() or {}
    add_history(
        s,
        patient_id=uuid.UUID(patient_id),
        condition_code=body.get("condition_code", ""),
        user_id=current_user_id(),
        note=body.get("note"),
    )
    s.commit()
    return jsonify(status="ok"), 201


@bp.get("/<patient_id>/history")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE)
def list_patient_history(patient_id: str) -> Response:
    s = session()
    rows = s.scalars(
        select(PatientHistory)
        .where(PatientHistory.patient_id == uuid.UUID(patient_id))
        .order_by(PatientHistory.id.desc())
    ).all()
    items = [
        {
            "id": h.id,
            "condition_code": h.condition_code,
            "onset_date_approx": (
                h.onset_date_approx.isoformat() if h.onset_date_approx else None
            ),
            "note": h.note_encrypted,
            "recorded_at": h.recorded_at.isoformat(),
        }
        for h in rows
    ]
    return jsonify(items=items)