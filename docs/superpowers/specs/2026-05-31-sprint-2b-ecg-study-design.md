# Sprint 2B: ECGStudy Layer — Design Spec

| Item | Keterangan |
| --- | --- |
| Dokumen | Sprint 2B ECGStudy Design |
| Versi | 1.0 |
| Tanggal | 2026-05-31 |
| Status | Approved design |
| Referensi | data-model-and-phi-design.md, sprint-2a-clinical-context.md, ADR-0008 |

## 1. Konteks

Sprint 2A menyelesaikan clinical-context layer (Patient, Encounter, ClinicalContext, VitalSigns, Consent, PatientHistory) — 12 model, 192 backend tests, 20 frontend tests, tagged `v0.2.0-sprint-2a`.

Sprint 2B menambahkan **ECGStudy** — entitas yang menghubungkan gambar EKG dengan Encounter. Ini adalah jembatan antara clinical context (Sprint 2A) dan AI analysis (Sprint 3). Model YOLO sudah di-train oleh user dan akan diintegrasikan di Sprint 3.

### Scope

**In scope (Sprint 2B):**
- 1 new ORM model: `ECGStudy`
- 1 Alembic migration
- 3 new service domains: upload, quality check, query
- 2 new API endpoints (POST/GET nested under encounter)
- Frontend: upload form + study list di Encounter Detail
- `storage/` directory structure for uploaded images
- `ai_analysis` consent auto-capture saat upload pertama

**Out of scope (explicit):**
- ModelMetadata, AIAnalysis (Sprint 3)
- HiResCAM (Sprint 4)
- Recommendation, Disposition, Referral (Sprint 5)
- Image preprocessing (resize, crop, normalize) — Sprint 3
- Real YOLO inference — Sprint 3
- PDF report — Sprint 6

## 2. ECGStudy Model

Schema dari data-model spec Section 4.4:

| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | Auto-increment |
| encounter_id | int FK | encounter.id, indexed |
| patient_id | uuid FK | patient.id, indexed (redundant untuk query) |
| study_uid | str unique | Format: ECG-{facility_code}-{timestamp}-{random4} |
| image_original_path | str | Relative path dari storage root |
| image_processed_path | str OR None | Untuk preprocessed image (Sprint 3) |
| image_quality_status | enum | good / acceptable / poor |
| image_quality_score | float | 0.0 - 1.0 |
| image_quality_metrics_json | json | blur, noise, brightness, contrast |
| acquired_at | datetime | Default: now |
| recorded_by_user_id | int FK | user.id |
| device_info | str OR None | Opsional |
| created_at | datetime | Default: now |

Indexes: `encounter_id`, `patient_id`, unique `study_uid`, composite `(encounter_id, created_at)`.

Relationship: Encounter (1) -< ECGStudy (M); Patient (1) -< ECGStudy (M); User (1) -< ECGStudy (M).

## 3. Image Upload Service

Validation rules:

| Rule | Value | Error Code |
| --- | --- | --- |
| Allowed formats | JPEG, PNG | INVALID_FILE_FORMAT |
| Max file size | 10 MB | FILE_TOO_LARGE |
| Min file size | 1 KB | FILE_TOO_SMALL |
| MIME type | image/jpeg, image/png | INVALID_FILE_FORMAT |
| Magic bytes | FF D8 (JPEG), 89 50 4E 47 (PNG) | INVALID_FILE_FORMAT |

Storage: `storage/uploads/ecg/{facility_id}/{encounter_id}/{study_uid}.{ext}`. Path di DB relatif terhadap storage root. Never trust client filename/MIME. No executable extensions. Path traversal dicegah dengan konstruksi path server-side.

## 4. Image Quality Check (OpenCV)

| Metric | Method | Good | Acceptable | Poor |
| --- | --- | --- | --- | --- |
| Blur | Laplacian variance | >= 100 | 50-100 | < 50 |
| Brightness | Mean intensity | 80-180 | 50-80 / 180-220 | else |
| Contrast | Stddev intensity | >= 40 | 20-40 | < 20 |
| Noise | Gaussian blur diff stddev | < 15 | 15-30 | > 30 |

Composite score: weighted (blur 35%, contrast 25%, brightness 20%, noise 20%). Status: good >= 0.7, acceptable >= 0.4, poor < 0.4.

Dependency: `opencv-python-headless` (~30MB). No GUI components, suitable for server deployment.

## 5. Consent Gate (ai_analysis)

Upload ECGStudy memerlukan consent `ai_analysis`. Progressive capture (sama seperti `data_use` saat register di Sprint 2A):

1. Check `has_consent(patient_id, "ai_analysis")`
2. Belum ada consent (tidak ada row sama sekali) → auto-capture (status=given), lalu proceed
3. Sudah given → proceed
4. Sudah revoked (row terakhir status=revoked) → raise `CONSENT_REVOKED` (422)

Rationale: auto-capture konsisten dengan pola `data_use` di Sprint 2A; consent tetap tercatat untuk audit; revoke eksplisit tetap dihormati.

## 6. API Endpoints

### POST /api/encounters/{encounter_id}/ecg-studies

multipart/form-data: `file` (required), `device_info` (optional). Role: clinician | nurse.

Flow: validate encounter exists → get patient_id → consent check/auto-capture → validate file → save → quality check → INSERT ECGStudy → audit log (action=ecg_upload) → 201.

Responses: 201 {study: ECGStudyOut}; 404 ENCOUNTER_NOT_FOUND; 422 INVALID_FILE_FORMAT/FILE_TOO_LARGE/FILE_TOO_SMALL/CONSENT_REVOKED; 403 AUTH_FORBIDDEN.

### GET /api/encounters/{encounter_id}/ecg-studies

Role: admin | clinician | nurse | researcher. Returns {items: [...]} ordered by created_at DESC. Researcher gets anonymized (no patient_id, no device_info).

ECGStudyOut: id, encounter_id, patient_id, study_uid, image_original_path, image_processed_path, image_quality_status, image_quality_score, image_quality_metrics_json, acquired_at, recorded_by_user_id, device_info, created_at.

## 7. Frontend

EcgUploadForm: drag-and-drop + file input, client-side format/size validation, thumbnail preview, upload progress, quality status badge (green good / yellow acceptable / red poor) after upload.

EcgStudyList: table with Study UID, Quality Status badge, Quality Score, Acquired At. Click row to view image (new tab via static path).

Integration: replace "Upload EKG akan diaktifkan di Sprint 2B" placeholder in Encounter Detail.tsx.

## 8. Migration

Single migration for ecg_study table (mengikuti pola Sprint 2A — satu migration per phase). Roundtrip clean (upgrade/downgrade).

## 9. Acceptance Criteria

| # | Kriteria |
| --- | --- |
| AC-1 | Migration adds ecg_study table; downgrade -1 succeeds without data loss for Sprint 2A tables |
| AC-2 | POST valid JPEG → 201, file saved to storage path, ECGStudy row with quality metrics |
| AC-3 | POST invalid format (GIF/BMP/WebP) → 422 INVALID_FILE_FORMAT |
| AC-4 | POST file > 10MB → 422 FILE_TOO_LARGE |
| AC-5 | POST without ai_analysis consent → auto-capture (status=given) + proceed |
| AC-6 | POST with revoked ai_analysis consent → 422 CONSENT_REVOKED |
| AC-7 | Quality check produces score (0-1) + status + metrics JSON with blur/noise/brightness/contrast |
| AC-8 | GET returns list ordered by created_at DESC |
| AC-9 | RBAC: upload=clinician/nurse; read=admin/clinician/nurse/researcher; researcher anonymized |
| AC-10 | Frontend: drag-drop upload, quality badge, study list |

## 10. Test Strategy

Backend: 17 tests (model 2, upload 4, quality 3, API 8). Frontend: 3 tests. Total ~20 new tests.

## 11. Phases

| Phase | Deliverable |
| --- | --- |
| S8 | ECGStudy model + migration |
| S9 | Image upload service (validasi + storage) |
| S10 | Image quality check (OpenCV) |
| S11 | Consent gate + upload orchestration |
| S12 | API endpoints |
| S13 | Frontend (upload form + study list) |

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| OpenCV headless install fails | Quality check unavailable | Pillow-only fallback (future) |
| Large uploads timeout | Upload failure | Chunked upload (future) |
| Storage disk full | Upload failure | Disk space check (future) |
| Quality thresholds not tuned | Poor classification | SystemConfig override (future) |

## 13. Dependencies

Backend: `opencv-python-headless`. Frontend: none (existing shadcn + TanStack Query). Infra: `storage/` dir with write perms; `.gitignore` entry for `storage/uploads/` (ECG images are clinical data).
