"""Shared helpers for the encounter-scoped API blueprints.

These were extracted from a single monolithic encounters blueprint so each
clinical domain (encounter, clinical context, vital signs, ECG study, AI
analysis) lives in its own focused module.
"""
from typing import cast

from flask import g, request
from sqlalchemy.orm import Session

from app.extensions import db


def session() -> Session:
    return cast(Session, db.session)


def request_ctx() -> dict[str, str]:
    return {
        "ip_address": request.remote_addr or "unknown",
        "user_agent": request.headers.get("User-Agent", "unknown"),
        "request_id": getattr(g, "request_id", request.headers.get("X-Request-ID", "n/a")),
    }


def current_user_id() -> int:
    from flask_jwt_extended import get_jwt_identity

    return int(get_jwt_identity())


def claims_facility_id() -> int:
    from flask_jwt_extended import get_jwt

    return int(get_jwt()["facility_id"])


def current_role() -> str | None:
    from flask_jwt_extended import get_jwt

    role = get_jwt().get("role")
    return str(role) if role is not None else None