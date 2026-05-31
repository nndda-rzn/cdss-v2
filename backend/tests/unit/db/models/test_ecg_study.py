"""ECGStudy model tests (M:1 with Encounter)."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient


def _encounter(session) -> Encounter:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    e = Encounter(patient_id=p.id, facility_id=1, attending_user_id=1)
    session.add(e)
    session.commit()
    return e


def test_ecg_study_persists(session, seeded_admin):
    e = _encounter(session)
    study = ECGStudy(
        encounter_id=e.id,
        patient_id=e.patient_id,
        study_uid="ECG-P1-20260531-abcd",
        image_original_path="uploads/ecg/1/1/ECG-P1-20260531-abcd.jpg",
        image_quality_status="good",
        image_quality_score=0.85,
        image_quality_metrics_json={"blur": 120, "noise": 8,
                                    "brightness": 130, "contrast": 55},
        recorded_by_user_id=1,
    )
    session.add(study)
    session.commit()
    row = session.scalar(select(ECGStudy))
    assert row is not None
    assert row.study_uid == "ECG-P1-20260531-abcd"
    assert row.image_quality_score == 0.85
    assert row.image_quality_metrics_json["blur"] == 120
    assert row.acquired_at is not None
    assert row.created_at is not None


def test_ecg_study_unique_uid(session, seeded_admin):
    e = _encounter(session)
    common = dict(
        encounter_id=e.id, patient_id=e.patient_id,
        image_original_path="a.jpg", image_quality_status="good",
        image_quality_score=0.5, image_quality_metrics_json={},
        recorded_by_user_id=1,
    )
    session.add(ECGStudy(study_uid="ECG-DUP", **common))
    session.commit()
    session.add(ECGStudy(study_uid="ECG-DUP", **common))
    with pytest.raises(IntegrityError):
        session.commit()
