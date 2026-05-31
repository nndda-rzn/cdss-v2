"""Encounter service tests."""
import uuid
from datetime import date

import pytest

from app.core.exceptions.base import ForbiddenError, NotFoundError
from app.db.models.patient import Patient
from app.services.consent.capture import capture_consent
from app.services.encounter.close import close_encounter
from app.services.encounter.create import create_encounter


def _patient(session, *, with_consent=True) -> Patient:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    if with_consent:
        capture_consent(
            session, patient_id=p.id, consent_type="data_use", user_id=1
        )
        session.commit()
    return p


def test_create_encounter_open(session, seeded_admin):
    p = _patient(session)
    e = create_encounter(
        session, patient_id=p.id, facility_id=1, user_id=1,
        encounter_type="rawat_jalan", chief_complaint="Nyeri dada",
    )
    session.commit()
    assert e.status == "open"
    assert e.patient_id == p.id


def test_create_blocks_without_consent(session, seeded_admin):
    p = _patient(session, with_consent=False)
    with pytest.raises(ForbiddenError) as exc:
        create_encounter(session, patient_id=p.id, facility_id=1, user_id=1)
    assert exc.value.code == "CONSENT_REQUIRED"


def test_create_unknown_patient_raises(session, seeded_admin):
    with pytest.raises(NotFoundError):
        create_encounter(
            session, patient_id=uuid.uuid4(), facility_id=1, user_id=1
        )


def test_close_encounter_sets_ended(session, seeded_admin):
    p = _patient(session)
    e = create_encounter(session, patient_id=p.id, facility_id=1, user_id=1)
    session.commit()
    close_encounter(session, encounter_id=e.id, user_id=1)
    session.commit()
    assert e.status == "closed"
    assert e.ended_at is not None


def test_close_idempotent(session, seeded_admin):
    p = _patient(session)
    e = create_encounter(session, patient_id=p.id, facility_id=1, user_id=1)
    session.commit()
    close_encounter(session, encounter_id=e.id, user_id=1)
    session.commit()
    # Second close is a no-op, no error
    close_encounter(session, encounter_id=e.id, user_id=1)
    session.commit()
    assert e.status == "closed"


def test_close_unknown_raises(session, seeded_admin):
    with pytest.raises(NotFoundError):
        close_encounter(session, encounter_id=9999, user_id=1)
