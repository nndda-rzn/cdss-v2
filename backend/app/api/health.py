"""Health and version endpoints."""
from datetime import UTC, datetime

from flask import Blueprint, Response, current_app, jsonify
from sqlalchemy import text

from app.extensions import db

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.get("/health")
def health() -> tuple[Response, int]:
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:  # noqa: BLE001
        db_status = "error"
    return (
        jsonify(
            status="ok",
            db=db_status,
            time=datetime.now(UTC).isoformat(),
        ),
        200,
    )


@bp.get("/version")
def version() -> tuple[Response, int]:
    return (
        jsonify(
            version=current_app.config["APP_VERSION"],
            build=current_app.config.get("APP_VERSION"),
            git_sha=current_app.config["GIT_SHA"],
        ),
        200,
    )
