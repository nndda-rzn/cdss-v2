"""List available models endpoint."""
from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from app.db.models.model_metadata import ModelMetadata
from app.extensions import db

bp = Blueprint("models", __name__, url_prefix="/api")


@bp.get("/models")
@jwt_required()
def list_models() -> tuple[Response, int]:
    rows = db.session.execute(
        select(ModelMetadata).order_by(ModelMetadata.model_name)
    ).scalars().all()

    result = [
        {
            "id": r.id,
            "model_name": r.model_name,
            "model_version": r.model_version,
            "architecture": r.architecture,
            "task_type": r.task_type,
            "input_size": r.input_size,
            "model_file_path": r.model_file_path,
            "model_checksum": r.model_checksum,
            "model_size_mb": r.model_size_mb,
            "class_names_json": r.class_names_json,
            "threshold_config_json": r.threshold_config_json,
            "is_active": r.is_active,
            "training_date": r.training_date.isoformat() if r.training_date else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return jsonify(items=result), 200
