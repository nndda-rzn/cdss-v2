"""HiResCAM API: generate artifacts, get status, serve images."""
from pathlib import Path

from flask import Blueprint, Response, current_app, jsonify, send_file
from sqlalchemy import select

from app.api._shared import session
from app.api.ecg_studies import get_study_or_404
from app.core.exceptions.base import NotFoundError
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.hirescam_artifact import HiResCAMArtifact
from app.schemas.hirescam import HiResCAMArtifactOut
from app.services.hirescam.orchestrate import generate_artifacts

bp = Blueprint("hirescam", __name__, url_prefix="/api/encounters")


def artifact_to_out(a: HiResCAMArtifact) -> dict[str, object]:
    return HiResCAMArtifactOut(
        id=a.id,
        ai_analysis_id=a.ai_analysis_id,
        heatmap_path=a.heatmap_path,
        overlay_path=a.overlay_path,
        side_by_side_path=a.side_by_side_path,
        explanation_status=a.explanation_status,
        focus_metric=a.focus_metric,
        colormap_used=a.colormap_used,
        generated_at=a.generated_at.isoformat(),
    ).model_dump()


@bp.post(
    "/<int:encounter_id>/ecg-studies/<int:study_id>/analyses/"
    "<int:analysis_id>/hirescam"
)
@require_role(Role.CLINICIAN, Role.NURSE)
def generate_hirescam(
    encounter_id: int, study_id: int, analysis_id: int
) -> tuple[Response, int]:
    """Generate HiResCAM artifacts for a specific analysis."""
    s = session()
    get_study_or_404(s, encounter_id=encounter_id, study_id=study_id)
    analysis = s.get(AIAnalysis, analysis_id)
    if analysis is None or analysis.ecg_study_id != study_id:
        raise NotFoundError(
            code="ANALYSIS_NOT_FOUND",
            message_id="Analisis tidak ditemukan",
            message_en="Analysis not found",
        )

    storage_root = Path(current_app.config["STORAGE_DIR"])
    model_dir = Path(current_app.config["MODEL_DIR"])

    artifact = generate_artifacts(
        s,
        analysis=analysis,
        storage_root=storage_root,
        model_dir=model_dir,
    )
    s.commit()

    if artifact is None:
        return (
            jsonify(error={"message_id": "Gagal generate HiResCAM"}),
            500,
        )

    return jsonify(artifact=artifact_to_out(artifact)), 201


@bp.get(
    "/<int:encounter_id>/ecg-studies/<int:study_id>/analyses/"
    "<int:analysis_id>/hirescam"
)
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_hirescam(
    encounter_id: int, study_id: int, analysis_id: int
) -> Response:
    """Get HiResCAM artifact for a specific analysis."""
    s = session()
    artifact = s.scalar(
        select(HiResCAMArtifact).where(
            HiResCAMArtifact.ai_analysis_id == analysis_id
        )
    )
    if artifact is None:
        raise NotFoundError(
            code="HIRESCAM_NOT_FOUND",
            message_id="HiResCAM belum di-generate",
            message_en="HiResCAM not yet generated",
        )

    return jsonify(artifact=artifact_to_out(artifact))


@bp.get(
    "/<int:encounter_id>/ecg-studies/<int:study_id>/hirescam"
)
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_study_hirescam(encounter_id: int, study_id: int) -> Response:
    """Get all HiResCAM artifacts for a study."""
    s = session()
    artifacts = list(
        s.scalars(
            select(HiResCAMArtifact)
            .join(AIAnalysis)
            .where(AIAnalysis.ecg_study_id == study_id)
        ).all()
    )
    items = [artifact_to_out(a) for a in artifacts]
    return jsonify(items=items)


@bp.get("/heatmaps/<path:filepath>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def serve_heatmap(filepath: str) -> Response:
    """Serve a heatmap/overlay/side-by-side PNG file."""
    storage_root = Path(current_app.config["STORAGE_DIR"])
    full_path = (storage_root / filepath).resolve()

    # Security: prevent path traversal
    if not full_path.is_relative_to(storage_root.resolve()):
        raise NotFoundError(
            code="FILE_NOT_FOUND",
            message_id="File tidak ditemukan",
            message_en="File not found",
        )

    if not full_path.exists():
        raise NotFoundError(
            code="FILE_NOT_FOUND",
            message_id="File tidak ditemukan",
            message_en="File not found",
        )

    return send_file(str(full_path), mimetype="image/png")
