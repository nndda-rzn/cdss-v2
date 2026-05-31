"""Patient register service tests."""
from datetime import date

import pytest
from sqlalchemy import select

from app.core.exceptions.base import ConflictError
from app.db.models.audit_log import AuditLog
from app.db.models.patient import Patient
from app.services.patient.register import register_patient


def test_register_creates_patient_with_mrn_and_encryption(session, seeded_admin):
    p = register_patient(
        session,
        facility_id=1,
        facility_code="P1",
        name="Budi Santoso",
        dob=date(1965, 3, 12),
        gender="male",
        nik="3201123456780001",
        phone="0812345678",
        address="Jl. Mawar 5",
        recorded_by_user_id=1,
    )
    session.commit()

    assert p.mrn == "MRN-P1-000001"
    assert p.nik_last4 == "0001"
    assert p.name_encrypted == "Budi Santoso"
    fetched = session.scalar(select(Patient).where(Patient.id == p.id))
    assert fetched is not None


def test_register_without_nik_succeeds(session, seeded_admin):
    p = register_patient(
        session,
        facility_id=1,
        facility_code="P1",
        name="Siti Aminah",
        dob=date(1980, 5, 1),
        gender="female",
        recorded_by_user_id=1,
    )
    session.commit()
    assert p.nik_hash is None
    assert p.nik_last4 is None


def test_register_duplicate_nik_raises_conflict(session, seeded_admin):
    register_patient(
        session, facility_id=1, facility_code="P1", name="A",
        dob=date(1990, 1, 1), gender="male", nik="3201123456780001",
        recorded_by_user_id=1,
    )
    session.commit()
    with pytest.raises(ConflictError) as exc:
        register_patient(
            session, facility_id=1, facility_code="P1", name="B",
            dob=date(1991, 2, 2), gender="female", nik="3201123456780001",
            recorded_by_user_id=1,
        )
    assert exc.value.code == "PATIENT_NIK_DUPLICATE"


def test_register_writes_audit(session, seeded_admin):
    register_patient(
        session, facility_id=1, facility_code="P1", name="A",
        dob=date(1990, 1, 1), gender="male", recorded_by_user_id=1,
    )
    session.commit()
    row = session.scalar(
        select(AuditLog).where(AuditLog.action == "patient_register")
    )
    assert row is not None


def test_register_captures_data_use_consent(session, seeded_admin):
    from app.services.consent.query import has_consent

    p = register_patient(
        session, facility_id=1, facility_code="P1", name="A",
        dob=date(1990, 1, 1), gender="male", recorded_by_user_id=1,
    )
    session.commit()
    assert has_consent(session, patient_id=p.id, consent_type="data_use") is True
