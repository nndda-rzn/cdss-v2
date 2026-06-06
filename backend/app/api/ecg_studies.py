"""ECG-study endpoints: upload (consent-gated) and list."""
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, request
from sqlalchemy.orm import Session

from app.api._shared import current_role, current_user_id, request_ctx, session
from app.core.exceptions.base import NotFoundError, ValidationError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ecg_study import ECGStudy
from app.schemas.ecg_study import ECGStudyOut
from app.services.ecg_study.create import create_ecg_study
from app.services.ecg_study.query import list_studies

bp = Blueprint("ecg_studies", __name__, url_prefix="/api/encounters")


def study_to_out(s: ECGStudy) -> dict[str, object]:
    return ECGStudyOut(
        id=s.id,
        encounter_id=s.encounter_id,
        patient_id=str(s.patient_id),
        study_uid=s.study_uid,
        image_original_path=s.image_original_path,
        image_processed_path=s.image_processed_path,
        image_quality_status=s.image_quality_status,
        image_quality_score=s.image_quality_score,
        image_quality_metrics_json=s.image_quality_metrics_json,
        acquired_at=s.acquired_at.isoformat(),
        recorded_by_user_id=s.recorded_by_user_id,
        device_info=s.device_info,
        created_at=s.created_at.isoformat(),
    ).model_dump()


def get_study_or_404(db: Session, *, encounter_id: int, study_id: int) -> ECGStudy:
    study = db.get(ECGStudy, study_id)
    if study is None or study.encounter_id != encounter_id:
        raise NotFoundError(
            code="ECG_STUDY_NOT_FOUND",
            message_id="Studi EKG tidak ditemukan",
            message_en="ECG study not found",
        )
    return study


@bp.post("/<int:encounter_id>/ecg-studies")
@require_role(Role.CLINICAL)
def create_ecg(encounter_id: int) -> tuple[Response, int]:
    s = session()
    file = request.files.get("file")
    if file is None:
        raise ValidationError(
            code="FILE_REQUIRED",
            message_id="Berkas EKG wajib diunggah",
            message_en="An ECG file is required",
        )
    file_bytes = file.read()
    storage_root = Path(current_app.config["STORAGE_DIR"])
    study = create_ecg_study(
        s,
        encounter_id=encounter_id,
        user_id=current_user_id(),
        storage_root=storage_root,
        file_bytes=file_bytes,
        content_type=file.mimetype,
        device_info=request.form.get("device_info"),
        **request_ctx(),
    )
    s.commit()
    return jsonify(study=study_to_out(study)), 201


@bp.get("/<int:encounter_id>/ecg-studies")
@require_role(Role.ADMIN, Role.CLINICAL, Role.RESEARCHER)
def get_ecg_studies(encounter_id: int) -> Response:
    s = session()
    rows = list_studies(s, encounter_id=encounter_id)
    role = current_role()
    items = []
    for study in rows:
        out = study_to_out(study)
        if role == "researcher":
            out.pop("patient_id", None)
            out.pop("device_info", None)
        items.append(out)
    return jsonify(items=items)


@bp.get("/<int:encounter_id>/ecg-studies/<int:study_id>")
@require_role(Role.ADMIN, Role.CLINICAL, Role.RESEARCHER)
def get_ecg_study(encounter_id: int, study_id: int) -> Response:
    s = session()
    study = get_study_or_404(s, encounter_id=encounter_id, study_id=study_id)
    out = study_to_out(study)
    if current_role() == "researcher":
        out.pop("patient_id", None)
        out.pop("device_info", None)
    return jsonify(study=out)