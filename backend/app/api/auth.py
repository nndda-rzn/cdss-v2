"""Auth endpoints: login, refresh, logout, me."""
from typing import cast

from flask import Blueprint, Response, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import AuthError, NotFoundError, RateLimitError
from app.core.security.jwt import make_access_token
from app.core.security.rate_limit import LoginRateLimiter
from app.core.security.tokens import hash_token
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.extensions import db
from app.schemas.auth import LoginRequest, RefreshRequest, UserOut
from app.services.auth.login_service import authenticate
from app.services.auth.token_service import (
    issue_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

_rate_limiter: LoginRateLimiter | None = None


def _get_rate_limiter() -> LoginRateLimiter:
    global _rate_limiter  # noqa: PLW0603
    if _rate_limiter is None:
        _rate_limiter = LoginRateLimiter(
            max_attempts=current_app.config["LOGIN_RATE_LIMIT_MAX"],
            window_seconds=current_app.config["LOGIN_RATE_LIMIT_WINDOW"],
        )
    return _rate_limiter


def _session() -> Session:
    # flask-sqlalchemy exposes a scoped_session proxy; the service layer accepts
    # a plain sqlalchemy Session. The proxy delegates to one at runtime.
    return cast(Session, db.session)


def _ctx() -> dict[str, str]:
    return {
        "ip_address": request.remote_addr or "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "request_id": getattr(g, "request_id", request.headers.get("X-Request-ID", "n/a")),
    }


@bp.post("/login")
def login() -> Response:
    limiter = _get_rate_limiter()
    ip = request.remote_addr or "unknown"

    if not limiter.is_allowed(ip):
        raise RateLimitError(
            code="AUTH_RATE_LIMITED",
            message_id="Terlalu banyak percobaan. Coba lagi nanti.",
            message_en="Too many attempts. Please try again later.",
        )

    data = LoginRequest(**(request.get_json() or {}))
    session = _session()
    try:
        user = authenticate(session, email=data.email, password=data.password, **_ctx())
    except AuthError:
        # authenticate() writes a login_failed audit row before raising; commit
        # it so failed attempts are persisted in the real request lifecycle.
        session.commit()
        raise
    access = make_access_token(user_id=user.id, role=user.role, facility_id=user.facility_id)
    refresh = issue_refresh_token(
        session, user_id=user.id, ttl_days=current_app.config["REFRESH_TTL_DAYS"]
    )
    session.commit()
    return jsonify(
        access_token=access,
        refresh_token=refresh,
        user=UserOut(
            id=user.id, name=user.name, role=user.role, facility_id=user.facility_id
        ).model_dump(),
    )


@bp.post("/refresh")
def refresh() -> Response:
    data = RefreshRequest(**(request.get_json() or {}))
    session = _session()
    try:
        new_refresh = rotate_refresh_token(
            session, raw_token=data.refresh_token, ttl_days=current_app.config["REFRESH_TTL_DAYS"]
        )
    except AuthError:
        # Replay detection writes a chain-wide revocation before raising; commit
        # it so the revocation persists in the real request lifecycle (C1).
        session.commit()
        raise
    token_row = session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(new_refresh))
    )
    if token_row is None:
        raise NotFoundError(
            code="AUTH_REFRESH_INVALID",
            message_id="Token tidak valid",
            message_en="Invalid refresh token",
        )
    user = session.get(User, token_row.user_id)
    # Re-check the user is still active: a deactivated user must not keep minting
    # access tokens by rotating refresh tokens (I2).
    if user is None or not user.is_active:
        revoke_refresh_token(session, raw_token=new_refresh)
        session.commit()
        raise AuthError(
            code="AUTH_REFRESH_INVALID",
            message_id="Akun tidak aktif",
            message_en="Account is inactive",
        )
    access = make_access_token(user_id=user.id, role=user.role, facility_id=user.facility_id)
    session.commit()
    return jsonify(access_token=access, refresh_token=new_refresh)


@bp.post("/logout")
@jwt_required()
def logout() -> Response:
    data = request.get_json() or {}
    raw = data.get("refresh_token")
    if raw:
        session = _session()
        revoke_refresh_token(session, raw_token=raw)
        session.commit()
    return jsonify(status="ok")


@bp.get("/me")
@jwt_required()
def me() -> Response:
    user = _session().get(User, int(get_jwt_identity()))
    if user is None:
        raise NotFoundError(
            code="USER_NOT_FOUND",
            message_id="Pengguna tidak ditemukan",
            message_en="User not found",
        )
    return jsonify(
        user=UserOut(
            id=user.id, name=user.name, role=user.role, facility_id=user.facility_id
        ).model_dump()
    )
