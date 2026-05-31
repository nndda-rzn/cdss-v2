"""ECGStudy model (M:1 with Encounter; EKG image metadata + quality)."""
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

_QUALITY = ("good", "acceptable", "poor")


class ECGStudy(Base):
    __tablename__ = "ecg_study"

    id: Mapped[int] = mapped_column(primary_key=True)
    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounter.id"), index=True
    )
    patient_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("patient.id"), index=True
    )
    study_uid: Mapped[str] = mapped_column(String(64), unique=True)
    image_original_path: Mapped[str] = mapped_column(String(500))
    image_processed_path: Mapped[str | None] = mapped_column(
        String(500), default=None
    )
    image_quality_status: Mapped[str] = mapped_column(
        Enum(*_QUALITY, name="ecg_quality_status_enum", create_constraint=True)
    )
    image_quality_score: Mapped[float] = mapped_column(Float)
    image_quality_metrics_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    recorded_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    device_info: Mapped[str | None] = mapped_column(String(200), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    __table_args__ = (
        Index("ix_ecg_encounter_created", "encounter_id", "created_at"),
    )
