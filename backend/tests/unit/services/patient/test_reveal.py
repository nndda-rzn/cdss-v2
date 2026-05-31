"""Patient detail (reveal) service tests."""
import uuid
from datetime import date, datetime

import pytest
from sqlalchemy import select

from app.core.exceptions.base import NotFoundError
from app.db.models.patient import Patient
from app.db.models.phi_access_log import PHIAccessLog
from app.services.patient.reveal import get_patient_detail


def _add(session, *, name, gender="male", phone=None, address=None,
         mrn="MRN-P1-000001", facility_id=1, deleted=False):
    p = Patient(
        id=uuid.uuid4(),
        facility_id=facility_id,
        mrn=mrn,
        name_encrypted=name,
        dob=date(1965, 3, 12),
        gender=gender,
        phone_encrypted=phone,
        address_encrypted=address,
        deleted_at=datetime.now() if deleted else None,
    )
    session.add(p)
    session.commit()
    return p


def test_detail_returns_plaintext(session, seeded_admin):
    p = _add(session, name="Budi Santoso", phone="0812345678",
             address="Jl. Mawar 5")
    out = get_patient_detail(session, patient_id=p.id, user_id=1, ip_address="127.0.0.1")
    assert out["name"] == "Budi Santoso"
    assert out["phone"] == "0812345678"
    assert out["address"] == "Jl. Mawar 5"


def test_detail_writes_phi_access_log_per_field(session, seeded_admin):
    p = _add(session, name="Budi", phone="0812345678", address="Jl. Mawar 5")
    get_patient_detail(session, patient_id=p.id, user_id=1, ip_address="127.0.0.1")
    session.commit()
    rows = session.scalars(select(PHIAccessLog)).all()
    assert {r.accessed_field for r in rows} == {"name", "phone", "address"}


def test_detail_skips_log_for_null_fields(session, seeded_admin):
    p = _add(session, name="Budi")  # no phone, no address
    get_patient_detail(session, patient_id=p.id, user_id=1, ip_address="127.0.0.1")
    session.commit()
    rows = session.scalars(select(PHIAccessLog)).all()
    assert {r.accessed_field for r in rows} == {"name"}


def test_detail_deleted_patient_raises(session, seeded_admin):
    p = _add(session, name="Budi", deleted=True)
    with pytest.raises(NotFoundError):
        get_patient_detail(session, patient_id=p.id, user_id=1, ip_address="127.0.0.1")


def test_detail_unknown_patient_raises(session, seeded_admin):
    with pytest.raises(NotFoundError):
        get_patient_detail(
            session, patient_id=uuid.uuid4(), user_id=1, ip_address="127.0.0.1"
        )
