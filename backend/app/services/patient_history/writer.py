"""Append a clinical history entry for a patient (append-only)."""
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.db.models.patient_history import PatientHistory


def add_history(
    session: Session,
    *,
    patient_id: uuid.UUID,
    condition_code: str,
    user_id: int,
    onset_date_approx: date | None = None,
    note: str | None = None,
) -> PatientHistory:
    entry = PatientHistory(
        patient_id=patient_id,
        condition_code=condition_code,
        onset_date_approx=onset_date_approx,
        note_encrypted=note,
        recorded_by_user_id=user_id,
    )
    session.add(entry)
    return entry
