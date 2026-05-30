from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.audit_log import AuditLog
from app.db.models.facility import HealthcareFacility


def test_create_audit_log(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'al.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(AuditLog(facility_id=1, action="login", request_id="req-1"))
        s.commit()
    with Session(engine) as s:
        a = s.scalar(select(AuditLog).where(AuditLog.action == "login"))
        assert a.request_id == "req-1"
        assert a.user_id is None


def test_audit_log_allows_null_facility(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'al2.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(AuditLog(action="login_failed", request_id="req-2"))
        s.commit()
    with Session(engine) as s:
        a = s.scalar(select(AuditLog).where(AuditLog.action == "login_failed"))
        assert a.facility_id is None
