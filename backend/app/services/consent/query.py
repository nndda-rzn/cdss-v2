"""Query consent: the current status is the latest row for a (patient, type)."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.consent import Consent


def has_consent(
    session: Session,
    *,
    patient_id: uuid.UUID,
    consent_type: str,
) -> bool:
    """True if the most recent consent row for the type has status 'given'."""
    latest = session.scalar(
        select(Consent)
        .where(
            Consent.patient_id == patient_id,
            Consent.consent_type == consent_type,
        )
        .order_by(Consent.id.desc())
        .limit(1)
    )
    return latest is not None and latest.status == "given"
