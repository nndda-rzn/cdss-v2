import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_admin import seed_admin
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.security.password import verify_password
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User


def test_seed_admin_creates_admin(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'a.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.commit()
        seed_admin(
            s,
            name="Admin",
            email="admin@x.id",
            password="StrongPass1",  # noqa: S106
            facility_id=1,
            rounds=4,
        )
        s.commit()
        u = s.scalar(select(User).where(User.email == "admin@x.id"))
        assert u.role == "admin"
        assert verify_password("StrongPass1", u.password_hash)


def test_seed_admin_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'a2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.commit()
        seed_admin(
            s, name="Admin", email="admin@x.id", password="x", facility_id=1, rounds=4  # noqa: S106
        )
        s.commit()
        seed_admin(
            s, name="Admin", email="admin@x.id", password="x", facility_id=1, rounds=4  # noqa: S106
        )
        s.commit()
        assert s.query(User).filter_by(email="admin@x.id").count() == 1
