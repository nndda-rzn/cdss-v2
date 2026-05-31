"""ai_analysis consent gate tests."""
import uuid
from datetime import UTC, datetime

import pytest

from app.core.exceptions.base import ValidationError
from app.db.models.consent import Consent
from app.services.consent.query import has_consent
from app.services.ecg_study.consent_gate import ensure_ai_analysis_consent


def _pid(session, seeded_admin) -> uuid.UUID:
    from datetime import date

    from app.db.models.patient import Patient

    p = Patient(id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
                name_encrypted="Budi", dob=date(1965, 3, 12), gender="male")
    session.add(p)
    session.commit()
    return p.id


def test_auto_captures_when_absent(session, seeded_admin):
    pid = _pid(session, seeded_admin)
    ensure_ai_analysis_consent(session, patient_id=pid, user_id=1)
    session.commit()
    assert has_consent(session, patient_id=pid, consent_type="ai_analysis")


def test_noop_when_already_given(session, seeded_admin):
    pid = _pid(session, seeded_admin)
    session.add(Consent(patient_id=pid, consent_type="ai_analysis",
                        status="given", given_at=datetime.now(UTC),
                        recorded_by_user_id=1))
    session.commit()
    ensure_ai_analysis_consent(session, patient_id=pid, user_id=1)
    session.commit()
    rows = session.query(Consent).filter_by(patient_id=pid).count()
    assert rows == 1  # no duplicate captured


def test_raises_when_revoked(session, seeded_admin):
    pid = _pid(session, seeded_admin)
    session.add(Consent(patient_id=pid, consent_type="ai_analysis",
                        status="revoked", revoked_at=datetime.now(UTC),
                        recorded_by_user_id=1))
    session.commit()
    with pytest.raises(ValidationError) as exc:
        ensure_ai_analysis_consent(session, patient_id=pid, user_id=1)
    assert exc.value.code == "CONSENT_REVOKED"
