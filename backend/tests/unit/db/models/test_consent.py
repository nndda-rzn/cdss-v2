"""Consent model tests."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.models.consent import Consent
from app.db.models.patient import Patient


def _patient(session) -> Patient:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    return p


def test_consent_persists(session, seeded_admin):
    p = _patient(session)
    c = Consent(
        patient_id=p.id,
        consent_type="data_use",
        status="given",
        recorded_by_user_id=1,
    )
    session.add(c)
    session.commit()
    fetched = session.scalar(select(Consent))
    assert fetched is not None
    assert fetched.consent_type == "data_use"
    assert fetched.status == "given"


def test_consent_multiple_rows_per_patient(session, seeded_admin):
    p = _patient(session)
    session.add_all(
        [
            Consent(patient_id=p.id, consent_type="data_use", status="given",
                    recorded_by_user_id=1),
            Consent(patient_id=p.id, consent_type="ai_analysis", status="pending",
                    recorded_by_user_id=1),
        ]
    )
    session.commit()
    assert len(session.scalars(select(Consent)).all()) == 2


def test_consent_invalid_type_rejected(session, seeded_admin):
    p = _patient(session)
    session.add(
        Consent(patient_id=p.id, consent_type="bogus", status="given",
                recorded_by_user_id=1)
    )
    with pytest.raises(IntegrityError):
        session.commit()
