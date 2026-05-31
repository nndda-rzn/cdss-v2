import uuid
from datetime import date, timedelta

import pytest
from pydantic import ValidationError as PydanticError

from app.schemas.patient import PatientCreate, PatientMasked, PatientOut


def test_patient_create_valid():
    p = PatientCreate(
        name="Budi Santoso",
        dob=date(1965, 3, 12),
        gender="male",
        nik="3201123456780001",
        consent_data_use=True,
    )
    assert p.nik == "3201123456780001"


def test_patient_create_nik_optional():
    p = PatientCreate(
        name="Budi", dob=date(1990, 1, 1), gender="male", consent_data_use=True
    )
    assert p.nik is None


def test_patient_create_rejects_15_digit_nik():
    with pytest.raises(PydanticError):
        PatientCreate(
            name="Budi", dob=date(1990, 1, 1), gender="male",
            nik="320112345678000", consent_data_use=True,
        )


def test_patient_create_rejects_17_digit_nik():
    with pytest.raises(PydanticError):
        PatientCreate(
            name="Budi", dob=date(1990, 1, 1), gender="male",
            nik="32011234567800012", consent_data_use=True,
        )


def test_patient_create_rejects_future_dob():
    future = date.today() + timedelta(days=1)
    with pytest.raises(PydanticError):
        PatientCreate(
            name="Budi", dob=future, gender="male", consent_data_use=True
        )


def test_patient_create_rejects_short_name():
    with pytest.raises(PydanticError):
        PatientCreate(
            name="B", dob=date(1990, 1, 1), gender="male", consent_data_use=True
        )


def test_patient_create_requires_consent():
    with pytest.raises(PydanticError):
        PatientCreate(
            name="Budi", dob=date(1990, 1, 1), gender="male",
            consent_data_use=False,
        )


def test_patient_out_serializes():
    out = PatientOut(
        id=str(uuid.uuid4()),
        mrn="MRN-P1-000001",
        name="Budi Santoso",
        dob=date(1965, 3, 12),
        gender="male",
        nik_last4="0001",
        phone="0812345678",
        address="Jl. Mawar 5",
        facility_id=1,
    )
    assert out.model_dump()["mrn"] == "MRN-P1-000001"


def test_patient_masked_serializes():
    out = PatientMasked(
        id=str(uuid.uuid4()),
        mrn="MRN-P1-000001",
        name_masked="B*** S******",
        dob=date(1965, 3, 12),
        gender="male",
        nik_last4="0001",
        phone_masked="******5678",
    )
    assert out.model_dump()["name_masked"] == "B*** S******"
