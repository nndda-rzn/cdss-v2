"""Auth endpoints: login, refresh, logout, me."""
from typing import cast

from flask import Blueprint, Response, current_app, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import AuthError
from app.core.security.jwt import make_access_token
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
    new_refresh = rotate_refresh_token(
        session, raw_token=data.refresh_token, ttl_days=current_app.config["REFRESH_TTL_DAYS"]
    )
    token_row = session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(new_refresh))
    )
    assert token_row is not None
    user = session.get(User, token_row.user_id)
    assert user is not None
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
    assert user is not None
    return jsonify(
        user=UserOut(
            id=user.id, name=user.name, role=user.role, facility_id=user.facility_id
        ).model_dump()
    )
