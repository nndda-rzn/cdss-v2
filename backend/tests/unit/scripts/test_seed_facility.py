import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_facility import seed_facility
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base


def test_seed_facility_creates(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fac.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        fac = seed_facility(
            s, name="Puskesmas Contoh", code="PUSK-001",
            facility_type="puskesmas", address="Jl. Contoh No. 1",
        )
        s.commit()
        assert fac.id is not None
        assert fac.code == "PUSK-001"


def test_seed_facility_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fac2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        f1 = seed_facility(s, name="A", code="X-001", facility_type="puskesmas")
        s.commit()
        f2 = seed_facility(s, name="B", code="X-001", facility_type="klinik")
        s.commit()
        assert f1.id == f2.id
        assert f2.name == "A"  # existing returned, not updated
