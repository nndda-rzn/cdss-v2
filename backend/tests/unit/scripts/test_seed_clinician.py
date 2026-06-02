import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_clinician import seed_clinical_user
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility


def _seed_facility(session):
    fac = HealthcareFacility(name="Test", code="T-CL", facility_type="puskesmas")
    session.add(fac)
    session.flush()
    return fac


def test_seed_clinician_creates(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'clin.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        fac = _seed_facility(s)
        user = seed_clinical_user(
            s, name="Dr. Contoh", email="clin@test.local",
            password="pass123", facility_id=fac.id, role="clinician",  # noqa: S106
        )
        s.commit()
        assert user.id is not None
        assert user.role == "clinician"
        assert user.facility_id == fac.id


def test_seed_clinician_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'clin2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        fac = _seed_facility(s)
        u1 = seed_clinical_user(
            s, name="A", email="c@t.local", password="p",  # noqa: S106
            facility_id=fac.id, role="clinician",
        )
        s.commit()
        u2 = seed_clinical_user(
            s, name="B", email="c@t.local", password="p",  # noqa: S106
            facility_id=fac.id, role="nurse",
        )
        s.commit()
        assert u1.id == u2.id
