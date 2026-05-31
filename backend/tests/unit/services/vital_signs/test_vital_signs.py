"""VitalSigns service tests."""
import uuid
from datetime import date

import pytest

from app.core.exceptions.base import ValidationError
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient
from app.services.vital_signs.capture import capture_vitals
from app.services.vital_signs.query import get_latest_vital, list_vitals


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


def test_capture_vitals_persists(session, seeded_admin):
    e = _encounter(session)
    v = capture_vitals(
        session, encounter_id=e.id, user_id=1, bp_systolic=140, bp_diastolic=90
    )
    session.commit()
    assert v.bp_systolic == 140


def test_capture_requires_at_least_one_vital(session, seeded_admin):
    e = _encounter(session)
    with pytest.raises(ValidationError) as exc:
        capture_vitals(session, encounter_id=e.id, user_id=1)
    assert exc.value.code == "VITALS_EMPTY"


def test_list_vitals_desc_by_measured(session, seeded_admin):
    e = _encounter(session)
    capture_vitals(session, encounter_id=e.id, user_id=1, heart_rate=100)
    session.commit()
    capture_vitals(session, encounter_id=e.id, user_id=1, heart_rate=95)
    session.commit()
    rows = list_vitals(session, encounter_id=e.id)
    assert len(rows) == 2
    # Most recent (by id as tiebreaker) first
    assert rows[0].measured_at >= rows[1].measured_at


def test_get_latest_vital(session, seeded_admin):
    e = _encounter(session)
    capture_vitals(session, encounter_id=e.id, user_id=1, heart_rate=100)
    session.commit()
    latest = capture_vitals(session, encounter_id=e.id, user_id=1, heart_rate=95)
    session.commit()
    fetched = get_latest_vital(session, encounter_id=e.id)
    assert fetched is not None
    assert fetched.id == latest.id


def test_get_latest_vital_none_when_empty(session, seeded_admin):
    e = _encounter(session)
    assert get_latest_vital(session, encounter_id=e.id) is None
