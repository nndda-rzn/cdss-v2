"""ClinicalContext model tests (1:1 with Encounter)."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.clinical_context import ClinicalContext
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


def test_context_persists(session, seeded_admin):
    e = _encounter(session)
    c = ClinicalContext(
        encounter_id=e.id,
        symptom_chest_pain=True,
        pain_onset_minutes=120,
        recorded_by_user_id=1,
    )
    session.add(c)
    session.commit()
    fetched = session.scalar(select(ClinicalContext))
    assert fetched is not None
    assert fetched.symptom_chest_pain is True
    assert fetched.symptom_dyspnea is False
    assert fetched.pain_onset_minutes == 120


def test_context_unique_per_encounter(session, seeded_admin):
    e = _encounter(session)
    session.add(ClinicalContext(encounter_id=e.id, recorded_by_user_id=1))
    session.commit()
    session.add(ClinicalContext(encounter_id=e.id, recorded_by_user_id=1))
    with pytest.raises(IntegrityError):
        session.commit()
