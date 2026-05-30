# Architecture Overview Design - EKG-Insight CDSS v2

| Item | Keterangan |
| --- | --- |
| Dokumen | Architecture Overview Design |
| Produk | EKG-Insight CDSS (Interpretable CDSS Berbasis Citra EKG 12-Lead) |
| Versi | 1.0 |
| Tanggal | 2026-05-30 |
| Status | Approved design - basis implementasi |
| Target Publikasi | Scopus Q2/Q3 |
| Referensi | docs/Grand_PRD_CDSS_EKG_HiResCAM_v3.md (PRD v3) |
| Dokumen Terkait | data-model-and-phi-design, decision-engine-design, sprint-1-foundation-design |

## 1. Identitas dan Konteks

EKG-Insight CDSS adalah Clinical Decision Support System berbasis web untuk skrining awal abnormalitas citra EKG 12-lead, dengan fokus Myocardial Infarction pada fasilitas kesehatan primer dan terpencil (low-resource settings).

Versi 2 (v2) ini adalah penulisan ulang dari v1. Pemisahan utama: training model dilakukan di Kaggle, sedangkan repository ini hanya mengonsumsi artefak model (file `.pt`). v2 tidak melakukan training apa pun.

Sistem dirancang sebagai deployable prototype research-grade, bukan certified medical device. Setiap instance dijalankan pada satu fasilitas kesehatan (single-facility per instance).

### Prinsip Inti

| Prinsip | Implikasi Desain |
| --- | --- |
| Human-in-the-loop | Semua hasil AI ditinjau pengguna klinis sebelum disposition. |
| Screening, not diagnosis | Output hanya skrining awal + saran tindakan umum. |
| Explainability-first | Setiap prediksi disertai HiResCAM. |
| Low-resource readiness | CPU-only, offline-capable, ringan, lokal. |
| Auditability | Model version, confidence, heatmap, decision path, audit log tersimpan. |
| Phased development | Phase 1 classification aktif; Phase 2 detection dormant. |
| Maintainability | One file per concept; line budget ketat. |

## 2. Tech Stack Final

### Backend (Python)

| Komponen | Pilihan | Peran |
| --- | --- | --- |
| Web framework | Flask | HTTP routing, blueprints |
| ORM | SQLAlchemy 2.0 (typed) | Persistence layer |
| Migration | Alembic | Schema evolution |
| Validation | Pydantic v2 | Request/response DTO |
| Auth | Flask-JWT-Extended | Access + refresh token |
| Logging | structlog | JSON structured logs untuk audit |
| Crypto | cryptography (Fernet) | Field-level PHI encryption |
| AI runtime | PyTorch + Ultralytics | YOLO classification inference |
| Explainability | pytorch-grad-cam (HiResCAM) | Visual explanation |
| PDF | ReportLab | Laporan pemeriksaan |
| Testing | pytest | Unit + integration |
| Lint/Type | ruff + mypy | Code quality |

### Frontend (TypeScript)

| Komponen | Pilihan | Peran |
| --- | --- | --- |
| Framework | React 18 + Vite | SPA + fast HMR |
| Bahasa | TypeScript | Type safety end-to-end |
| Server state | TanStack Query | Data fetching + cache |
| Client state | Zustand | UI state ringan |
| Styling | Tailwind CSS | Utility-first |
| Komponen | shadcn/ui | Accessible primitives |
| Routing | React Router | Navigasi |
| Testing | Vitest + Playwright | Unit + e2e |
| Lint/Format | eslint + prettier | Code quality |

### Infrastructure

| Komponen | Pilihan | Peran |
| --- | --- | --- |
| Database | SQLite | Zero-config local DB |
| Replication | Litestream | WAL streaming backup |
| File storage | Local filesystem | Uploads, heatmaps, reports |
| API | REST + OpenAPI | Kontrak terdokumentasi |
| Deployment | Single process (prod) | Flask serve React build |

## 3. Repository Structure (Top-Level)

```
CDSS-web-project-v2/
  backend/                  # Flask app + AI services (Python)
  frontend/                 # React SPA (TypeScript)
  models/                   # Artefak .pt dari Kaggle (read-only)
  storage/                  # Runtime artifacts (uploads, heatmaps, reports)
  data/                     # SQLite DB file (cdss.db)
  secrets/                  # master.key (NEVER commit)
  docs/                     # PRD, design specs, reference
  scripts/                  # Dev/build/deploy automation
  tests/                    # E2E tests (Playwright)
  litestream.yml            # Litestream replication config
  .env.example
  .gitignore
  README.md
```

Mode dev: Vite dev server (port 5173) + Flask (port 5000), Vite proxy `/api` ke Flask.
Mode prod: build React ke `backend/app/static/`, jalankan Flask saja (1 proses, low-resource).

## 4. Component Responsibility Matrix

| Komponen | Layer | PRD Reference |
| --- | --- | --- |
| backend/app/api/auth | HTTP | FR-01, FR-02 |
| backend/app/api/ecg | HTTP | FR-03..FR-11 |
| backend/app/services/upload | Business | FR-03, FR-04 |
| backend/app/services/image_quality | Business | FR-05 |
| backend/app/services/preprocessing | Business | FR-06 |
| backend/app/services/inference | Business | FR-07, FR-08 |
| backend/app/services/hirescam | Business | FR-09 |
| backend/app/services/recommendation | Business | FR-10 |
| backend/app/services/report | Business | FR-14 |
| backend/app/services/audit | Business | FR-16 |
| backend/app/services/evaluation | Business | FR-15 |
| backend/app/core/disclaimer | Cross-cutting | Section 18 (safety) |
| backend/app/db/models | Persistence | data-model doc (22 tabel) |
| frontend/features/ecg-result | UI | Section 16 Result Page |
| frontend/features/research | UI | Section 16 Research Dashboard |

## 5. Maintainability Rulebook

### Line Budget per File

| Tipe File | Target | Hard Ceiling |
| --- | --- | --- |
| Pure utility / helper | 80 | 150 |
| Single-class service | 150 | 250 |
| Orchestrator / pipeline | 200 | 250 |
| ORM model | 120 | 200 |
| API blueprint / route | 150 | 250 |
| Pydantic schema | 150 | 200 |
| React component | 120 | 200 |
| React route page | 100 | 150 |
| Test file | 250 | 350 |

Aturan emas: jika file mencapai 80% target, stop dan split. Jangan tunggu ceiling.

### Decomposition Principles

1. One file = one concept (satu rule, satu check, satu section = satu file).
2. Page/Orchestrator = composition only, tanpa logika sendiri.
3. Public surface via `__init__.py`; internal detail private.
4. Numbered prefix untuk pipeline berurutan (`_01_validate.py`).
5. Domain-noun untuk entitas (`examination.py`).
6. Test mirror struktur source.

### Library Wrapping Rule

Setiap penggunaan komponen library berulang dengan konfigurasi khusus = file sendiri. Jangan inline-config library di dalam page/section. Contoh: shadcn compositions di `components/composed/`, chart wrappers di `components/charts/`, ReportLab flowables di `services/report/flowables/`.

## 6. Naming Conventions

| Pola | Penggunaan |
| --- | --- |
| `snake_case.py` | Python module/file |
| `PascalCase.tsx` | React component |
| `camelCase.ts` | Hook/utility TS |
| `_NN_name.py` | Pipeline step (NN = order) |
| `dt_NN_descriptor.py` | Decision rule Phase 1 |
| `r_NN_descriptor.py` | Triage rule Phase 2 |

## 7. Sprint Roadmap

| Sprint | Fokus | Output |
| --- | --- | --- |
| 1 | Project Foundation | Repo, DB, storage, auth skeleton, encryption bootstrap, audit, CI |
| 2 | Auth & Upload | Login, RBAC, patient/encounter, upload, validation, image quality |
| 3 | AI Inference | Load 3 model YOLO, model registry, prediction endpoint |
| 4 | HiResCAM | Heatmap, overlay, explanation status, storage |
| 5 | Recommendation | DT-01..DT-10, risk level, bilingual recommendation, decision path |
| 6 | History & PDF | Examination history, detail, PDF report |
| 7 | Research Dashboard | Confusion matrix, metrics, model comparison, low-resource score |
| 8 | Audit & Finalization | Audit trail, security hardening, docs, demo-ready |
| 9 | Phase 2 Preparation | Annotation protocol, detection schema, expert review workflow, R1-R17 |

Setiap sprint mendapat design doc + implementation plan sendiri (pendekatan decompose-per-sprint).

## 8. Publication Readiness Plan (Scopus Q2/Q3)

| Aspek | Tambahan Publication-Grade |
| --- | --- |
| Reproducibility | Dataset version pinning, model checksum, config versioning, seed tracking, environment lockfile |
| Methodology | Stratified train/val/test split, cross-validation protocol, significance tests |
| Metrics | ROC-AUC, PR-AUC, Cohen's kappa, MCC, per-class metrics, confidence intervals |
| Model comparison | McNemar's test untuk paired predictions |
| HiResCAM eval | IoU vs expert annotation, faithfulness (deletion/insertion AUC) |
| Decision validation | Inter-rater agreement Sp.JP (kappa), coverage analysis, edge case audit |
| Clinical safety | Pre-registered analysis plan, harms-benefits trade-off |
| Ethics | IRB/ethical clearance reference, consent process |
| Limitations | Generalizability, dataset bias, demographic representation |

## 9. Referensi Dokumen

| Dokumen | Isi |
| --- | --- |
| data-model-and-phi-design.md | 22 tabel + PHI strategy |
| decision-engine-design.md | DT-01..DT-10 + R1-R17 + co-design |
| sprint-1-foundation-design.md | Detail Sprint 1 |
| color-system-and-tokens-design.md | Color system + 12 kategori design tokens |
| Grand_PRD_CDSS_EKG_HiResCAM_v3.1_delta.md | Update PRD untuk faskes primer/terpencil |
| reference/01_Rule_Based_Design_source.md | Sumber rule base original |
| adr/README.md | Index 14 Architecture Decision Records |
| operations/git-workflow.md | Branch strategy GitHub Flow + sprint tags |
| operations/commit-convention.md | Conventional Commits + scopes |
| operations/pr-flow.md | PR lifecycle + self-review checklist |
| operations/release-process.md | release-please + sprint release |
| operations/branch-protection.md | Branch protection settings |
| operations/repo-setup.md | First-time GitHub setup checklist |
