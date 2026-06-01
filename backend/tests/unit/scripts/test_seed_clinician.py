import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_clinician import seed_clinical_user
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.security.password import verify_password
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User


def test_seed_clinical_user_creates_user(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'c.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(
            HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas")
        )
        s.commit()
        seed_clinical_user(
            s,
            name="Dr. Demo",
            email="dokter@x.id",
            password="DokterDemo1!",  # noqa: S106
            facility_id=1,
            role="clinician",
            rounds=4,
        )
        s.commit()
        u = s.scalar(select(User).where(User.email == "dokter@x.id"))
        assert u is not None
        assert u.role == "clinician"
        assert verify_password("DokterDemo1!", u.password_hash)


def test_seed_clinical_user_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'c2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(
            HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas")
        )
        s.commit()
        seed_clinical_user(
            s,
            name="Nurse",
            email="perawat@x.id",
            password="x",  # noqa: S106
            facility_id=1,
            role="nurse",
            rounds=4,
        )
        s.commit()
        seed_clinical_user(
            s,
            name="Nurse 2",
            email="perawat@x.id",
            password="y",  # noqa: S106
            facility_id=1,
            role="nurse",
            rounds=4,
        )
        s.commit()
        assert s.query(User).filter_by(email="perawat@x.id").count() == 1
        # Original user kept (first seed).
        u = s.scalar(select(User).where(User.email == "perawat@x.id"))
        assert verify_password("x", u.password_hash)
