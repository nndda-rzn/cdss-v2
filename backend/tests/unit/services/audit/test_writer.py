from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.audit_log import AuditLog
from app.db.models.facility import HealthcareFacility
from app.services.audit.writer import write_audit


def test_write_audit_persists(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'aud.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.commit()
        write_audit(s, facility_id=1, action="login", user_id=None,
                    request_id="req-9", ip_address="127.0.0.1", user_agent="pytest")
        s.commit()
        row = s.scalar(select(AuditLog).where(AuditLog.action == "login"))
        assert row.request_id == "req-9"
        assert row.ip_address == "127.0.0.1"
