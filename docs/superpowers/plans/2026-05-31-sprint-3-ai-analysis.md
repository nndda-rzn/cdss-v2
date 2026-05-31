# Sprint 3: AIAnalysis Layer (5 YOLO Models) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run 5 trained YOLO classification models on uploaded ECG images, persisting predicted class + confidence + per-class probabilities per model, exposed via API and a comparison-table UI. Synchronous, CPU-only. No HiResCAM (Sprint 4).

**Architecture:** Vertical slice following Sprint 2A/2B patterns. S14/S16 add ModelMetadata + AIAnalysis ORM models + migrations. S15 seeds the 5 models with SHA256. S17 builds inference services (loader cache, predict, run-all-active orchestrator) with a mockable loader so CI needs no model files. S18 wires nested API endpoints. S19 adds the AnalysisPanel. S20 amends ADR-0004.

**Tech Stack:** Flask, SQLAlchemy 2.0 (typed), Alembic, Pydantic v2, ultralytics + torch (CPU), React 18, TypeScript, TanStack Query 5, shadcn/ui.

---

## Environment Facts (verified during planning)

- 5 models at `D:\Kuliah\Skripsi\Model\Final Model\{yolov8n_cls,yolov8s_cls,yolo11n_cls,yolo11s_cls,yolo26n_cls}\best.pt`
- All task=classify, identical 4 classes in this index order:
  - 0 `abnormal_heartbeat` -> enum `abnormal`
  - 1 `history_myocardial_infarction` -> enum `homi`
  - 2 `myocardial_infarction` -> enum `mi`
  - 3 `normal` -> enum `normal`
- Per-model inference ~93ms CPU (synthetic 224x224); 5 models ~0.5s
- ultralytics 8.4.58 + torch 2.12.0+cpu already installed in backend/.venv (opencv-python-headless retained; ultralytics installed without opencv-python)
- Current Alembic head: `c5d8f21b44c0` (ecg_study)

## File Structure Map

```
backend/app/
  db/models/model_metadata.py            (NEW)
  db/models/ai_analysis.py               (NEW)
  db/models/__init__.py                  (MODIFY register both)
  services/inference/__init__.py         (NEW)
  services/inference/mapping.py          (NEW - YOLO idx<->enum)
  services/inference/loader.py           (NEW - model cache)
  services/inference/predict.py          (NEW - run_inference)
  services/inference/orchestrate.py      (NEW - analyze_study)
  services/model_registry/query.py       (NEW - list_active_models)
  schemas/ai_analysis.py                 (NEW)
  api/encounters.py                      (MODIFY - 2 endpoints)
  config.py                              (MODIFY - MODEL_DIR)
  paths.py                               (MODIFY - MODEL_DIR default)
  pyproject.toml                         (MODIFY - ultralytics dep)

backend/tests/
  unit/db/models/test_model_metadata.py  (NEW)
  unit/db/models/test_ai_analysis.py     (NEW)
  unit/services/inference/test_predict.py     (NEW)
  unit/services/inference/test_orchestrate.py (NEW)
  integration/test_ai_analysis_api.py    (NEW)

backend/migrations/versions/
  <hash>_add_model_metadata_table.py     (NEW)
  <hash>_add_ai_analysis_table.py        (NEW)

scripts/seed_models.py                   (NEW)

frontend/src/features/ai_analysis/
  api.ts                                 (NEW)
  AnalysisPanel.tsx                      (NEW)
  AnalysisPanel.test.tsx                 (NEW)
frontend/src/features/encounter/Detail.tsx OR ecg_study (MODIFY - mount panel)

docs/adr/0004-three-yolo-models-comparison.md (MODIFY - amend to 5)
models/.gitkeep                          (NEW - MODEL_DIR default, weights gitignored)
.gitignore                               (MODIFY - ignore models/*.pt)
```

---
## Phase S14 — ModelMetadata Model + Migration

### Task S14-1: ModelMetadata ORM + migration

**Files:** create `backend/app/db/models/model_metadata.py`, `backend/tests/unit/db/models/test_model_metadata.py`; modify `backend/app/db/models/__init__.py`; generate migration.

- [ ] Step 1: Write failing test `test_model_metadata.py`:
  - test_persists: ModelMetadata(model_name="yolov8n-cls", model_version="v1.0", architecture="YOLOv8n", task_type="classification", input_size=224, model_file_path="yolov8n_cls/best.pt", model_checksum="abc", model_size_mb=2.83, class_names_json=["abnormal","homi","mi","normal"], is_active=True) persists; query back.
  - test_unique_name_version: two rows same (model_name, model_version) -> IntegrityError.

- [ ] Step 2: Run, expect FAIL (module not found). Workdir backend.

- [ ] Step 3: Create model. Columns per spec 3.1. Use Enum for task_type ("classification",), JSON for class_names_json/threshold_config_json, Boolean is_active default False, DateTime created_at default `_utcnow`. `__table_args__`: UniqueConstraint("model_name","model_version", name="uq_model_name_version"), Index("ix_model_active","is_active"). Follow vital_signs.py / ecg_study.py style. Use Mapped[dict[str, object]] for JSON columns, Mapped[list[str]] won't map cleanly — use `Mapped[list]` with `mapped_column(JSON)` or `Mapped[dict[str, object]]`. For class_names_json use `Mapped[list]` typed as `mapped_column(JSON, default=list)`; if mypy complains use `Mapped[list[str]]`.

- [ ] Step 4: Register in __init__.py (import after EcgStudy, add "ModelMetadata" to __all__).

- [ ] Step 5: Run test, expect 2 passed.

- [ ] Step 6: Generate migration: `alembic upgrade head && alembic revision --autogenerate -m "add model_metadata table"`. Clean to repo style (imports `import sqlalchemy as sa` then `from alembic import op`, remove autogen comments, verify down_revision = "c5d8f21b44c0"). `ruff check migrations/versions/<hash>... --fix`.

- [ ] Step 7: Roundtrip `alembic downgrade -1 && alembic upgrade head`; `ruff check . && mypy .`.

- [ ] Step 8: Commit `feat(db): add ModelMetadata model and migration`.

---

## Phase S15 — Seed Models Script

### Task S15-1: seed_models.py

**Files:** create `scripts/seed_models.py`; create `models/.gitkeep`; modify `.gitignore`, `backend/app/paths.py`, `backend/app/config.py`.

- [ ] Step 1: Add MODEL_DIR to paths.py: `MODEL_DIR = REPO_ROOT / "models"` after STORAGE_DIR.

- [ ] Step 2: Wire config.py: import MODEL_DIR; BaseConfig `self.MODEL_DIR = os.environ.get("MODEL_DIR", str(MODEL_DIR))`; TestConfig `self.MODEL_DIR = os.environ.get("TEST_MODEL_DIR", str(MODEL_DIR))`.

- [ ] Step 3: .gitignore add block: `# ===== Model weights (large, not in git) =====` then `models/**` then `!models/.gitkeep`. Create `models/.gitkeep`.

- [ ] Step 4: Write seed_models.py. For each of 5 model dirs under MODEL_DIR, compute SHA256 of best.pt, read class names via ultralytics YOLO(path).names mapped to enum order, upsert ModelMetadata (idempotent on model_name+version). Architecture + model_name derived from folder name. Use env MODEL_DIR or default. Mapping constant: {"abnormal_heartbeat":"abnormal","history_myocardial_infarction":"homi","myocardial_infarction":"mi","normal":"normal"}. Store class_names_json as the enum-mapped ordered list. Mark is_active=True for all 5. Print summary to stderr. Idempotent (skip if exists).

```python
"""Seed the 5 trained YOLO classification models into ModelMetadata."""
import hashlib
import os
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.model_metadata import ModelMetadata

_FOLDERS = {
    "yolov8n_cls": ("yolov8n-cls", "YOLOv8n"),
    "yolov8s_cls": ("yolov8s-cls", "YOLOv8s"),
    "yolo11n_cls": ("yolov11n-cls", "YOLOv11n"),
    "yolo11s_cls": ("yolov11s-cls", "YOLOv11s"),
    "yolo26n_cls": ("yolov26n-cls", "YOLOv26n"),
}
_ENUM_MAP = {
    "abnormal_heartbeat": "abnormal",
    "history_myocardial_infarction": "homi",
    "myocardial_infarction": "mi",
    "normal": "normal",
}


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def seed_models(session: Session, model_dir: Path, version: str = "v1.0") -> int:
    from ultralytics import YOLO

    count = 0
    for folder, (name, arch) in _FOLDERS.items():
        weights = model_dir / folder / "best.pt"
        if not weights.exists():
            print(f"skip {folder}: {weights} missing", file=sys.stderr)
            continue
        exists = session.scalar(
            select(ModelMetadata).where(
                ModelMetadata.model_name == name,
                ModelMetadata.model_version == version,
            )
        )
        if exists is not None:
            continue
        names = YOLO(str(weights)).names
        ordered = [_ENUM_MAP[names[i]] for i in sorted(names)]
        session.add(
            ModelMetadata(
                model_name=name,
                model_version=version,
                architecture=arch,
                task_type="classification",
                input_size=224,
                model_file_path=f"{folder}/best.pt",
                model_checksum=_sha256(weights),
                model_size_mb=round(weights.stat().st_size / (1024 * 1024), 2),
                class_names_json=ordered,
                threshold_config_json={},
                is_active=True,
            )
        )
        count += 1
    return count


if __name__ == "__main__":
    from app.db.engine import create_db_engine
    from app.paths import default_database_url

    model_dir = Path(os.environ.get("MODEL_DIR", "models"))
    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        n = seed_models(s, model_dir)
        s.commit()
    print(f"Models seeded: {n}", file=sys.stderr)
```

- [ ] Step 5: Verify `ruff check scripts/seed_models.py` (note: scripts have mypy override ignore_missing_imports). Run against real models: `$env:MODEL_DIR="D:\Kuliah\Skripsi\Model\Final Model"; .venv\Scripts\python.exe ..\scripts\seed_models.py` — expect "Models seeded: 5". Re-run -> "Models seeded: 0" (idempotent).

- [ ] Step 6: Commit `feat(models): add seed_models.py registering 5 YOLO models with SHA256`.

---
## Phase S16 — AIAnalysis Model + Migration

### Task S16-1: AIAnalysis ORM + migration

**Files:** create `backend/app/db/models/ai_analysis.py`, `backend/tests/unit/db/models/test_ai_analysis.py`; modify `__init__.py`; generate migration.

- [ ] Step 1: Write failing test:
  - test_persists: needs Patient+Encounter+ECGStudy+ModelMetadata fixtures, then AIAnalysis(ecg_study_id, model_metadata_id, predicted_class="mi", confidence_score=0.92, probability_json={...}, status="success", device_used="cpu") persists.
  - test_unique_study_model: same (ecg_study_id, model_metadata_id) twice -> IntegrityError.

- [ ] Step 2: Run, expect FAIL.

- [ ] Step 3: Create model per spec 3.2. Enums: predicted_class ("normal","mi","homi","abnormal") nullable; device_used ("cpu","gpu") default "cpu"; status ("success","failed","skipped"). probability_json Mapped[dict[str, object]] JSON default dict. FKs ecg_study.id + model_metadata.id + indexes. `__table_args__`: UniqueConstraint("ecg_study_id","model_metadata_id", name="uq_analysis_study_model"), Index("ix_analysis_status","status").

- [ ] Step 4: Register in __init__.py ("AIAnalysis").

- [ ] Step 5: Run test, expect 2 passed.

- [ ] Step 6: Migration `alembic revision --autogenerate -m "add ai_analysis table"`, clean, down_revision = model_metadata migration hash. Roundtrip + gate.

- [ ] Step 7: Commit `feat(db): add AIAnalysis model and migration`.

---

## Phase S17 — Inference Services

### Task S17-1: mapping + loader + predict

**Files:** create `backend/app/services/inference/{__init__,mapping,loader,predict}.py`, `backend/tests/unit/services/inference/test_predict.py`.

- [ ] Step 1: `__init__.py` docstring. `mapping.py`:
```python
"""YOLO class-index <-> data-model enum mapping (verified at seed time)."""
YOLO_NAME_TO_ENUM = {
    "abnormal_heartbeat": "abnormal",
    "history_myocardial_infarction": "homi",
    "myocardial_infarction": "mi",
    "normal": "normal",
}
ENUM_ORDER = ["abnormal", "homi", "mi", "normal"]  # YOLO index order
```

- [ ] Step 2: `loader.py` — in-process cache:
```python
"""Cache loaded YOLO models by resolved path (avoid reloading per request)."""
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=8)
def load_model(resolved_path: str) -> Any:
    from ultralytics import YOLO

    if not Path(resolved_path).exists():
        raise FileNotFoundError(f"Model weights not found: {resolved_path}")
    return YOLO(resolved_path)
```

- [ ] Step 3: Write failing test_predict.py. Mock the model object (not ultralytics) — pass a fake model whose .predict returns an object exposing .probs.top1, .probs.top1conf, .probs.data.tolist(). Assert run_inference maps index->enum, returns probs dict keyed by enum, includes inference_ms.

```python
from app.services.inference.predict import run_inference


class _Probs:
    def __init__(self, data, top1):
        self.data = type("T", (), {"tolist": lambda self: data})()
        self.top1 = top1
        self.top1conf = data[top1]


class _Res:
    def __init__(self, data, top1):
        self.probs = _Probs(data, top1)


class _Model:
    def __init__(self, data, top1):
        self._r = _Res(data, top1)

    def predict(self, *a, **k):
        return [self._r]


def test_run_inference_maps_enum():
    # YOLO index order: 0 abnormal, 1 homi, 2 mi, 3 normal
    m = _Model([0.1, 0.15, 0.7, 0.05], top1=2)
    out = run_inference(m, "x.jpg", device="cpu")
    assert out["predicted_class"] == "mi"
    assert round(out["confidence"], 2) == 0.7
    assert set(out["probabilities"]) == {"abnormal", "homi", "mi", "normal"}
    assert out["probabilities"]["normal"] == 0.05
    assert out["inference_ms"] >= 0
```

- [ ] Step 4: Implement predict.py:
```python
"""Run a single YOLO classification inference and map to data-model enums."""
import time
from typing import Any

from app.services.inference.mapping import ENUM_ORDER


def run_inference(model: Any, image_path: str, *, device: str = "cpu") -> dict[str, Any]:
    t0 = time.perf_counter()
    res = model.predict(image_path, device=device, verbose=False)[0]
    elapsed = (time.perf_counter() - t0) * 1000
    probs_list = res.probs.data.tolist()
    top1 = int(res.probs.top1)
    probabilities = {ENUM_ORDER[i]: round(float(p), 4) for i, p in enumerate(probs_list)}
    return {
        "predicted_class": ENUM_ORDER[top1],
        "confidence": round(float(res.probs.top1conf), 4),
        "probabilities": probabilities,
        "inference_ms": round(elapsed, 1),
    }
```

- [ ] Step 5: Run test_predict, expect pass. Gate ruff+mypy. cv2/ultralytics already in mypy overrides? Add override for `ultralytics.*` and `torch.*` ignore_missing_imports if mypy complains.

- [ ] Step 6: Commit `feat(inference): add YOLO mapping, model loader cache, predict`.

### Task S17-2: model_registry query + orchestrate

**Files:** create `backend/app/services/model_registry/{__init__,query}.py`, `backend/app/services/inference/orchestrate.py`, `backend/tests/unit/services/inference/test_orchestrate.py`.

- [ ] Step 1: query.py `list_active_models(session) -> list[ModelMetadata]` ordered by id where is_active.

- [ ] Step 2: Write failing test_orchestrate.py with monkeypatched loader + ECGStudy fixture. Cover: run-all creates N rows status=success; one model raises -> that row failed, others success; idempotent re-run skips existing success.

- [ ] Step 3: Implement orchestrate.py `analyze_study(session, *, study_id, user_id, model_dir)`:
  - get ECGStudy (NotFoundError ENCOUNTER... use ECG_STUDY_NOT_FOUND)
  - abs image path = Path(storage_root? no — image under storage). NOTE image_original_path is relative to STORAGE_DIR. orchestrate needs storage_root too -> add param storage_root.
  - existing = {analysis.model_metadata_id: analysis for success rows}
  - for each active model: skip if already success; else load_model(model_dir/file_path), run_inference, persist row (success/failed), write_audit(action="ai_analysis", entity_type="ai_analysis")
  - return list of AIAnalysis rows for the study

- [ ] Step 4: Run tests, expect pass.

- [ ] Step 5: Commit `feat(inference): add active-model query and run-all orchestrator`.

---
## Phase S18 — API Endpoints

### Task S18-1: schema + endpoints + integration tests

**Files:** create `backend/app/schemas/ai_analysis.py`, `backend/tests/integration/test_ai_analysis_api.py`; modify `backend/app/api/encounters.py`.

- [ ] Step 1: schema `AIAnalysisOut` (BaseModel): id, ecg_study_id, model_metadata_id, model_name (str), architecture (str), predicted_class (str|None), confidence_score (float|None), probability_json (dict), inference_time_ms (int|None), device_used (str), status (str), error_message (str|None), created_at (str).

- [ ] Step 2: Write failing integration test. Mock inference at the orchestrate boundary: monkeypatch `app.services.inference.loader.load_model` to return a fake model (deterministic probs), and set app.config MODEL_DIR/STORAGE_DIR to tmp_path with a seeded ModelMetadata row + a real ECGStudy (upload via the Sprint 2B flow or insert directly). Tests:
  - analyze 201 returns analyses list, rows have predicted_class
  - idempotent: 2nd analyze returns same count, no duplicate
  - consent revoked -> 422 CONSENT_REVOKED
  - researcher POST analyze -> 403
  - GET analyses ordered, researcher can read
  Seed ModelMetadata directly in fixture (avoid needing real weights): insert 2 rows is_active=True with model_file_path pointing at tmp files; monkeypatch load_model so file existence not required.

- [ ] Step 3: Add imports to encounters.py: AIAnalysisOut, analyze_study, list_analyses query, ensure_ai_analysis_consent (already imported for upload). Add `_analysis_to_out(a, model)` serializer joining model_name/architecture.

- [ ] Step 4: POST `/<int:encounter_id>/ecg-studies/<int:study_id>/analyze` @require_role(CLINICIAN, NURSE):
  - resolve encounter+study, derive patient_id, ensure_ai_analysis_consent (revoked->422)
  - storage_root = Path(current_app.config["STORAGE_DIR"]); model_dir = Path(current_app.config["MODEL_DIR"])
  - rows = analyze_study(session, study_id=study_id, user_id=_user_id(), model_dir=model_dir, storage_root=storage_root, **_ctx())
  - commit; return jsonify(analyses=[_analysis_to_out(...)]), 201

- [ ] Step 5: GET `/<int:encounter_id>/ecg-studies/<int:study_id>/analyses` @require_role(ADMIN, CLINICIAN, NURSE, RESEARCHER): list rows joined with model, return items.

- [ ] Step 6: Run tests, expect pass. Full backend gate `ruff check . && mypy . && pytest tests`.

- [ ] Step 7: Commit `feat(api): add ECG analyze + analyses endpoints (5-model run)`.

---

## Phase S19 — Frontend AnalysisPanel

### Task S19-1: api client + AnalysisPanel + test

**Files:** create `frontend/src/features/ai_analysis/{api.ts,AnalysisPanel.tsx,AnalysisPanel.test.tsx}`; modify the ECG study area (EcgStudyList card or Detail) to mount per-study panel.

- [ ] Step 1: api.ts — interface AnalysisRow (mirror AIAnalysisOut), analysisKeys.list(studyId), fetchAnalyses(encounterId, studyId) via apiFetch GET, runAnalysis(encounterId, studyId) via apiFetch POST (JSON, no body). Error -> body.error.message_id.

- [ ] Step 2: Write failing AnalysisPanel.test.tsx — mock fetchAnalyses returning 2 rows (mi/normal), render in QueryClientProvider, assert architecture text + predicted class chip render.

- [ ] Step 3: Implement AnalysisPanel:
  - useQuery(analysisKeys.list) fetchAnalyses
  - useMutation runAnalysis -> invalidate on success
  - "Jalankan Analisis AI" button (disabled while pending) when no rows; "Analisis ulang" when rows exist
  - comparison table: architecture | predicted class chip (color by enum: normal=affirmed, abnormal=caution, mi/homi=negative) | confidence bar (tabular %) | status
  - consensus line: majority predicted_class
  - EmptyState when none
  - props: { encounterId, studyId }

- [ ] Step 4: Mount in EcgStudyList card (add an expandable "Analisis AI" section per study) OR add to Detail under study list. Simplest: render `<AnalysisPanel encounterId studyId={String(s.id)} />` inside each study card footer (collapsible). Keep card not too tall — use a details/summary or a toggle.

- [ ] Step 5: Run test, expect pass. Frontend gate lint+typecheck+test+build.

- [ ] Step 6: Commit `feat(ai-ui): add AnalysisPanel with 5-model comparison table`.

---

## Phase S20 — ADR Amend + Final

### Task S20-1: amend ADR-0004 + README + dependency + final gate

**Files:** modify `docs/adr/0004-three-yolo-models-comparison.md`, `README.md`, `backend/pyproject.toml`.

- [ ] Step 1: pyproject.toml dependencies add `ultralytics>=8.4`. (torch pulled transitively; document CPU wheel in a comment or README.) Add mypy overrides for `ultralytics.*` and `torch.*` ignore_missing_imports if not already present.

- [ ] Step 2: Amend ADR-0004 in-place: keep Status Accepted, add a dated note under Decision: "2026-05-31: scope expanded from 3 to 5 models (yolov8n/s, yolov11n/s, yolov26n) after the training pass produced five comparable classifiers; all share the 4-class output (normal/mi/homi/abnormal)." Update title/consequences as needed.

- [ ] Step 3: README dev-status table: Sprint 3 -> Done note; badge bump if applicable. Add a line on MODEL_DIR setup for first run.

- [ ] Step 4: Full backend gate: `ruff check . && mypy . && pytest tests --cov`. Full frontend gate. markdownlint on changed docs.

- [ ] Step 5: Commit `docs(adr): amend ADR-0004 to five YOLO models; sprint-3 wrap`.

---

## Final Verification

- [ ] Backend: ruff + mypy clean, all tests pass (~245+), coverage maintained
- [ ] Frontend: lint + typecheck + prettier + test + build clean
- [ ] AC-1..AC-10 each covered by a passing test or manual check
- [ ] Manual smoke (local, real models): set MODEL_DIR, seed_models, upload ECG, run analyze, see 5-model table
- [ ] Push feat/sprint-3/impl, PR, CI green, squash-merge, tag v0.5.0-sprint-3, release
