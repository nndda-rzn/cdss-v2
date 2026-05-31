"""Encounter model tests."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.encounter import Encounter
from app.db.models.patient import Patient


def _patient(session) -> Patient:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    return p


def test_encounter_persists_with_defaults(session, seeded_admin):
    p = _patient(session)
    e = Encounter(
        patient_id=p.id,
        facility_id=1,
        attending_user_id=1,
        chief_complaint="Nyeri dada",
    )
    session.add(e)
    session.commit()
    fetched = session.scalar(select(Encounter))
    assert fetched is not None
    assert fetched.status == "open"
    assert fetched.encounter_type == "rawat_jalan"
    assert fetched.started_at is not None


def test_encounter_invalid_type_rejected(session, seeded_admin):
    p = _patient(session)
    e = Encounter(
        patient_id=p.id, facility_id=1, attending_user_id=1,
        encounter_type="bogus",
    )
    session.add(e)
    with pytest.raises(IntegrityError):
        session.commit()
