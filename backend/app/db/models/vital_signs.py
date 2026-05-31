"""VitalSigns model (M:1 with Encounter; latest-wins for decision engine)."""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow


class VitalSigns(Base):
    __tablename__ = "vital_signs"

    id: Mapped[int] = mapped_column(primary_key=True)
    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounter.id"), index=True
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
    bp_systolic: Mapped[int | None] = mapped_column(Integer, default=None)
    bp_diastolic: Mapped[int | None] = mapped_column(Integer, default=None)
    heart_rate: Mapped[int | None] = mapped_column(Integer, default=None)
    respiratory_rate: Mapped[int | None] = mapped_column(Integer, default=None)
    spo2: Mapped[int | None] = mapped_column(Integer, default=None)
    temperature: Mapped[float | None] = mapped_column(Float, default=None)
    weight: Mapped[float | None] = mapped_column(Float, default=None)
    height: Mapped[float | None] = mapped_column(Float, default=None)
    recorded_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    __table_args__ = (
        Index("ix_vitals_encounter_measured", "encounter_id", "measured_at"),
    )
