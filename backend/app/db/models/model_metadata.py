"""ModelMetadata model (registry of trained YOLO classification models)."""
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import _utcnow

_TASK_TYPE = ("classification",)


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100))
    model_version: Mapped[str] = mapped_column(String(50))
    architecture: Mapped[str] = mapped_column(String(50))
    task_type: Mapped[str] = mapped_column(
        Enum(*_TASK_TYPE, name="model_task_type_enum", create_constraint=True)
    )
    input_size: Mapped[int] = mapped_column(default=224)
    model_file_path: Mapped[str] = mapped_column(String(500))
    model_checksum: Mapped[str] = mapped_column(String(64))
    model_size_mb: Mapped[float] = mapped_column(Float)
    class_names_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    threshold_config_json: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    training_date: Mapped[date | None] = mapped_column(Date, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "model_name", "model_version", name="uq_model_name_version"
        ),
        Index("ix_model_active", "is_active"),
    )
