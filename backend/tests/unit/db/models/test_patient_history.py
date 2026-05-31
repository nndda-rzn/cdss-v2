"""PatientHistory model tests."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.patient import Patient
from app.db.models.patient_history import PatientHistory


def _patient(session) -> Patient:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    return p


def test_history_persists_with_encrypted_note(session, seeded_admin):
    p = _patient(session)
    h = PatientHistory(
        patient_id=p.id,
        condition_code="MI",
        note_encrypted="riwayat infark 2020",
        recorded_by_user_id=1,
    )
    session.add(h)
    session.commit()

    fetched = session.scalar(select(PatientHistory))
    assert fetched is not None
    assert fetched.condition_code == "MI"
    assert fetched.note_encrypted == "riwayat infark 2020"


def test_history_invalid_condition_rejected(session, seeded_admin):
    p = _patient(session)
    h = PatientHistory(
        patient_id=p.id, condition_code="BOGUS", recorded_by_user_id=1
    )
    session.add(h)
    with pytest.raises(IntegrityError):
        session.commit()
