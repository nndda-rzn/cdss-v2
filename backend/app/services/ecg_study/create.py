"""Orchestrate an ECG upload: consent gate, validate, save, quality, persist."""
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.facility import HealthcareFacility
from app.services.audit.writer import write_audit
from app.services.ecg_study.consent_gate import ensure_ai_analysis_consent
from app.services.ecg_study.quality import assess_quality
from app.services.ecg_study.storage import (
    generate_study_uid,
    save_image,
    storage_path_for,
)
from app.services.ecg_study.upload import validate_image


def create_ecg_study(
    session: Session,
    *,
    encounter_id: int,
    user_id: int,
    storage_root: Path,
    file_bytes: bytes,
    content_type: str | None = None,
    device_info: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> ECGStudy:
    encounter = session.get(Encounter, encounter_id)
    if encounter is None:
        raise NotFoundError(
            code="ENCOUNTER_NOT_FOUND",
            message_id="Kunjungan tidak ditemukan",
            message_en="Encounter not found",
        )

    patient_id = uuid.UUID(str(encounter.patient_id))
    ensure_ai_analysis_consent(session, patient_id=patient_id, user_id=user_id)

    fmt, ext = validate_image(file_bytes, content_type=content_type)

    facility = session.get(HealthcareFacility, encounter.facility_id)
    facility_code = (
        facility.code if facility and facility.code else f"F{encounter.facility_id}"
    )
    study_uid = generate_study_uid(facility_code)

    rel_path = storage_path_for(
        facility_id=encounter.facility_id,
        encounter_id=encounter_id,
        study_uid=study_uid,
        ext=ext,
    )
    save_image(storage_root, rel_path, file_bytes)

    score, status, metrics = assess_quality(file_bytes, detailed=True)

    study = ECGStudy(
        encounter_id=encounter_id,
        patient_id=patient_id,
        study_uid=study_uid,
        image_original_path=rel_path,
        image_quality_status=status,
        image_quality_score=score,
        image_quality_metrics_json=metrics,
        recorded_by_user_id=user_id,
        device_info=device_info,
    )
    session.add(study)
    session.flush()
    write_audit(
        session,
        facility_id=encounter.facility_id,
        action="ecg_upload",
        user_id=user_id,
        entity_type="ecg_study",
        entity_id=study.id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    return study
