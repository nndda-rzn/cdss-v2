"""Refresh token issue + rotation with replay detection."""
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.exceptions.base import AuthError
from app.core.security.tokens import generate_refresh_token, hash_token
from app.db.models.refresh_token import RefreshToken


def _now() -> datetime:
    return datetime.now(UTC)


def _as_aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def issue_refresh_token(session: Session, *, user_id: int, ttl_days: int) -> str:
    raw, token_hash = generate_refresh_token()
    session.add(RefreshToken(
        user_id=user_id, token_hash=token_hash,
        expires_at=_now() + timedelta(days=ttl_days),
    ))
    return raw


def rotate_refresh_token(session: Session, *, raw_token: str, ttl_days: int) -> str:
    token_hash = hash_token(raw_token)
    current = session.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if current is None:
        raise AuthError(code="AUTH_REFRESH_INVALID",
                        message_id="Token tidak valid", message_en="Invalid refresh token")
    if current.revoked_at is not None:
        session.execute(
            update(RefreshToken).where(
                RefreshToken.user_id == current.user_id,
                RefreshToken.revoked_at.is_(None),
            ).values(revoked_at=_now())
        )
        raise AuthError(code="AUTH_REFRESH_REPLAY",
                        message_id="Token sudah digunakan",
                        message_en="Refresh token reuse detected")
    if _as_aware(current.expires_at) <= _now():
        raise AuthError(code="AUTH_REFRESH_INVALID",
                        message_id="Token kedaluwarsa", message_en="Refresh token expired")
    new_raw, new_hash = generate_refresh_token()
    new_token = RefreshToken(user_id=current.user_id, token_hash=new_hash,
                             expires_at=_now() + timedelta(days=ttl_days))
    session.add(new_token)
    session.flush()
    current.revoked_at = _now()
    current.replaced_by_id = new_token.id
    return new_raw
