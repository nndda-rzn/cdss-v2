"""AIAnalysis model (N:1 with ECGStudy and ModelMetadata; one row per model)."""
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

_PREDICTED_CLASS = ("normal", "mi", "homi", "abnormal")
_DEVICE = ("cpu", "gpu")
_STATUS = ("success", "failed", "skipped")


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    ecg_study_id: Mapped[int] = mapped_column(
        ForeignKey("ecg_study.id"), index=True
    )
    model_metadata_id: Mapped[int] = mapped_column(
        ForeignKey("model_metadata.id"), index=True
    )
    predicted_class: Mapped[str | None] = mapped_column(
        Enum(
            *_PREDICTED_CLASS,
            name="analysis_predicted_class_enum",
            create_constraint=True,
        ),
        default=None,
    )
    confidence_score: Mapped[float | None] = mapped_column(Float, default=None)
    probability_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    inference_time_ms: Mapped[int | None] = mapped_column(
        Integer, default=None
    )
    device_used: Mapped[str] = mapped_column(
        Enum(*_DEVICE, name="analysis_device_enum", create_constraint=True),
        default="cpu",
    )
    inference_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    inference_finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    status: Mapped[str] = mapped_column(
        Enum(*_STATUS, name="analysis_status_enum", create_constraint=True)
    )
    error_message: Mapped[str | None] = mapped_column(
        String(500), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "ecg_study_id",
            "model_metadata_id",
            name="uq_analysis_study_model",
        ),
        Index("ix_analysis_status", "status"),
    )
