"""Create an encounter for a patient, gated on data_use consent (ADR-0008)."""
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions.base import ForbiddenError, NotFoundError
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient
from app.services.audit.writer import write_audit
from app.services.consent.query import has_consent


def create_encounter(
    session: Session,
    *,
    patient_id: uuid.UUID,
    facility_id: int,
    user_id: int,
    encounter_type: str = "rawat_jalan",
    chief_complaint: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> Encounter:
    patient = session.get(Patient, patient_id)
    if patient is None or patient.deleted_at is not None:
        raise NotFoundError(
            code="PATIENT_NOT_FOUND",
            message_id="Pasien tidak ditemukan",
            message_en="Patient not found",
        )
    if not has_consent(session, patient_id=patient_id, consent_type="data_use"):
        raise ForbiddenError(
            code="CONSENT_REQUIRED",
            message_id="Persetujuan penggunaan data diperlukan",
            message_en="data_use consent is required",
        )

    encounter = Encounter(
        patient_id=patient_id,
        facility_id=facility_id,
        attending_user_id=user_id,
        encounter_type=encounter_type,
        chief_complaint=chief_complaint,
    )
    session.add(encounter)
    session.flush()
    write_audit(
        session,
        facility_id=facility_id,
        action="encounter_create",
        user_id=user_id,
        entity_type="encounter",
        entity_id=encounter.id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    return encounter
