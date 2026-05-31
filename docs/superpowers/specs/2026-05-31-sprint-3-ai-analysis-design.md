# Sprint 3: AIAnalysis Layer (5 YOLO Models) — Design Spec

| Item | Keterangan |
| --- | --- |
| Dokumen | Sprint 3 AIAnalysis Design |
| Versi | 1.0 |
| Tanggal | 2026-05-31 |
| Status | Approved design |
| Referensi | data-model-and-phi-design.md, ADR-0004, ADR-0009, sprint-2b-ecg-study |

## 1. Konteks

Sprint 2B menyelesaikan ECGStudy layer (upload, quality check, consent gate). Sprint 3 menambahkan **AIAnalysis** — menjalankan model YOLO classification pada citra EKG yang sudah di-upload, menghasilkan prediksi kelas + confidence + probabilities per model.

Model sudah di-train oleh user (5 model, lokasi `D:\Kuliah\Skripsi\Model\Final Model\`). HiResCAM (explainability) ditunda ke Sprint 4.

### Scope

**In scope (Sprint 3):**
- 2 new ORM models: ModelMetadata, AIAnalysis
- 2 Alembic migrations
- seed_models.py script (register 5 model + SHA256 checksum)
- Inference services (loader cache, predict, run-all-active orchestrator)
- 2 API endpoints (POST analyze, GET analyses) nested under ecg-study
- Frontend AnalysisPanel (trigger + 5-model comparison table)
- ADR-0004 amend in-place (3 -> 5 models)

**Out of scope (explicit):**
- HiResCAMArtifact + heatmap (Sprint 4)
- Recommendation / DecisionTree engine (Sprint 5)
- Disposition / Referral (Sprint 5)
- Async inference / background worker (synchronous only)
- GPU inference (CPU-only)
- ONNX export (defer ke optimization pass)
- Model re-training feedback loop (research workflow di luar app)

## 2. Detected Model Facts (verified)

5 model di `Final Model/`, semua task=classify, 4 kelas identik:

| Folder | best.pt | Arsitektur | Class names (index order) |
| --- | --- | --- | --- |
| yolov8n_cls | 2.83 MB | YOLOv8 nano | abnormal_heartbeat, history_myocardial_infarction, myocardial_infarction, normal |
| yolov8s_cls | 9.79 MB | YOLOv8 small | (sama) |
| yolo11n_cls | 3.04 MB | YOLOv11 nano | (sama) |
| yolo11s_cls | 10.52 MB | YOLOv11 small | (sama) |
| yolo26n_cls | 3.04 MB | YOLOv26 nano | (sama) |

Inference smoke test (synthetic 224x224, CPU): ~93ms per model. 5 model sekuensial ~465ms + load. Synchronous mode layak.

### Class mapping (YOLO -> data-model enum)

| YOLO index | YOLO name | data-model enum (predicted_class) |
| --- | --- | --- |
| 0 | abnormal_heartbeat | abnormal |
| 1 | history_myocardial_infarction | homi |
| 2 | myocardial_infarction | mi |
| 3 | normal | normal |

Mapping ini disimpan sebagai konstanta di inference service. probability_json menyimpan per-enum probability.

## 3. Model Schemas

### 3.1 ModelMetadata

| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| model_name | str | yolov8n-cls / yolov11n-cls / yolov26n-cls / etc |
| model_version | str | training tag, e.g. v1.0 |
| architecture | str | YOLOv8n / YOLOv8s / YOLOv11n / YOLOv11s / YOLOv26n |
| task_type | enum | classification (only) |
| input_size | int | 224 default |
| model_file_path | str | relative to MODEL_DIR, e.g. yolov8n_cls/best.pt |
| model_checksum | str | SHA256 of best.pt (reproducibility) |
| model_size_mb | float | |
| class_names_json | json | ordered list from model.names |
| threshold_config_json | json | per-class confidence cutoff (default empty) |
| is_active | bool | only active models run on analyze |
| training_date | date OR None | |
| created_at | datetime | |

Indexes: unique (model_name, model_version); is_active.

### 3.2 AIAnalysis

| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| ecg_study_id | int FK | ecg_study.id, indexed |
| model_metadata_id | int FK | model_metadata.id, indexed |
| predicted_class | enum OR None | normal/mi/homi/abnormal (None if failed) |
| confidence_score | float OR None | top-1 probability |
| probability_json | json | per-enum probabilities |
| inference_time_ms | int OR None | |
| device_used | enum | cpu (only for now) |
| inference_started_at | datetime OR None | |
| inference_finished_at | datetime OR None | |
| status | enum | success / failed / skipped |
| error_message | str OR None | when status=failed |
| created_at | datetime | |

Indexes: (ecg_study_id, model_metadata_id) unique together; status. Relationship: 1 ECGStudy : N AIAnalysis (one row per active model).

## 4. Inference Services

### 4.1 loader.py
- `load_model(path: Path) -> YOLO` with in-process LRU cache keyed by resolved path (avoid reloading 5 models on every request)
- Resolve path against MODEL_DIR config

### 4.2 predict.py
- `run_inference(model, image_path, *, device="cpu") -> dict` returns {top1_idx, top1_conf, probs (per YOLO index), inference_ms}
- Map YOLO index -> enum via constant
- Pure-ish: takes a loaded model + path, returns plain dict (no DB)

### 4.3 orchestrate.py
- `analyze_study(session, *, study_id, user_id, model_dir) -> list[AIAnalysis]`
- Flow: load ECGStudy (404 if missing) -> resolve image abs path -> list active ModelMetadata -> for each: run_inference (try/except -> status success/failed) -> persist AIAnalysis row -> write_audit(action="ai_analysis")
- Idempotency: skip models that already have a success row for the study; re-run only missing/failed
- One model failure does not block others

## 5. Consent

ai_analysis consent already enforced at upload (Sprint 2B). Analyze re-checks via ensure_ai_analysis_consent (revoked -> 422 CONSENT_REVOKED) as defense-in-depth.

## 6. API Endpoints

### POST /api/encounters/{encounter_id}/ecg-studies/{study_id}/analyze
- Role: clinician | nurse
- Re-check ai_analysis consent (revoked -> 422)
- Run all active models (synchronous), commit, return 201 {analyses: [...]}
- Idempotent: existing success rows preserved; only missing/failed re-run
- 404 if study not found

### GET /api/encounters/{encounter_id}/ecg-studies/{study_id}/analyses
- Role: admin | clinician | nurse | researcher
- Returns {items: [AIAnalysisOut, ...]} ordered by model_metadata_id
- Researcher: same data (no PHI in analysis rows; clinical T4)

### AIAnalysisOut schema
id, ecg_study_id, model_metadata_id, model_name (joined), architecture (joined),
predicted_class, confidence_score, probability_json, inference_time_ms,
device_used, status, error_message, created_at

## 7. Frontend

### AnalysisPanel (features/ai_analysis/)
- "Jalankan Analisis AI" button (triggers POST analyze, disabled while pending)
- After run: comparison table — one row per model: architecture, predicted class chip (color by enum), confidence bar (tabular %), status
- Consensus summary: majority predicted_class across models (informational)
- Per-class probability shown on row expand or tooltip
- EmptyState when no analysis yet
- Wired into Encounter Detail under each ECG study (or study detail section)

### Predicted class chip colors (clinical palette)
- normal -> affirmed (petrol)
- abnormal -> caution (amber)
- mi -> negative (wine)
- homi -> negative-soft / wine outline

## 8. Migrations

2 migrations: model_metadata table, ai_analysis table. Roundtrip clean. down_revision chains off current head (ecg_study migration c5d8f21b44c0).

## 9. Acceptance Criteria

| # | Kriteria |
| --- | --- |
| AC-1 | Migrations add model_metadata + ai_analysis; downgrade succeeds |
| AC-2 | seed_models.py registers 5 models with SHA256 checksum + class_names from model.names (idempotent) |
| AC-3 | POST analyze runs all active models, creates one AIAnalysis row each, returns 201 |
| AC-4 | predicted_class correctly mapped from YOLO index to enum (normal/mi/homi/abnormal) |
| AC-5 | probability_json contains per-enum probabilities summing ~1.0 |
| AC-6 | One model failure -> that row status=failed, others still success (partial resilience) |
| AC-7 | Idempotent: second analyze does not duplicate success rows |
| AC-8 | Revoked ai_analysis consent -> 422 CONSENT_REVOKED |
| AC-9 | GET analyses returns rows ordered; RBAC enforced (researcher read, no analyze) |
| AC-10 | Frontend: trigger button + comparison table with predicted class chips + confidence bars |

## 10. Test Strategy

Inference unit tests mock the YOLO loader (synthetic logits) so CI needs no model files. One integration smoke test marked skip-if-no-model for local validation.

| Domain | Test | Type |
| --- | --- | --- |
| ModelMetadata | persists + unique (name,version) | unit |
| AIAnalysis | persists + unique (study,model) | unit |
| predict | YOLO idx->enum mapping | unit (mocked) |
| orchestrate | run-all, partial failure, idempotency | unit (mocked loader) |
| API | analyze 201 + rows | integration (mocked inference) |
| API | consent revoked 422 | integration |
| API | idempotent re-run | integration |
| API | RBAC researcher 403 on analyze | integration |
| API | GET analyses ordered | integration |
| Frontend | AnalysisPanel renders table + chips | unit |

## 11. Phases

| Phase | Deliverable |
| --- | --- |
| S14 | ModelMetadata model + migration |
| S15 | seed_models.py (5 models + SHA256 + class_names) |
| S16 | AIAnalysis model + migration |
| S17 | Inference services (loader, predict, orchestrate) |
| S18 | API endpoints + schema + integration tests |
| S19 | Frontend AnalysisPanel |
| S20 | ADR-0004 amend + README + final gate |

## 12. Dependencies

Backend: ultralytics (+torch CPU ~700MB). pyproject.toml dependencies updated. opencv-python-headless retained (ultralytics installed without pulling opencv-python). Frontend: none new.

## 13. Risks

| Risk | Mitigation |
| --- | --- |
| torch install size (~700MB) | CPU wheel only; documented; ONNX defer |
| Model files absent in CI | inference mocked in tests; smoke test skip-if-missing |
| Inference slow on weak CPU | 5 nano/small ~0.5s acceptable; async defer to pass-2 |
| Class name drift in future models | seed_models stores class_names_json per model; mapping verified at seed |
| MODEL_DIR misconfig | seed + analyze fail loudly with clear error |
