"""HealthcareFacility model."""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin


class HealthcareFacility(TimestampMixin, Base):
    __tablename__ = "healthcare_facility"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    facility_type: Mapped[str] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(300), default=None)
    province_code: Mapped[str | None] = mapped_column(String(10), default=None)
    regency_code: Mapped[str | None] = mapped_column(String(10), default=None)
    subdistrict_code: Mapped[str | None] = mapped_column(String(10), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
