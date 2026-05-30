from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.phi_access_log import PHIAccessLog
from app.db.models.user import User


def test_create_phi_access_log(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'phi.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(
            User(
                id=1,
                name="A",
                email="a@x.id",
                password_hash="h",  # noqa: S106
                role="clinician",
                facility_id=1,
            )
        )
        s.add(PHIAccessLog(user_id=1, patient_id="p-uuid", access_type="view",
                           purpose="treatment", accessed_field="name"))
        s.commit()
    with Session(engine) as s:
        log = s.scalar(select(PHIAccessLog).where(PHIAccessLog.user_id == 1))
        assert log.access_type == "view"
        assert log.purpose == "treatment"
