"""Patient registration: validate, encrypt, assign MRN, audit.

Consent capture (data_use) is wired in a later phase once the Consent model
exists; this service owns identity creation and the duplicate-NIK guard.
"""
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import ConflictError
from app.db.models.patient import Patient
from app.db.mrn_generator import generate_mrn
from app.services.audit.writer import write_audit


def _nik_exists(session: Session, *, facility_id: int, nik: str) -> bool:
    # Pass the raw NIK: the HashedString TypeDecorator hashes the bind param,
    # so the comparison matches the single-hashed value stored in the column.
    existing = session.scalar(
        select(Patient.id).where(
            Patient.facility_id == facility_id,
            Patient.nik_hash == nik,
        )
    )
    return existing is not None


def register_patient(
    session: Session,
    *,
    facility_id: int,
    facility_code: str,
    name: str,
    dob: date,
    gender: str,
    nik: str | None = None,
    phone: str | None = None,
    address: str | None = None,
    is_pseudonymized: bool = False,
    recorded_by_user_id: int,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> Patient:
    if nik and _nik_exists(session, facility_id=facility_id, nik=nik):
        raise ConflictError(
            code="PATIENT_NIK_DUPLICATE",
            message_id="NIK sudah terdaftar di faskes ini",
            message_en="NIK already registered at this facility",
        )

    patient = Patient(
        id=uuid.uuid4(),
        facility_id=facility_id,
        mrn=generate_mrn(session, facility_id=facility_id, facility_code=facility_code),
        nik_hash=nik if nik else None,
        nik_last4=nik[-4:] if nik else None,
        name_encrypted=name,
        dob=dob,
        gender=gender,
        phone_encrypted=phone,
        address_encrypted=address,
        is_pseudonymized=is_pseudonymized,
    )
    session.add(patient)
    session.flush()

    write_audit(
        session,
        facility_id=facility_id,
        action="patient_register",
        user_id=recorded_by_user_id,
        entity_type="patient",
        description=f"registered patient {patient.mrn}",
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    return patient
