from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins.timestamp import TimestampMixin


class _Sample(TimestampMixin, Base):
    __tablename__ = "sample_ts"
    id: Mapped[int] = mapped_column(primary_key=True)


def test_mixin_adds_columns():
    cols = {c.name for c in _Sample.__table__.columns}
    assert "created_at" in cols
    assert "updated_at" in cols
