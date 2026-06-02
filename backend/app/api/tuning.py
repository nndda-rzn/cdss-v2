"""Tuning pipeline results API."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, send_file

from app.api._shared import current_user_id, session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import get_config, save_config

bp = Blueprint("tuning", __name__, url_prefix="/api/tuning")

ALLOWED_IMAGES = {
    "original.png", "heatmap_colored.png", "heatmap_norm.png",
    "overlay.png", "mask_top_area.png",
}


def _repo_root() -> Path:
    """Get project root from STORAGE_DIR config."""
    return Path(current_app.config.get("STORAGE_DIR", "")).parent


def _grid_dir() -> Path:
    return _repo_root() / "outputs" / "hirescam_tuning_grid"


def _read_summary_row(config_index: int) -> dict[str, str] | None:
    """Find a specific config_index row in summary.csv."""
    summary_path = _grid_dir() / "summary.csv"
    if not summary_path.exists():
        return None
    with open(summary_path, newline="") as f:
        for row in csv.DictReader(f):
            if int(row["config_index"]) == config_index:
                return row
    return None


@bp.get("/grid")
@require_role(Role.ADMIN)
def get_grid():
    """Return summary.csv as JSON array."""
    summary_path = _grid_dir() / "summary.csv"

    if not summary_path.exists():
        return jsonify({"items": []})

    with open(summary_path, newline="") as f:
        reader = csv.DictReader(f)
        items = []
        for row in reader:
            items.append({
                "config_index": int(row["config_index"]),
                "input_size": int(row["input_size"]),
                "target_layer": row["target_layer"],
                "smooth_sigma": float(row["smooth_sigma"]),
                "top_percent": float(row["top_percent"]),
                "clip_percentile": float(row["clip_percentile"]),
                "colormap": row["colormap"],
                "explanation_status": row["explanation_status"],
                "focus_metric": float(row["focus_metric"]),
                "confidence": float(row["confidence"]),
            })

    return jsonify({"items": items})


@bp.get("/active")
@require_role(Role.ADMIN)
def get_active_config():
    """Return the currently active HiResCAM config from DB."""
    s = session()
    config = get_config(s)
    return jsonify(config.to_dict())


@bp.post("/apply/<int:config_index>")
@require_role(Role.ADMIN)
def apply_config(config_index: int):
    """Apply a tuning config as the active HiResCAM production config."""
    row = _read_summary_row(config_index)
    if row is None:
        abort(404, description=f"Config {config_index} not found in summary.csv")

    config = HiResCAMConfig(
        target_layer_name=row["target_layer"],
        input_size=int(row["input_size"]),
        clip_percentile=float(row["clip_percentile"]),
        smooth_sigma=float(row["smooth_sigma"]),
        top_percent=float(row["top_percent"]),
        colormap=row["colormap"],
    )

    s = session()
    uid = current_user_id()
    save_config(s, config, user_id=uid)
    s.commit()

    return jsonify(status="applied", config=config.to_dict())


@bp.get("/grid/<int:config_index>")
@require_role(Role.ADMIN)
def get_config_detail(config_index: int):
    """Return metadata.json for a specific config."""
    config_dir = _grid_dir() / f"config_{config_index:03d}"
    metadata_path = config_dir / "metadata.json"

    if not metadata_path.exists():
        abort(404, description=f"Config {config_index} not found")

    with open(metadata_path) as f:
        metadata = json.load(f)

    return jsonify(metadata)


@bp.get("/grid/<int:config_index>/images/<filename>")
def get_config_image(config_index: int, filename: str):
    """Serve a PNG image from a config directory."""
    if filename not in ALLOWED_IMAGES:
        abort(404, description=f"Unknown image: {filename}")

    image_path = _grid_dir() / f"config_{config_index:03d}" / filename

    if not image_path.exists() or not image_path.is_file():
        abort(404, description=f"Image not found: {filename}")

    # Path traversal guard
    if not image_path.resolve().is_relative_to(_grid_dir().resolve()):
        abort(400, description="Invalid path")

    return send_file(str(image_path), mimetype="image/png")
