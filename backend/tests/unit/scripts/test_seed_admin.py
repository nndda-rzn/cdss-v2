import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_admin import seed_admin
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility


def _seed_facility(session):
    """Helper: create a facility for FK constraint."""
    fac = HealthcareFacility(name="Test", code="T-ADM", facility_type="puskesmas")
    session.add(fac)
    session.flush()
    return fac


def test_seed_admin_creates_user(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'admin.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        fac = _seed_facility(s)
        user = seed_admin(
            s, name="Admin", email="admin@test.local",
            password="pass123", facility_id=fac.id,  # noqa: S106
        )
        s.commit()
        assert user.id is not None
        assert user.role == "admin"


def test_seed_admin_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'admin2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        fac = _seed_facility(s)
        u1 = seed_admin(s, name="A", email="a@t.local", password="p", facility_id=fac.id)  # noqa: S106
        s.commit()
        u2 = seed_admin(s, name="B", email="a@t.local", password="p", facility_id=fac.id)  # noqa: S106
        s.commit()
        assert u1.id == u2.id
