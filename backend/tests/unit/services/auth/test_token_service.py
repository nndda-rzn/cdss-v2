from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.exceptions.base import AuthError
from app.core.security.tokens import hash_token
from app.db.base import Base
from app.db.models.facility import HealthcareFacility
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.services.auth.token_service import issue_refresh_token, rotate_refresh_token


def _seed(engine):
    with Session(engine) as s:
        s.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
        s.add(User(id=1, name="A", email="a@x.id", password_hash="h",  # noqa: S106
                   role="admin", facility_id=1))
        s.commit()


def test_issue_then_rotate(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tok.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        raw1 = issue_refresh_token(s, user_id=1, ttl_days=7)
        s.commit()
        raw2 = rotate_refresh_token(s, raw_token=raw1, ttl_days=7)
        s.commit()
        assert raw2 != raw1
        old = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw1)))
        assert old.revoked_at is not None
        assert old.replaced_by_id is not None


def test_replay_detection_revokes_chain(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tok2.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        raw1 = issue_refresh_token(s, user_id=1, ttl_days=7)
        s.commit()
        rotate_refresh_token(s, raw_token=raw1, ttl_days=7)
        s.commit()
        with pytest.raises(AuthError) as exc:
            rotate_refresh_token(s, raw_token=raw1, ttl_days=7)
        assert exc.value.code == "AUTH_REFRESH_REPLAY"


def test_expired_token_rejected(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tok3.db'}")
    Base.metadata.create_all(engine)
    _seed(engine)
    with Session(engine) as s:
        raw = issue_refresh_token(s, user_id=1, ttl_days=7)
        t = s.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
        t.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        s.commit()
        with pytest.raises(AuthError) as exc:
            rotate_refresh_token(s, raw_token=raw, ttl_days=7)
        assert exc.value.code == "AUTH_REFRESH_INVALID"
