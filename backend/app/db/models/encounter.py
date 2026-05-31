"""Encounter model (a patient visit; ECG studies attach to it in Sprint 2B)."""
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

_TYPES = ("rawat_jalan", "igd")
_STATUSES = ("open", "closed")


class Encounter(Base):
    __tablename__ = "encounter"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("patient.id"), index=True
    )
    facility_id: Mapped[int] = mapped_column(
        ForeignKey("healthcare_facility.id"), index=True
    )
    attending_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True
    )
    encounter_type: Mapped[str] = mapped_column(
        Enum(*_TYPES, name="encounter_type_enum", create_constraint=True),
        default="rawat_jalan",
    )
    status: Mapped[str] = mapped_column(
        Enum(*_STATUSES, name="encounter_status_enum", create_constraint=True),
        default="open",
    )
    chief_complaint: Mapped[str | None] = mapped_column(Text, default=None)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    __table_args__ = (
        Index("ix_encounter_patient_status", "patient_id", "status"),
    )
