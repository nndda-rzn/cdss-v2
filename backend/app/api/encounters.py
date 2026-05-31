"""Encounter endpoints: create (consent-gated), detail, close."""
import uuid
from pathlib import Path
from typing import cast

from flask import Blueprint, Response, current_app, g, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.clinical_context import ClinicalContext
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.model_metadata import ModelMetadata
from app.extensions import db
from app.schemas.ai_analysis import AIAnalysisOut
from app.schemas.ecg_study import ECGStudyOut
from app.schemas.encounter import EncounterCreate, EncounterOut
from app.services.clinical_context.writer import write_context
from app.services.ecg_study.consent_gate import ensure_ai_analysis_consent
from app.services.ecg_study.create import create_ecg_study
from app.services.ecg_study.query import list_studies
from app.services.encounter.close import close_encounter
from app.services.encounter.create import create_encounter
from app.services.inference.orchestrate import analyze_study
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


def _study_to_out(s: ECGStudy) -> dict[str, object]:
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


def _analysis_to_out(a: AIAnalysis, model: ModelMetadata) -> dict[str, object]:
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


@bp.post("/<int:encounter_id>/ecg-studies")
@require_role(Role.CLINICIAN, Role.NURSE)
def create_ecg(encounter_id: int) -> tuple[Response, int]:
    session = _session()
    file = request.files.get("file")
    if file is None:
        from app.core.exceptions.base import ValidationError

        raise ValidationError(
            code="FILE_REQUIRED",
            message_id="Berkas EKG wajib diunggah",
            message_en="An ECG file is required",
        )
    file_bytes = file.read()
    storage_root = Path(current_app.config["STORAGE_DIR"])
    study = create_ecg_study(
        session,
        encounter_id=encounter_id,
        user_id=_user_id(),
        storage_root=storage_root,
        file_bytes=file_bytes,
        content_type=file.mimetype,
        device_info=request.form.get("device_info"),
        **_ctx(),
    )
    session.commit()
    return jsonify(study=_study_to_out(study)), 201


@bp.get("/<int:encounter_id>/ecg-studies")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_ecg_studies(encounter_id: int) -> Response:
    from flask_jwt_extended import get_jwt

    session = _session()
    rows = list_studies(session, encounter_id=encounter_id)
    role = get_jwt().get("role")
    items = []
    for s in rows:
        out = _study_to_out(s)
        if role == "researcher":
            out.pop("patient_id", None)
            out.pop("device_info", None)
        items.append(out)
    return jsonify(items=items)


def _get_study_or_404(session: Session, *, encounter_id: int, study_id: int) -> ECGStudy:
    study = session.get(ECGStudy, study_id)
    if study is None or study.encounter_id != encounter_id:
        raise NotFoundError(
            code="ECG_STUDY_NOT_FOUND",
            message_id="Studi EKG tidak ditemukan",
            message_en="ECG study not found",
        )
    return study


@bp.post("/<int:encounter_id>/ecg-studies/<int:study_id>/analyze")
@require_role(Role.CLINICIAN, Role.NURSE)
def analyze_ecg(encounter_id: int, study_id: int) -> tuple[Response, int]:
    session = _session()
    study = _get_study_or_404(session, encounter_id=encounter_id, study_id=study_id)
    ensure_ai_analysis_consent(
        session,
        patient_id=uuid.UUID(str(study.patient_id)),
        user_id=_user_id(),
    )
    model_dir = Path(current_app.config["MODEL_DIR"])
    storage_root = Path(current_app.config["STORAGE_DIR"])
    rows = analyze_study(
        session,
        study_id=study_id,
        user_id=_user_id(),
        model_dir=model_dir,
        storage_root=storage_root,
        **_ctx(),
    )
    session.commit()
    analyses = []
    for r in rows:
        model = session.get(ModelMetadata, r.model_metadata_id)
        if model is not None:
            analyses.append(_analysis_to_out(r, model))
    return jsonify(analyses=analyses), 201


@bp.get("/<int:encounter_id>/ecg-studies/<int:study_id>/analyses")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_analyses(encounter_id: int, study_id: int) -> Response:
    session = _session()
    rows = list(
        session.scalars(
            select(AIAnalysis)
            .where(AIAnalysis.ecg_study_id == study_id)
            .order_by(AIAnalysis.model_metadata_id)
        ).all()
    )
    items = []
    for r in rows:
        model = session.get(ModelMetadata, r.model_metadata_id)
        if model is not None:
            items.append(_analysis_to_out(r, model))
    return jsonify(items=items)
