from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.user import User


def test_create_user(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'u.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(
            User(name="Dr A", email="a@x.id", password_hash="h", role="admin", facility_id=1)  # noqa: S106
        )
        s.commit()
    with Session(engine) as s:
        u = s.scalar(select(User).where(User.email == "a@x.id"))
        assert u.role == "admin"
        assert u.is_active is True
