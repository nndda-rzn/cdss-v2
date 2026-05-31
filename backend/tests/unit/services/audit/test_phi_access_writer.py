"""PHIAccessLog writer tests."""
import uuid

from sqlalchemy import select

from app.db.models.phi_access_log import PHIAccessLog
from app.services.audit.phi_access_writer import log_phi_access


def test_log_phi_access_writes_row(session, seeded_admin):
    pid = uuid.uuid4()
    log_phi_access(
        session,
        user_id=1,
        patient_id=pid,
        accessed_field="name",
        ip_address="127.0.0.1",
    )
    session.commit()

    row = session.scalar(select(PHIAccessLog))
    assert row is not None
    assert row.user_id == 1
    assert row.patient_id == str(pid)
    assert row.accessed_field == "name"
    assert row.access_type == "view"
    assert row.purpose == "treatment"
    assert row.ip_address == "127.0.0.1"


def test_log_phi_access_multiple_fields(session, seeded_admin):
    pid = uuid.uuid4()
    for field in ("name", "phone", "address"):
        log_phi_access(
            session, user_id=1, patient_id=pid, accessed_field=field
        )
    session.commit()

    rows = session.scalars(select(PHIAccessLog)).all()
    assert len(rows) == 3
    assert {r.accessed_field for r in rows} == {"name", "phone", "address"}
