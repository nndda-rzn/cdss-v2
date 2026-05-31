"""Patient DTOs."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    dob: date
    gender: Literal["male", "female"]
    nik: str | None = Field(default=None, pattern=r"^\d{16}$")
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=300)
    is_pseudonymized: bool = False
    consent_data_use: Literal[True]

    @field_validator("dob")
    @classmethod
    def _dob_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("DOB tidak boleh di masa depan")
        return v

    @field_validator("nik", mode="before")
    @classmethod
    def _empty_nik_to_none(cls, v: str | None) -> str | None:
        return v or None


class PatientOut(BaseModel):
    id: str
    mrn: str
    name: str
    dob: date
    gender: str
    nik_last4: str | None = None
    phone: str | None = None
    address: str | None = None
    facility_id: int


class PatientMasked(BaseModel):
    id: str
    mrn: str
    name_masked: str
    dob: date
    gender: str
    nik_last4: str | None = None
    phone_masked: str | None = None


class DuplicateSuggestion(BaseModel):
    id: str
    mrn: str
    name_masked: str
    dob: date
    gender: str
