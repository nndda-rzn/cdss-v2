"""AIAnalysis model tests (N:1 with ECGStudy and ModelMetadata)."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.model_metadata import ModelMetadata
from app.db.models.patient import Patient


def _study(session) -> ECGStudy:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    e = Encounter(patient_id=p.id, facility_id=1, attending_user_id=1)
    session.add(e)
    session.commit()
    study = ECGStudy(
        encounter_id=e.id,
        patient_id=e.patient_id,
        study_uid="ECG-P1-20260531-abcd",
        image_original_path="uploads/ecg/1/1/ECG-P1-20260531-abcd.jpg",
        image_quality_status="good",
        image_quality_score=0.85,
        image_quality_metrics_json={},
        recorded_by_user_id=1,
    )
    session.add(study)
    session.commit()
    return study


def _model(session) -> ModelMetadata:
    m = ModelMetadata(
        model_name="yolov8n-cls",
        model_version="v1.0",
        architecture="YOLOv8n",
        task_type="classification",
        input_size=224,
        model_file_path="yolov8n_cls/best.pt",
        model_checksum="abc",
        model_size_mb=2.83,
        class_names_json=["abnormal", "homi", "mi", "normal"],
        is_active=True,
    )
    session.add(m)
    session.commit()
    return m


def test_ai_analysis_persists(session, seeded_admin):
    study = _study(session)
    model = _model(session)
    analysis = AIAnalysis(
        ecg_study_id=study.id,
        model_metadata_id=model.id,
        predicted_class="mi",
        confidence_score=0.92,
        probability_json={
            "abnormal": 0.02, "homi": 0.03, "mi": 0.92, "normal": 0.03
        },
        status="success",
        device_used="cpu",
    )
    session.add(analysis)
    session.commit()
    row = session.scalar(select(AIAnalysis))
    assert row is not None
    assert row.ecg_study_id == study.id
    assert row.model_metadata_id == model.id
    assert row.predicted_class == "mi"
    assert row.confidence_score == 0.92
    assert row.probability_json["mi"] == 0.92
    assert row.status == "success"
    assert row.device_used == "cpu"
    assert row.created_at is not None


def test_ai_analysis_unique_study_model(session, seeded_admin):
    study = _study(session)
    model = _model(session)
    common = dict(
        ecg_study_id=study.id, model_metadata_id=model.id,
        predicted_class="mi", confidence_score=0.92,
        probability_json={}, status="success", device_used="cpu",
    )
    session.add(AIAnalysis(**common))
    session.commit()
    session.add(AIAnalysis(**common))
    with pytest.raises(IntegrityError):
        session.commit()
