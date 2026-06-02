"""Tuning pipeline results API."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, send_file

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


@bp.get("/grid")
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


@bp.get("/grid/<int:config_index>")
def get_config(config_index: int):
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
