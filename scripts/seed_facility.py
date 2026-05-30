"""Seed a single HealthcareFacility row (idempotent on code)."""
import os
import sys

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


if __name__ == "__main__":
    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    def _ask(prompt: str, env_key: str, *, required: bool = True) -> str | None:
        if env_key in os.environ:
            return os.environ[env_key]
        try:
            value = input(prompt) or None
        except EOFError:
            value = None
        if value is None and required:
            raise SystemExit(f"Set {env_key} (non-interactive) or run in a terminal.")
        return value

    name = _ask("Facility name: ", "FACILITY_NAME")
    code = _ask("Facility code: ", "FACILITY_CODE")
    ftype = _ask("Facility type (puskesmas/pustu/klinik/rs_pratama): ", "FACILITY_TYPE")
    address = _ask("Address (optional): ", "FACILITY_ADDRESS", required=False)
    assert name is not None and code is not None and ftype is not None
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        seed_facility(s, name=name, code=code, facility_type=ftype, address=address)
        s.commit()
    print(f"Facility seeded: {code}", file=sys.stderr)
