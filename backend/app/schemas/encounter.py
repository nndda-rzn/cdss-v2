"""Encounter DTOs."""
from typing import Literal

from pydantic import BaseModel


class EncounterCreate(BaseModel):
    patient_id: str
    encounter_type: Literal["rawat_jalan", "igd"] = "rawat_jalan"
    chief_complaint: str | None = None


class EncounterOut(BaseModel):
    id: int
    patient_id: str
    facility_id: int
    attending_user_id: int
    encounter_type: str
    status: str
    chief_complaint: str | None = None
    started_at: str
    ended_at: str | None = None
