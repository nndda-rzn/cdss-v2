import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from scripts.seed_system_config import seed_system_config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.system_config import SystemConfig


def test_seed_defaults(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'sc.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_system_config(s)
        s.commit()
        keys = {c.key for c in s.scalars(select(SystemConfig)).all()}
        assert "enable_clinical_mode" in keys
        assert "default_model_id" in keys
        assert "nearest_pci_facility_distance_minutes" in keys


def test_seed_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'sc2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        seed_system_config(s)
        s.commit()
        seed_system_config(s)
        s.commit()
        assert s.query(SystemConfig).filter_by(key="enable_clinical_mode").count() == 1
