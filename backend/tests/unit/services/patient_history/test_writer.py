"""PatientHistory writer service tests."""
import uuid
from datetime import date

from sqlalchemy import select

from app.db.models.patient import Patient
from app.db.models.patient_history import PatientHistory
from app.services.patient_history.writer import add_history


def _patient(session) -> Patient:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    return p


def test_add_history_persists(session, seeded_admin):
    p = _patient(session)
    add_history(
        session,
        patient_id=p.id,
        condition_code="MI",
        user_id=1,
        note="riwayat infark 2020",
    )
    session.commit()
    row = session.scalar(select(PatientHistory))
    assert row is not None
    assert row.condition_code == "MI"
    assert row.note_encrypted == "riwayat infark 2020"


def test_add_history_optional_fields_none(session, seeded_admin):
    p = _patient(session)
    add_history(session, patient_id=p.id, condition_code="DM", user_id=1)
    session.commit()
    row = session.scalar(select(PatientHistory))
    assert row.note_encrypted is None
    assert row.onset_date_approx is None
