"""Serve uploaded clinical images (ECG) with RBAC and path-traversal guards.

ECG images are T4 clinical data (anonymous by themselves), not T1 direct
identifiers, so per-request PHI access logging is intentionally omitted here
(it would be noisy on every thumbnail render). The RBAC gate is the access
boundary; the patient-detail reveal path already records PHIAccessLog for the
identifying fields.
"""
from pathlib import Path

from flask import Blueprint, Response, current_app, send_from_directory
from werkzeug.exceptions import NotFound

from app.core.exceptions.base import NotFoundError, ValidationError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role

bp = Blueprint("uploads", __name__)

_ALLOWED_PREFIX = "ecg/"


@bp.get("/uploads/<path:subpath>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def serve_upload(subpath: str) -> Response:
    # Defense-in-depth: send_from_directory already rejects traversal, but we
    # fail fast on anything outside the ecg/ whitelist or containing "..".
    if ".." in subpath or subpath.startswith("/") or "\\" in subpath:
        raise ValidationError(
            code="INVALID_PATH",
            message_id="Path berkas tidak valid",
            message_en="Invalid file path",
        )
    if not subpath.startswith(_ALLOWED_PREFIX):
        raise ValidationError(
            code="INVALID_PATH",
            message_id="Path berkas tidak valid",
            message_en="Invalid file path",
        )

    base_dir = Path(current_app.config["STORAGE_DIR"]) / "uploads"
    try:
        return send_from_directory(base_dir, subpath)
    except NotFound:
        raise NotFoundError(
            code="FILE_NOT_FOUND",
            message_id="Berkas tidak ditemukan",
            message_en="File not found",
        ) from None