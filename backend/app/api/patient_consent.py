"""Patient consent endpoints (capture / revoke / list)."""
import uuid

from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select

from app.api._shared import current_user_id, session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.consent import Consent
from app.services.consent.capture import capture_consent
from app.services.consent.revoke import revoke_consent

bp = Blueprint("patient_consent", __name__, url_prefix="/api/patients")


@bp.post("/<patient_id>/consent")
@require_role(Role.CLINICIAN, Role.NURSE)
def capture_patient_consent(patient_id: str) -> tuple[Response, int]:
    s = session()
    body = request.get_json() or {}
    consent_type = body.get("consent_type", "")
    pid = uuid.UUID(patient_id)
    if body.get("status") == "revoked":
        revoke_consent(s, patient_id=pid, consent_type=consent_type, user_id=current_user_id())
    else:
        capture_consent(s, patient_id=pid, consent_type=consent_type, user_id=current_user_id())
    s.commit()
    return jsonify(status="ok"), 201


@bp.get("/<patient_id>/consent")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE)
def list_patient_consent(patient_id: str) -> Response:
    s = session()
    rows = s.scalars(
        select(Consent)
        .where(Consent.patient_id == uuid.UUID(patient_id))
        .order_by(Consent.id.desc())
    ).all()
    items = [
        {
            "id": c.id,
            "consent_type": c.consent_type,
            "status": c.status,
            "given_at": c.given_at.isoformat() if c.given_at else None,
            "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
        }
        for c in rows
    ]
    return jsonify(items=items)