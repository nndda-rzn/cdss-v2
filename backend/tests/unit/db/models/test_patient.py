"""Patient model tests."""
import uuid
from datetime import date

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.db.models.patient import Patient


def test_patient_t1_fields_are_encrypted_at_rest(session, seeded_admin):
    """T1 fields (name, phone, address) stored as ciphertext, not plaintext."""
    p = Patient(
        id=uuid.uuid4(),
        facility_id=1,
        mrn="MRN-P1-000001",
        name_encrypted="Budi Santoso",
        dob=date(1965, 3, 12),
        gender="male",
        phone_encrypted="0812345678",
        address_encrypted="Jl. Mawar 5",
    )
    session.add(p)
    session.commit()

    # Read raw column bytes (text() bypasses the TypeDecorator decrypt).
    row = session.execute(
        text(
            "SELECT name_encrypted, phone_encrypted, address_encrypted "
            "FROM patient WHERE mrn = :mrn"
        ),
        {"mrn": "MRN-P1-000001"},
    ).one()
    raw = b"".join(bytes(v) for v in row if v is not None)
    assert b"Budi Santoso" not in raw
    assert b"0812345678" not in raw
    assert b"Jl. Mawar 5" not in raw

    # ORM read decrypts back to plaintext.
    fetched = session.scalar(select(Patient).where(Patient.mrn == "MRN-P1-000001"))
    assert fetched is not None
    assert fetched.name_encrypted == "Budi Santoso"
    assert fetched.phone_encrypted == "0812345678"
    assert fetched.address_encrypted == "Jl. Mawar 5"


def test_patient_nik_hash_partial_unique_per_facility(session, seeded_admin):
    """Duplicate NIK at the same facility violates the partial unique index."""
    p1 = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        nik_hash="3201123456780001", name_encrypted="A",
        dob=date(1990, 1, 1), gender="male",
    )
    p2 = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000002",
        nik_hash="3201123456780001", name_encrypted="B",
        dob=date(1990, 1, 1), gender="female",
    )
    session.add_all([p1, p2])
    with pytest.raises(IntegrityError):
        session.commit()


def test_patient_nik_nullable_allows_multiple(session, seeded_admin):
    """Patients without NIK can coexist (partial index ignores NULLs)."""
    p1 = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="A", dob=date(1990, 1, 1), gender="male",
    )
    p2 = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000002",
        name_encrypted="B", dob=date(1990, 1, 1), gender="female",
    )
    session.add_all([p1, p2])
    session.commit()
    assert session.scalar(select(Patient).where(Patient.mrn == "MRN-P1-000002")) is not None
