"""Capture a vital-signs measurement (at least one field must be present)."""
from sqlalchemy.orm import Session

from app.core.exceptions.base import ValidationError
from app.db.models.vital_signs import VitalSigns

_VITAL_FIELDS = (
    "bp_systolic",
    "bp_diastolic",
    "heart_rate",
    "respiratory_rate",
    "spo2",
    "temperature",
    "weight",
    "height",
)


def capture_vitals(
    session: Session,
    *,
    encounter_id: int,
    user_id: int,
    bp_systolic: int | None = None,
    bp_diastolic: int | None = None,
    heart_rate: int | None = None,
    respiratory_rate: int | None = None,
    spo2: int | None = None,
    temperature: float | None = None,
    weight: float | None = None,
    height: float | None = None,
) -> VitalSigns:
    values = {
        "bp_systolic": bp_systolic,
        "bp_diastolic": bp_diastolic,
        "heart_rate": heart_rate,
        "respiratory_rate": respiratory_rate,
        "spo2": spo2,
        "temperature": temperature,
        "weight": weight,
        "height": height,
    }
    if all(values[f] is None for f in _VITAL_FIELDS):
        raise ValidationError(
            code="VITALS_EMPTY",
            message_id="Minimal satu tanda vital harus diisi",
            message_en="At least one vital sign must be provided",
        )

    vital = VitalSigns(
        encounter_id=encounter_id, recorded_by_user_id=user_id, **values
    )
    session.add(vital)
    return vital
