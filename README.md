# EKG-Insight CDSS

> Interpretable Clinical Decision Support System for ECG-based Myocardial Infarction screening in low-resource primary healthcare settings.
> Sistem Pendukung Keputusan Klinis interpretable untuk skrining Myocardial Infarction berbasis citra EKG 12-lead pada fasilitas kesehatan primer dan terpencil.

![status](https://img.shields.io/badge/status-research_prototype-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.13-blue)
![node](https://img.shields.io/badge/node-24-green)
![sprint](https://img.shields.io/badge/sprint-2a_clinical_context-blue)
![ci](https://github.com/nndda-rzn/cdss-v2/actions/workflows/ci.yml/badge.svg)

> This repository is currently **private** as part of an ongoing research project. It will be made public upon paper publication.

---

## English

### Overview

EKG-Insight CDSS is a web-based clinical decision support system that assists early screening of 12-lead ECG image abnormalities, focusing on Myocardial Infarction (MI). It combines:

- **YOLO classification** (YOLOv8n-cls, YOLOv11n-cls, YOLOv26n-cls) for ECG image class prediction
- **HiResCAM** for visual explanation (inferno colormap, perceptually uniform)
- **Decision Tree / Rule-Based recommendation** for risk level and general follow-up advice

It is designed for **low-resource settings**: CPU-only inference, offline-capable, lightweight, and locally deployable on a single healthcare facility per instance.

**This is a research prototype, NOT a certified medical device.** It provides screening support only - never final diagnosis, treatment, or prescription. All results require confirmation by a qualified healthcare professional.

### Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Flask, SQLAlchemy 2.0, Alembic, Pydantic, Flask-JWT-Extended, structlog |
| Frontend | React 18, Vite, TypeScript, TanStack Query, Tailwind CSS, shadcn/ui |
| Database | SQLite + Litestream |
| AI | PyTorch, Ultralytics YOLO, pytorch-grad-cam (HiResCAM) |
| Security | cryptography (Fernet field encryption) |

### Quick Start

```bash
# Backend
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -e .
python ../scripts/init_secrets.py
alembic upgrade head
python ../scripts/seed_facility.py
python ../scripts/seed_admin.py
python ../scripts/seed_system_config.py
# Sprint 3: register the 5 trained YOLO models (set MODEL_DIR to your weights folder)
pip install -e ".[inference]"  # YOLO runtime (torch); not needed for tests
$env:MODEL_DIR="path/to/Final Model"; python ../scripts/seed_models.py
flask run

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

See [docs/operations/repo-setup.md](docs/operations/repo-setup.md) for full setup.

After login, Sprint 2A enables the clinical-context flow: register a patient,
create an encounter, then capture clinical context and vital signs. Image upload
and AI analysis arrive in later sprints.

### Documentation

| Document | Description |
| --- | --- |
| [PRD v3](docs/Grand_PRD_CDSS_EKG_HiResCAM_v3.md) | Product requirements |
| [PRD v3.1 Delta](docs/Grand_PRD_CDSS_EKG_HiResCAM_v3.1_delta.md) | Updates for primary/remote facility |
| [Architecture](docs/superpowers/specs/2026-05-30-architecture-overview-design.md) | Tech stack, structure, conventions |
| [Data Model & PHI](docs/superpowers/specs/2026-05-30-data-model-and-phi-design.md) | 22-table schema + PHI strategy |
| [Decision Engine](docs/superpowers/specs/2026-05-30-decision-engine-design.md) | DT-01..DT-10 + R1-R17 |
| [Color System & Tokens](docs/superpowers/specs/2026-05-30-color-system-and-tokens-design.md) | Design tokens |
| [ADR Index](docs/adr/README.md) | Architecture decisions |

### Security & Privacy

Patient Health Information (PHI) is protected via layered encryption. See [SECURITY.md](SECURITY.md). Never commit real patient data, secrets, or model weights.

### License

[MIT](LICENSE) with clinical disclaimer.

---

## Bahasa Indonesia

### Ikhtisar

EKG-Insight CDSS adalah sistem pendukung keputusan klinis berbasis web untuk membantu skrining awal abnormalitas citra EKG 12-lead, dengan fokus Myocardial Infarction (MI). Sistem menggabungkan:

- **Klasifikasi YOLO** (YOLOv8n-cls, YOLOv11n-cls, YOLOv26n-cls) untuk prediksi kelas citra EKG
- **HiResCAM** untuk penjelasan visual (colormap inferno, perceptually uniform)
- **Decision Tree / Rule-Based recommendation** untuk risk level dan saran tindak lanjut umum

Dirancang untuk **low-resource settings**: inferensi CPU-only, dapat offline, ringan, dan dapat dijalankan lokal per satu fasilitas kesehatan.

**Ini adalah prototype penelitian, BUKAN medical device tersertifikasi.** Sistem hanya membantu skrining - bukan diagnosis final, terapi, atau resep. Semua hasil wajib dikonfirmasi tenaga kesehatan.

### Konteks Deployment

- Single-facility per instance (Puskesmas, Pustu, Klinik Pratama, RS Pratama)
- Workflow encounter-driven (kunjungan dulu), AI-only
- Output bilingual (Indonesia + English)

### Status Pengembangan

| Sprint | Fokus | Status |
| --- | --- | --- |
| 1 | Project Foundation | Done (v0.1.0-sprint-1) |
| 2 | Auth & Upload | Done (2A clinical context, 2B ECG study) |
| 3 | AI Inference | Done (v0.5.0-sprint-3, 5 YOLO models) |
| 4 | HiResCAM | Done |
| 5 | Recommendation | Planned |
| 6 | History & PDF | Planned |
| 7 | Research Dashboard | Planned |
| 8 | Audit & Finalization | Planned |
| 9 | Phase 2 Preparation | Planned |

### Kontribusi

Lihat [CONTRIBUTING.md](CONTRIBUTING.md) untuk setup pengembangan, alur branch, dan konvensi commit.

### Lisensi

[MIT](LICENSE) dengan disclaimer klinis.
