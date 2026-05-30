from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User


def test_create_refresh_token(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'rt.db'}")
    Base.metadata.create_all(engine)
    now = datetime.now(UTC)
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(
            User(id=1, name="A", email="a@x.id", password_hash="h", role="admin", facility_id=1)  # noqa: S106
        )
        s.add(RefreshToken(user_id=1, token_hash="abc", expires_at=now + timedelta(days=7)))  # noqa: S106
        s.commit()
    with Session(engine) as s:
        t = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == "abc"))  # noqa: S105
        assert t.revoked_at is None
        assert t.replaced_by_id is None
