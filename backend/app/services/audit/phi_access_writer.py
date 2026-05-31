"""PHI access writer. Called when a T1 (direct identifier) field is revealed.

One row per field accessed, so an auditor can see exactly which identifiers a
user decrypted and when (UU PDP access logging).
"""
import uuid

from sqlalchemy.orm import Session

from app.db.models.phi_access_log import PHIAccessLog


def log_phi_access(
    session: Session,
    *,
    user_id: int,
    patient_id: uuid.UUID | str,
    accessed_field: str,
    access_type: str = "view",
    purpose: str = "treatment",
    ip_address: str | None = None,
) -> PHIAccessLog:
    entry = PHIAccessLog(
        user_id=user_id,
        patient_id=str(patient_id),
        access_type=access_type,
        purpose=purpose,
        accessed_field=accessed_field,
        ip_address=ip_address,
    )
    session.add(entry)
    return entry
