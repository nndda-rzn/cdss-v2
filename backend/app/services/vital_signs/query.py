"""Query vital signs: list (DESC) and latest helper for the decision engine."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.vital_signs import VitalSigns


def list_vitals(session: Session, *, encounter_id: int) -> list[VitalSigns]:
    return list(
        session.scalars(
            select(VitalSigns)
            .where(VitalSigns.encounter_id == encounter_id)
            .order_by(VitalSigns.measured_at.desc(), VitalSigns.id.desc())
        ).all()
    )


def get_latest_vital(
    session: Session, *, encounter_id: int
) -> VitalSigns | None:
    return session.scalar(
        select(VitalSigns)
        .where(VitalSigns.encounter_id == encounter_id)
        .order_by(VitalSigns.measured_at.desc(), VitalSigns.id.desc())
        .limit(1)
    )
