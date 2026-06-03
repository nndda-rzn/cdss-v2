"""Orchestrate HiResCAM generation for AIAnalysis rows and persist artifacts."""
from pathlib import Path

import numpy as np
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.hirescam_artifact import HiResCAMArtifact
from app.db.models.model_metadata import ModelMetadata
from app.services.hirescam.colormap import array_to_png
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import get_config
from app.services.hirescam.evaluator import evaluate_explanation
from app.services.hirescam.generator_v2 import generate_hirescam_v2
from app.services.hirescam.overlay import compose_overlay, compose_side_by_side
from app.services.hirescam.postprocess import postprocess_heatmap
from app.services.inference.loader import load_model


def generate_artifacts(
    session: Session,
    *,
    analysis: AIAnalysis,
    storage_root: Path,
    model_dir: Path,
    config: HiResCAMConfig | None = None,
) -> HiResCAMArtifact | None:
    """Generate HiResCAM artifacts for a single successful AIAnalysis row.

    If *config* is ``None``, the active config is read from the DB.
    Returns the persisted HiResCAMArtifact, or ``None`` on failure.
    """
    if analysis.status != "success" or analysis.predicted_class is None:
        return None

    # Check if artifact already exists (idempotency)
    existing = session.scalar(
        select(HiResCAMArtifact).where(HiResCAMArtifact.ai_analysis_id == analysis.id)
    )
    if existing is not None:
        return existing

    if config is None:
        config = get_config(session)

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
        model_path = Path(model_dir) / model.model_file_path
        yolo_model = load_model(str(model_path))

        class_idx = _class_to_index(analysis.predicted_class)

        heatmap_arr, lb_params, _ = generate_hirescam_v2(
            yolo_model, str(image_path), class_idx,
            target_layer_name=config.target_layer_name,
            input_size=config.input_size,
            device=config.device,
        )

        # Post-process with tuning params
        processed = postprocess_heatmap(
            heatmap_arr,
            lb_params,
            clip_percentile=config.clip_percentile,
            smooth_sigma=config.smooth_sigma,
            top_percent=config.top_percent,
            colormap=config.colormap,
        )

        # Apply signal mask to focus heatmap on ECG signals
        if config.use_signal_mask:
            from app.services.hirescam.signal_mask import create_signal_mask

            rgb_img = np.array(Image.open(str(image_path)).convert("RGB"))
            sig_mask = create_signal_mask(
                rgb_img,
                blur_radius=config.signal_mask_blur_radius,
            )
            norm_heatmap = processed["heatmap_norm"]
            masked = (
                (1.0 - config.signal_mask_strength) * norm_heatmap
                + config.signal_mask_strength * (norm_heatmap * sig_mask)
            )
            # Re-normalize
            m_min, m_max = masked.min(), masked.max()
            if m_max - m_min > 1e-8:
                masked = (masked - m_min) / (m_max - m_min)
            else:
                masked = np.zeros_like(masked)
            processed["heatmap_norm"] = masked

        heatmap_png = array_to_png(processed["heatmap_norm"], colormap=config.colormap)

        overlay_png = compose_overlay(
            str(image_path), heatmap_png, alpha=config.overlay_alpha,
        )
        side_by_side_png = compose_side_by_side(
            str(image_path), heatmap_png, overlay_png
        )

        status, focus_metric = evaluate_explanation(
            heatmap_arr,
            confidence=analysis.confidence_score,
            rgb_image=rgb_img if config.use_signal_mask else None,
        )

        heatmap_dir = storage_root / "heatmaps" / str(analysis.id)
        heatmap_dir.mkdir(parents=True, exist_ok=True)

        heatmap_path = heatmap_dir / "heatmap.png"
        overlay_path = heatmap_dir / "overlay.png"
        side_by_side_path = heatmap_dir / "side_by_side.png"

        heatmap_path.write_bytes(heatmap_png)
        overlay_path.write_bytes(overlay_png)
        side_by_side_path.write_bytes(side_by_side_png)

        artifact = HiResCAMArtifact(
            ai_analysis_id=analysis.id,
            heatmap_path=str(heatmap_path.relative_to(heatmap_dir.parent)),
            overlay_path=str(overlay_path.relative_to(heatmap_dir.parent)),
            side_by_side_path=str(side_by_side_path.relative_to(heatmap_dir.parent)),
            explanation_status=status,
            focus_metric=focus_metric,
            colormap_used=config.colormap,
        )
        session.add(artifact)
        return artifact

    except Exception:
        return None


def generate_for_study(
    session: Session,
    *,
    study_id: int,
    storage_root: Path,
    model_dir: Path,
    config: HiResCAMConfig | None = None,
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
            config=config,
        )
        if artifact is not None:
            artifacts.append(artifact)

    return artifacts


def _class_to_index(predicted_class: str) -> int:
    """Map predicted class name to YOLO class index."""
    class_order = ["abnormal", "homi", "mi", "normal"]
    return class_order.index(predicted_class)
