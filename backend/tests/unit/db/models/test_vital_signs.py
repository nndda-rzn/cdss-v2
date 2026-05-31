"""VitalSigns model tests (M:1 with Encounter)."""
import uuid
from datetime import date

from sqlalchemy import select

from app.db.models.encounter import Encounter
from app.db.models.patient import Patient
from app.db.models.vital_signs import VitalSigns


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


def test_vitals_persists(session, seeded_admin):
    e = _encounter(session)
    v = VitalSigns(
        encounter_id=e.id,
        bp_systolic=140,
        bp_diastolic=90,
        heart_rate=110,
        recorded_by_user_id=1,
    )
    session.add(v)
    session.commit()
    row = session.scalar(select(VitalSigns))
    assert row is not None
    assert row.bp_systolic == 140
    assert row.measured_at is not None


def test_vitals_multiple_per_encounter(session, seeded_admin):
    e = _encounter(session)
    session.add_all(
        [
            VitalSigns(encounter_id=e.id, heart_rate=100, recorded_by_user_id=1),
            VitalSigns(encounter_id=e.id, heart_rate=95, recorded_by_user_id=1),
        ]
    )
    session.commit()
    assert len(session.scalars(select(VitalSigns)).all()) == 2
