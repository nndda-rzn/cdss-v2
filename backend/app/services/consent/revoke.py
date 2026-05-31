"""Revoke consent: append a 'revoked' row for a (patient, consent_type)."""
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models.consent import Consent


def revoke_consent(
    session: Session,
    *,
    patient_id: uuid.UUID,
    consent_type: str,
    user_id: int,
) -> Consent:
    entry = Consent(
        patient_id=patient_id,
        consent_type=consent_type,
        status="revoked",
        revoked_at=datetime.now(UTC),
        recorded_by_user_id=user_id,
    )
    session.add(entry)
    return entry
