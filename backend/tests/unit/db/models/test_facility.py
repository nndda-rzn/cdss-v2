from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility


def test_create_facility(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'f.db'}")
    Base.metadata.create_all(engine, tables=[HealthcareFacility.__table__])
    with Session(engine) as s:
        s.add(HealthcareFacility(name="Puskesmas A", code="PKM-A", facility_type="puskesmas"))
        s.commit()
    with Session(engine) as s:
        f = s.scalar(select(HealthcareFacility).where(HealthcareFacility.code == "PKM-A"))
        assert f.name == "Puskesmas A"
        assert f.is_active is True
