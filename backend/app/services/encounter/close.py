"""Close an encounter (idempotent): set status=closed and ended_at."""
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError
from app.db.models.encounter import Encounter


def close_encounter(
    session: Session,
    *,
    encounter_id: int,
    user_id: int,
) -> Encounter:
    encounter = session.get(Encounter, encounter_id)
    if encounter is None:
        raise NotFoundError(
            code="ENCOUNTER_NOT_FOUND",
            message_id="Kunjungan tidak ditemukan",
            message_en="Encounter not found",
        )
    if encounter.status == "closed":
        return encounter  # idempotent no-op
    encounter.status = "closed"
    encounter.ended_at = datetime.now(UTC)
    return encounter
