"""Consent service tests."""
import uuid
from datetime import date

from sqlalchemy import select

from app.db.models.consent import Consent
from app.db.models.patient import Patient
from app.services.consent.capture import capture_consent
from app.services.consent.query import has_consent
from app.services.consent.revoke import revoke_consent


def _patient(session) -> Patient:
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.commit()
    return p


def test_capture_consent_given(session, seeded_admin):
    p = _patient(session)
    capture_consent(
        session, patient_id=p.id, consent_type="data_use", user_id=1
    )
    session.commit()
    row = session.scalar(select(Consent))
    assert row.status == "given"
    assert row.given_at is not None


def test_has_consent_true_when_given(session, seeded_admin):
    p = _patient(session)
    capture_consent(
        session, patient_id=p.id, consent_type="data_use", user_id=1
    )
    session.commit()
    assert has_consent(session, patient_id=p.id, consent_type="data_use") is True


def test_has_consent_false_when_absent(session, seeded_admin):
    p = _patient(session)
    assert has_consent(session, patient_id=p.id, consent_type="ai_analysis") is False


def test_revoke_then_has_consent_false(session, seeded_admin):
    p = _patient(session)
    capture_consent(
        session, patient_id=p.id, consent_type="data_use", user_id=1
    )
    session.commit()
    revoke_consent(
        session, patient_id=p.id, consent_type="data_use", user_id=1
    )
    session.commit()
    assert has_consent(session, patient_id=p.id, consent_type="data_use") is False


def test_has_consent_uses_latest_status(session, seeded_admin):
    p = _patient(session)
    capture_consent(session, patient_id=p.id, consent_type="data_use", user_id=1)
    session.commit()
    revoke_consent(session, patient_id=p.id, consent_type="data_use", user_id=1)
    session.commit()
    capture_consent(session, patient_id=p.id, consent_type="data_use", user_id=1)
    session.commit()
    # Latest row is "given" again
    assert has_consent(session, patient_id=p.id, consent_type="data_use") is True
