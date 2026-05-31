"""Patient soft-delete: admin-only, requires a reason, writes an audit row.

Soft delete sets deleted_at; the row is retained for medical-record retention
(Permenkes). All read paths filter deleted_at IS NULL by default.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError, ValidationError
from app.db.models.patient import Patient
from app.services.audit.writer import write_audit


def soft_delete_patient(
    session: Session,
    *,
    patient_id: uuid.UUID,
    user_id: int,
    reason: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> None:
    if not reason or not reason.strip():
        raise ValidationError(
            code="PATIENT_DELETE_REASON_REQUIRED",
            message_id="Alasan penghapusan wajib diisi",
            message_en="A deletion reason is required",
        )

    patient = session.get(Patient, patient_id)
    if patient is None or patient.deleted_at is not None:
        raise NotFoundError(
            code="PATIENT_NOT_FOUND",
            message_id="Pasien tidak ditemukan",
            message_en="Patient not found",
        )

    patient.deleted_at = datetime.now(UTC)
    write_audit(
        session,
        facility_id=patient.facility_id,
        action="patient_soft_delete",
        user_id=user_id,
        entity_type="patient",
        description=f"soft-deleted patient {patient.mrn}: {reason}",
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
