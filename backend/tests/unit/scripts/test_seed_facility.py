import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_facility import seed_facility
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility


def test_seed_facility_creates_row(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 's.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_facility(
            s,
            name="Puskesmas A",
            code="PKM-A",
            facility_type="puskesmas",
            address="Jl. Sehat 1",
        )
        s.commit()
        f = s.scalar(select(HealthcareFacility).where(HealthcareFacility.code == "PKM-A"))
        assert f is not None


def test_seed_facility_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 's2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_facility(s, name="A", code="PKM-A", facility_type="puskesmas", address="x")
        s.commit()
        seed_facility(s, name="A", code="PKM-A", facility_type="puskesmas", address="x")
        s.commit()
        assert s.query(HealthcareFacility).filter_by(code="PKM-A").count() == 1
