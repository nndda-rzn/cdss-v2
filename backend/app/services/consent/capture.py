"""Capture consent: append a 'given' row for a (patient, consent_type)."""
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models.consent import Consent


def capture_consent(
    session: Session,
    *,
    patient_id: uuid.UUID,
    consent_type: str,
    user_id: int,
    evidence_path: str | None = None,
) -> Consent:
    entry = Consent(
        patient_id=patient_id,
        consent_type=consent_type,
        status="given",
        given_at=datetime.now(UTC),
        evidence_path=evidence_path,
        recorded_by_user_id=user_id,
    )
    session.add(entry)
    return entry
