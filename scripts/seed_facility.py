"""Seed a single HealthcareFacility row (idempotent on code)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.facility import HealthcareFacility


def seed_facility(
    session: Session,
    *,
    name: str,
    code: str,
    facility_type: str,
    address: str | None = None,
) -> HealthcareFacility:
    existing = session.scalar(
        select(HealthcareFacility).where(HealthcareFacility.code == code)
    )
    if existing is not None:
        return existing
    facility = HealthcareFacility(
        name=name, code=code, facility_type=facility_type, address=address
    )
    session.add(facility)
    return facility
