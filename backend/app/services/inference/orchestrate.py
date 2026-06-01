"""Run all active YOLO models on an ECG study and persist one row per model.

Synchronous, CPU-only. Idempotent: success rows are preserved across re-runs;
only missing or previously failed models are (re)executed. A single model
failure is isolated to its own row (status=failed) and never blocks others.
"""
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions.base import NotFoundError
from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.model_metadata import ModelMetadata
from app.services.audit.writer import write_audit
from app.services.inference.loader import load_model
from app.services.inference.predict import run_inference
from app.services.model_registry.query import list_active_models


def analyze_study(
    session: Session,
    *,
    study_id: int,
    user_id: int,
    model_dir: Path,
    storage_root: Path,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> list[AIAnalysis]:
    study = session.get(ECGStudy, study_id)
    if study is None:
        raise NotFoundError(
            code="ECG_STUDY_NOT_FOUND",
            message_id="Studi EKG tidak ditemukan",
            message_en="ECG study not found",
        )

    image_path = Path(storage_root) / study.image_original_path

    done = {
        row.model_metadata_id
        for row in session.scalars(
            select(AIAnalysis).where(
                AIAnalysis.ecg_study_id == study_id,
                AIAnalysis.status == "success",
            )
        ).all()
    }

    for model in list_active_models(session):
        if model.id in done:
            continue
        _run_one(
            session,
            study_id=study_id,
            model=model,
            model_dir=model_dir,
            image_path=image_path,
        )

    encounter = session.get(Encounter, study.encounter_id)
    write_audit(
        session,
        facility_id=encounter.facility_id if encounter is not None else None,
        action="ai_analysis",
        user_id=user_id,
        entity_type="ecg_study",
        entity_id=study_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    session.flush()

    # Auto-generate HiResCAM artifacts for successful analyses
    try:
        from app.services.hirescam.orchestrate import generate_for_study

        generate_for_study(
            session,
            study_id=study_id,
            storage_root=storage_root,
            model_dir=model_dir,
        )
        session.flush()
    except Exception as exc:  # noqa: BLE001 — HiResCAM failure must not block inference
        import logging
        logging.getLogger(__name__).warning("HiResCAM generation failed: %s", exc)

    return list(
        session.scalars(
            select(AIAnalysis)
            .where(AIAnalysis.ecg_study_id == study_id)
            .order_by(AIAnalysis.model_metadata_id)
        ).all()
    )


def _run_one(
    session: Session,
    *,
    study_id: int,
    model: ModelMetadata,
    model_dir: Path,
    image_path: Path,
) -> None:
    # Reuse a prior non-success row to avoid the (study, model) unique-constraint
    # violation on re-run; otherwise create a fresh row.
    row = session.scalar(
        select(AIAnalysis).where(
            AIAnalysis.ecg_study_id == study_id,
            AIAnalysis.model_metadata_id == model.id,
        )
    )
    is_new = row is None
    if row is None:
        row = AIAnalysis(
            ecg_study_id=study_id,
            model_metadata_id=model.id,
            status="failed",
        )

    try:
        resolved = str(Path(model_dir) / model.model_file_path)
        loaded = load_model(resolved)
        started = datetime.now(UTC)
        out = run_inference(loaded, str(image_path), device="cpu")
        finished = datetime.now(UTC)
        row.predicted_class = out["predicted_class"]
        row.confidence_score = out["confidence"]
        row.probability_json = out["probabilities"]
        row.inference_time_ms = int(out["inference_ms"])
        row.device_used = "cpu"
        row.status = "success"
        row.error_message = None
        row.inference_started_at = started
        row.inference_finished_at = finished
    except Exception as exc:  # noqa: BLE001 - isolate per-model failure
        row.status = "failed"
        row.error_message = str(exc)[:500]
        row.device_used = "cpu"

    if is_new:
        session.add(row)
