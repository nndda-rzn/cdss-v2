"""Patient search: filtered, masked, paginated list for a facility.

Returns masked T1 fields only (no decryption logged) since this is a list
view. Detail reveal (with PHIAccessLog) lives in reveal.py.
"""
from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.patient import Patient
from app.services.patient.mask import mask_name, mask_phone

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


def search_patients(
    session: Session,
    *,
    facility_id: int,
    mrn: str | None = None,
    nik_last4: str | None = None,
    dob: date | None = None,
    gender: str | None = None,
    page: int = 1,
    page_size: int = _DEFAULT_PAGE_SIZE,
) -> dict[str, Any]:
    page = max(page, 1)
    page_size = min(max(page_size, 1), _MAX_PAGE_SIZE)

    filters = [Patient.facility_id == facility_id, Patient.deleted_at.is_(None)]
    if mrn:
        filters.append(Patient.mrn == mrn)
    if nik_last4:
        filters.append(Patient.nik_last4 == nik_last4)
    if dob:
        filters.append(Patient.dob == dob)
    if gender:
        filters.append(Patient.gender == gender)

    total = session.scalar(
        select(func.count()).select_from(Patient).where(*filters)
    ) or 0

    rows = session.scalars(
        select(Patient)
        .where(*filters)
        .order_by(Patient.mrn)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        {
            "id": str(p.id),
            "mrn": p.mrn,
            "name_masked": mask_name(p.name_encrypted),
            "dob": p.dob.isoformat(),
            "gender": p.gender,
            "nik_last4": p.nik_last4,
            "phone_masked": mask_phone(p.phone_encrypted),
        }
        for p in rows
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}
