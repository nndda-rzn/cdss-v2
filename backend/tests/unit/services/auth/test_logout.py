from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.security.tokens import hash_token
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.services.auth.token_service import issue_refresh_token, revoke_refresh_token


def _seed(engine):
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(
            User(
                id=1,
                name="A",
                email="a@x.id",
                password_hash="h",  # noqa: S106
                role="admin",
                facility_id=1,
            )
        )
        s.commit()


def test_logout_is_idempotent(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'lo.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        raw = issue_refresh_token(s, user_id=1, ttl_days=7)
        s.commit()
        revoke_refresh_token(s, raw_token=raw)
        s.commit()
        t = s.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw))
        )
        assert t.revoked_at is not None
        revoke_refresh_token(s, raw_token=raw)
        s.commit()
        revoke_refresh_token(s, raw_token="never-existed")  # noqa: S106
        s.commit()
