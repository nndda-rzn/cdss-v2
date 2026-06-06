"""AI-analysis endpoints: run all active models on a study, list results."""
import uuid
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request
from sqlalchemy import select

from app.api._shared import current_user_id, request_ctx, session
from app.api.ecg_studies import get_study_or_404
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.model_metadata import ModelMetadata
from app.schemas.ai_analysis import AIAnalysisOut
from app.services.ecg_study.consent_gate import ensure_ai_analysis_consent
from app.services.inference.orchestrate import analyze_study

bp = Blueprint("ai_analysis", __name__, url_prefix="/api/encounters")


def analysis_to_out(a: AIAnalysis, model: ModelMetadata) -> dict[str, object]:
    return AIAnalysisOut(
        id=a.id,
        ecg_study_id=a.ecg_study_id,
        model_metadata_id=a.model_metadata_id,
        model_name=model.model_name,
        architecture=model.architecture,
        predicted_class=a.predicted_class,
        confidence_score=a.confidence_score,
        probability_json=a.probability_json,
        inference_time_ms=a.inference_time_ms,
        device_used=a.device_used,
        status=a.status,
        error_message=a.error_message,
        created_at=a.created_at.isoformat(),
    ).model_dump()


@bp.post("/<int:encounter_id>/ecg-studies/<int:study_id>/analyze")
@require_role(Role.CLINICAL)
def analyze_ecg(encounter_id: int, study_id: int) -> tuple[Response, int]:
    body = request.get_json(silent=True) or {}
    model_ids = body.get("model_ids")
    if model_ids is not None and not isinstance(model_ids, list):
        return jsonify(error="model_ids must be a list of integers"), 400

    s = session()
    study = get_study_or_404(s, encounter_id=encounter_id, study_id=study_id)
    ensure_ai_analysis_consent(
        s,
        patient_id=uuid.UUID(str(study.patient_id)),
        user_id=current_user_id(),
    )

    model_dir = Path(current_app.config["MODEL_DIR"])
    storage_root = Path(current_app.config["STORAGE_DIR"])
    rows = analyze_study(
        s,
        study_id=study_id,
        user_id=current_user_id(),
        model_dir=model_dir,
        storage_root=storage_root,
        model_ids=model_ids,
        **request_ctx(),
    )
    s.commit()
    analyses = []
    for r in rows:
        model = s.get(ModelMetadata, r.model_metadata_id)
        if model is not None:
            analyses.append(analysis_to_out(r, model))
    return jsonify(analyses=analyses), 201


@bp.get("/<int:encounter_id>/ecg-studies/<int:study_id>/analyses")
@require_role(Role.ADMIN, Role.CLINICAL, Role.RESEARCHER)
def get_analyses(encounter_id: int, study_id: int) -> Response:
    s = session()
    rows = list(
        s.scalars(
            select(AIAnalysis)
            .where(AIAnalysis.ecg_study_id == study_id)
            .order_by(AIAnalysis.model_metadata_id)
        ).all()
    )
    items = []
    for r in rows:
        model = s.get(ModelMetadata, r.model_metadata_id)
        if model is not None:
            items.append(analysis_to_out(r, model))
    return jsonify(items=items)