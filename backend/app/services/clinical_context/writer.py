"""Write the 1:1 ClinicalContext for an encounter (reject if one exists)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import ConflictError
from app.db.models.clinical_context import ClinicalContext


def write_context(
    session: Session,
    *,
    encounter_id: int,
    user_id: int,
    symptom_chest_pain: bool = False,
    symptom_dyspnea: bool = False,
    symptom_palpitation: bool = False,
    symptom_syncope: bool = False,
    symptom_other: str | None = None,
    pain_onset_minutes: int | None = None,
    pain_duration_minutes: int | None = None,
) -> ClinicalContext:
    existing = session.scalar(
        select(ClinicalContext).where(
            ClinicalContext.encounter_id == encounter_id
        )
    )
    if existing is not None:
        raise ConflictError(
            code="CLINICAL_CONTEXT_EXISTS",
            message_id="Konteks klinis sudah ada untuk kunjungan ini",
            message_en="Clinical context already exists for this encounter",
        )

    context = ClinicalContext(
        encounter_id=encounter_id,
        symptom_chest_pain=symptom_chest_pain,
        symptom_dyspnea=symptom_dyspnea,
        symptom_palpitation=symptom_palpitation,
        symptom_syncope=symptom_syncope,
        symptom_other=symptom_other,
        pain_onset_minutes=pain_onset_minutes,
        pain_duration_minutes=pain_duration_minutes,
        recorded_by_user_id=user_id,
    )
    session.add(context)
    return context
