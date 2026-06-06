"""Clinical-context endpoints (1:1 with an encounter)."""
from flask import Blueprint, Response, jsonify, request
from sqlalchemy import select

from app.api._shared import current_user_id, session
from app.core.exceptions.base import NotFoundError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.clinical_context import ClinicalContext
from app.services.clinical_context.writer import write_context

bp = Blueprint("clinical_context", __name__, url_prefix="/api/encounters")


@bp.post("/<int:encounter_id>/clinical-context")
@require_role(Role.CLINICAL)
def create_context(encounter_id: int) -> tuple[Response, int]:
    s = session()
    body = request.get_json() or {}
    write_context(
        s,
        encounter_id=encounter_id,
        user_id=current_user_id(),
        symptom_chest_pain=body.get("symptom_chest_pain", False),
        symptom_dyspnea=body.get("symptom_dyspnea", False),
        symptom_palpitation=body.get("symptom_palpitation", False),
        symptom_syncope=body.get("symptom_syncope", False),
        symptom_other=body.get("symptom_other"),
        pain_onset_minutes=body.get("pain_onset_minutes"),
        pain_duration_minutes=body.get("pain_duration_minutes"),
    )
    s.commit()
    return jsonify(status="ok"), 201


@bp.get("/<int:encounter_id>/clinical-context")
@require_role(Role.ADMIN, Role.CLINICAL)
def get_context(encounter_id: int) -> Response:
    s = session()
    ctx = s.scalar(
        select(ClinicalContext).where(ClinicalContext.encounter_id == encounter_id)
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