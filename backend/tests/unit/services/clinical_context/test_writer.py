"""ClinicalContext writer service tests."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select

from app.core.exceptions.base import ConflictError
from app.db.models.clinical_context import ClinicalContext
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient
from app.services.clinical_context.writer import write_context


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


def test_write_context_persists(session, seeded_admin):
    e = _encounter(session)
    write_context(
        session,
        encounter_id=e.id,
        user_id=1,
        symptom_chest_pain=True,
        pain_onset_minutes=120,
    )
    session.commit()
    row = session.scalar(select(ClinicalContext))
    assert row is not None
    assert row.symptom_chest_pain is True
    assert row.pain_onset_minutes == 120


def test_write_context_duplicate_raises(session, seeded_admin):
    e = _encounter(session)
    write_context(session, encounter_id=e.id, user_id=1)
    session.commit()
    with pytest.raises(ConflictError) as exc:
        write_context(session, encounter_id=e.id, user_id=1)
    assert exc.value.code == "CLINICAL_CONTEXT_EXISTS"
