"""Seed default SystemConfig rows (idempotent per key)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.system_config import SystemConfig

_DEFAULTS: dict[str, dict[str, object]] = {
    "enable_clinical_mode": {"value": True},
    "default_model_id": {"value": None},
    "nearest_pci_facility_distance_minutes": {"value": None},
}


def seed_system_config(session: Session) -> None:
    for key, value in _DEFAULTS.items():
        existing = session.scalar(select(SystemConfig).where(SystemConfig.key == key))
        if existing is None:
            session.add(SystemConfig(key=key, value_json=value))


if __name__ == "__main__":
    import sys

    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        seed_system_config(s)
        s.commit()
    print("System config seeded", file=sys.stderr)
