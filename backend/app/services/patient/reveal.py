"""Patient detail reveal: decrypts T1 fields and logs each access (PHIAccessLog).

Used by the detail endpoint. Every non-null T1 field decrypted produces one
PHIAccessLog row so an auditor can see exactly which identifiers were viewed.
"""
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError
from app.db.models.patient import Patient
from app.services.audit.phi_access_writer import log_phi_access

_T1_FIELDS = ("name", "phone", "address")


def get_patient_detail(
    session: Session,
    *,
    patient_id: uuid.UUID,
    user_id: int,
    ip_address: str | None = None,
    purpose: str = "treatment",
) -> dict[str, Any]:
    patient = session.get(Patient, patient_id)
    if patient is None or patient.deleted_at is not None:
        raise NotFoundError(
            code="PATIENT_NOT_FOUND",
            message_id="Pasien tidak ditemukan",
            message_en="Patient not found",
        )

    values = {
        "name": patient.name_encrypted,
        "phone": patient.phone_encrypted,
        "address": patient.address_encrypted,
    }
    for field in _T1_FIELDS:
        if values[field] is not None:
            log_phi_access(
                session,
                user_id=user_id,
                patient_id=patient.id,
                accessed_field=field,
                purpose=purpose,
                ip_address=ip_address,
            )

    return {
        "id": str(patient.id),
        "mrn": patient.mrn,
        "name": patient.name_encrypted,
        "dob": patient.dob.isoformat(),
        "gender": patient.gender,
        "nik_last4": patient.nik_last4,
        "phone": patient.phone_encrypted,
        "address": patient.address_encrypted,
        "facility_id": patient.facility_id,
    }
