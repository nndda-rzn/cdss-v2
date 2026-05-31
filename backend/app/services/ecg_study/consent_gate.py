"""Ensure ai_analysis consent before an ECG upload (progressive capture)."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import ValidationError
from app.db.models.consent import Consent
from app.services.consent.capture import capture_consent


def ensure_ai_analysis_consent(
    session: Session, *, patient_id: uuid.UUID, user_id: int
) -> None:
    """Auto-capture ai_analysis consent if none exists; honor explicit revoke."""
    latest = session.scalar(
        select(Consent)
        .where(
            Consent.patient_id == patient_id,
            Consent.consent_type == "ai_analysis",
        )
        .order_by(Consent.id.desc())
        .limit(1)
    )
    if latest is None:
        capture_consent(
            session, patient_id=patient_id,
            consent_type="ai_analysis", user_id=user_id,
        )
        return
    if latest.status == "revoked":
        raise ValidationError(
            code="CONSENT_REVOKED",
            message_id="Persetujuan analisis AI telah dicabut",
            message_en="ai_analysis consent has been revoked",
        )
    # "given" -> implicit no-op; "pending" -> capture an explicit grant.
    if latest.status == "pending":
        capture_consent(
            session, patient_id=patient_id,
            consent_type="ai_analysis", user_id=user_id,
        )
