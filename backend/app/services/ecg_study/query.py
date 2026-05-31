"""List ECG studies for an encounter (newest first)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ecg_study import ECGStudy


def list_studies(session: Session, *, encounter_id: int) -> list[ECGStudy]:
    return list(
        session.scalars(
            select(ECGStudy)
            .where(ECGStudy.encounter_id == encounter_id)
            .order_by(ECGStudy.created_at.desc(), ECGStudy.id.desc())
        ).all()
    )
