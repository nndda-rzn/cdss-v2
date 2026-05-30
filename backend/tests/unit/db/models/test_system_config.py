from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.system_config import SystemConfig


def test_create_system_config(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'sc.db'}")
    Base.metadata.create_all(engine, tables=[SystemConfig.__table__])
    with Session(engine) as s:
        s.add(SystemConfig(key="enable_clinical_mode", value_json={"value": True}))
        s.commit()
    with Session(engine) as s:
        c = s.scalar(select(SystemConfig).where(SystemConfig.key == "enable_clinical_mode"))
        assert c.value_json == {"value": True}
