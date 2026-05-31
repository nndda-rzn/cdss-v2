"""Query encounters by id, patient, or status."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.encounter import Encounter


def get_encounter(session: Session, encounter_id: int) -> Encounter | None:
    return session.get(Encounter, encounter_id)


def list_encounters_for_patient(
    session: Session,
    *,
    patient_id: uuid.UUID,
    status: str | None = None,
) -> list[Encounter]:
    stmt = select(Encounter).where(Encounter.patient_id == patient_id)
    if status:
        stmt = stmt.where(Encounter.status == status)
    stmt = stmt.order_by(Encounter.started_at.desc())
    return list(session.scalars(stmt).all())
