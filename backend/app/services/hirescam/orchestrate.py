"""Orchestrate HiResCAM generation for AIAnalysis rows and persist artifacts."""
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.hirescam_artifact import HiResCAMArtifact
from app.db.models.model_metadata import ModelMetadata
from app.services.hirescam.colormap import array_to_png
from app.services.hirescam.evaluator import evaluate_explanation
from app.services.hirescam.generator_v2 import generate_hirescam_v2
from app.services.hirescam.overlay import compose_overlay, compose_side_by_side
from app.services.inference.loader import load_model


def generate_artifacts(
    session: Session,
    *,
    analysis: AIAnalysis,
    storage_root: Path,
    model_dir: Path,
) -> HiResCAMArtifact | None:
    """Generate HiResCAM artifacts for a single successful AIAnalysis row.

    Returns the persisted HiResCAMArtifact, or None if generation fails.
    """
    if analysis.status != "success" or analysis.predicted_class is None:
        return None

    # Check if artifact already exists (idempotency)
    existing = session.scalar(
        select(HiResCAMArtifact).where(HiResCAMArtifact.ai_analysis_id == analysis.id)
    )
    if existing is not None:
        return existing

    study = session.get(ECGStudy, analysis.ecg_study_id)
    if study is None:
        return None

    model = session.get(ModelMetadata, analysis.model_metadata_id)
    if model is None:
        return None

    image_path = Path(storage_root) / study.image_original_path
    if not image_path.exists():
        return None

    try:
        # Load model and generate HiResCAM
        model_path = Path(model_dir) / model.model_file_path
        yolo_model = load_model(str(model_path))

        # Map predicted_class to class index
        class_idx = _class_to_index(analysis.predicted_class)

        heatmap_arr, lb_params, _ = generate_hirescam_v2(
            yolo_model, str(image_path), class_idx,
            target_layer_name="last_conv",
            input_size=1600,
            device="cpu",
        )

        # Render heatmap PNG
        heatmap_png = array_to_png(heatmap_arr)

        # Compose overlay and side-by-side
        overlay_png = compose_overlay(str(image_path), heatmap_png)
        side_by_side_png = compose_side_by_side(
            str(image_path), heatmap_png, overlay_png
        )

        # Evaluate explanation quality
        status, focus_metric = evaluate_explanation(
            heatmap_arr, confidence=analysis.confidence_score
        )

        # Save artifacts to storage
        # Store paths relative to STORAGE_DIR/heatmaps (not STORAGE_DIR)
        # So paths are "21/heatmap.png" not "heatmaps/21/heatmap.png"
        heatmap_dir = storage_root / "heatmaps" / str(analysis.id)
        heatmap_dir.mkdir(parents=True, exist_ok=True)

        heatmap_path = heatmap_dir / "heatmap.png"
        overlay_path = heatmap_dir / "overlay.png"
        side_by_side_path = heatmap_dir / "side_by_side.png"

        heatmap_path.write_bytes(heatmap_png)
        overlay_path.write_bytes(overlay_png)
        side_by_side_path.write_bytes(side_by_side_png)

        # Persist artifact
        artifact = HiResCAMArtifact(
            ai_analysis_id=analysis.id,
            heatmap_path=str(heatmap_path.relative_to(heatmap_dir.parent)),
            overlay_path=str(overlay_path.relative_to(heatmap_dir.parent)),
            side_by_side_path=str(side_by_side_path.relative_to(heatmap_dir.parent)),
            explanation_status=status,
            focus_metric=focus_metric,
            colormap_used="inferno",
        )
        session.add(artifact)
        return artifact

    except Exception:
        # Isolate failure — don't block other artifacts
        return None


def generate_for_study(
    session: Session,
    *,
    study_id: int,
    storage_root: Path,
    model_dir: Path,
) -> list[HiResCAMArtifact]:
    """Generate HiResCAM artifacts for all successful AIAnalysis rows of a study."""
    analyses = list(
        session.scalars(
            select(AIAnalysis).where(
                AIAnalysis.ecg_study_id == study_id,
                AIAnalysis.status == "success",
            )
        ).all()
    )

    artifacts: list[HiResCAMArtifact] = []
    for analysis in analyses:
        artifact = generate_artifacts(
            session,
            analysis=analysis,
            storage_root=storage_root,
            model_dir=model_dir,
        )
        if artifact is not None:
            artifacts.append(artifact)

    return artifacts


def _class_to_index(predicted_class: str) -> int:
    """Map predicted class name to YOLO class index."""
    class_order = ["abnormal", "homi", "mi", "normal"]
    return class_order.index(predicted_class)


def _artifact_dir(storage_root: Path, analysis_id: int) -> Path:
    """Returns directory path for analysis artifacts."""
    return storage_root / "heatmaps" / str(analysis_id)
