---
title: "Grand PRD CDSS EKG v3.1 - Delta Update"
version: "3.1 Delta"
status: "Deployable prototype (research-grade) untuk fasilitas kesehatan primer/terpencil"
language: "id"
base_document: "Grand_PRD_CDSS_EKG_HiResCAM_v3.md"
---

# Grand PRD v3.1 - Delta Update

Dokumen ini adalah delta (perubahan) terhadap PRD v3. PRD v3 tetap utuh sebagai baseline. Delta ini merangkum section yang berubah agar mudah dipresentasikan ke pembimbing/evaluator.

## Ringkasan Perubahan v3 -> v3.1

| Area | v3 | v3.1 |
| --- | --- | --- |
| Status produk | Research prototype | Deployable prototype (research-grade) untuk faskes primer/terpencil |
| Target deployment | Tidak spesifik | Single-facility per instance (Puskesmas/Pustu/Klinik/RS Pratama) |
| Workflow | Upload-centric | Encounter-driven, AI-only |
| Data model | 7 tabel | 22 tabel (operational CDSS schema) |
| PHI handling | Tidak dirinci | Layered strategy (T1-T5, Fernet encryption, PHIAccessLog) |
| Bilingual | id only | id + en (rationale, recommended action, error) |
| Publikasi | Skripsi | Target Scopus Q2/Q3 |

## Delta Section 1 - Identitas Dokumen

Perubahan field:
- Status Produk: "Deployable prototype research-grade untuk fasilitas kesehatan primer dan terpencil; bukan certified medical device."
- Tambah: "Deployment Model: single-facility per instance."

## Delta Section 5 - Definisi Low-Resource Settings

Tambahan: target deployment dipertegas sebagai fasilitas kesehatan primer dan terpencil di Indonesia (Puskesmas, Pustu, Klinik Pratama, RS Pratama) dengan keterbatasan Sp.JP, komputasi, internet, dan akses rujukan cepat.

Implikasi context-aware recommendation: bila PCI primer <90 menit tidak feasible, rekomendasi otomatis disesuaikan menjadi "rujuk RS terdekat dengan kapabilitas ICCU" (via SystemConfig).

## Delta Section 6 - Scope Produk

### Tambahan In Scope (Phase 1)

- Operational data model: Patient, Encounter, ClinicalContext, VitalSigns, ECGStudy.
- Encounter-driven workflow (kunjungan sebagai konteks klinis).
- PHI handling layered (encryption at rest untuk direct identifier).
- Clinical disposition + referral tracking.
- Bilingual output (id/en).
- Co-design + sign-off tracking Sp.JP (schema + workflow, aktif penuh di Phase 2).

### Tetap Out of Scope

- Sertifikasi medical device.
- Uji klinis randomized / validasi klinis eksternal penuh.
- Lab order, e-prescribing, billing, integrasi HIS/SIMRS penuh.
- Cloud/GPU server sebagai syarat wajib.

Catatan: AI-only berarti sistem hanya menangani alur skrining EKG berbasis AI dalam konteks kunjungan; output klinis = saran tindakan lanjutan dari Rule-Based System + Decision Tree, bukan manajemen klinis lengkap.

## Delta Section 13 - Functional Requirements

Tambahan FR:

| ID | Requirement | Deskripsi |
| --- | --- | --- |
| FR-18 | Patient Management | Registrasi/pencarian pasien dengan PHI encryption |
| FR-19 | Encounter Management | Buat kunjungan, chief complaint, clinical context, vital signs |
| FR-20 | Clinical Interpretation | Clinician agree/disagree + note terhadap output AI |
| FR-21 | Disposition & Referral | Keputusan tindak lanjut + surat rujukan |
| FR-22 | PHI Access Logging | Catat tiap akses ke direct identifier (UU PDP) |
| FR-23 | Bilingual Output | rationale + recommended action dalam id/en |

## Delta Section 15 - Database

Skema diganti ke 22 tabel; detail penuh di `docs/superpowers/specs/2026-05-30-data-model-and-phi-design.md`. Skema PRD v3 (7 tabel) menjadi subset.

## Delta Section 21 - Novelty

Tambahan novelty:

- Deployable operational schema untuk fasilitas kesehatan primer/terpencil (bukan hanya research prototype).
- Layered PHI protection yang kompatibel low-resource (SQLite + Litestream + field encryption).
- Context-aware recommendation untuk keterbatasan rujukan PCI di puskesmas terpencil.
- Bilingual interpretable output untuk jangkauan publikasi internasional.

## Publication Readiness (Scopus Q2/Q3)

Lihat architecture-overview-design.md Section 8. Poin utama: reproducibility (model checksum, dataset version, seed), metrik lengkap (ROC-AUC, PR-AUC, kappa, MCC, CI), McNemar's test untuk model comparison, HiResCAM faithfulness, inter-rater agreement Sp.JP, ethical clearance, dan limitations section.

## Repository Operations

Repo dikelola sebagai **private** sampai paper accepted. Praktik GitHub:

| Aspek | Keputusan |
| --- | --- |
| Branching | GitHub Flow + sprint tags (main protected) |
| Commit | Conventional Commits + commitlint |
| Versioning | Modified SemVer v0.<sprint>.<patch>, v1.0.0 di Sprint 8 |
| Release | release-please otomatis + GitHub Release per sprint |
| CI | ruff, mypy, pytest, eslint, prettier, vitest, build, gitleaks |
| ADR | 14 Architecture Decision Records (docs/adr/) |
| Lisensi | MIT + clinical disclaimer |
| License/citation | LICENSE (MIT), CITATION.cff |

Detail di `docs/operations/` dan `docs/adr/`.

## Dokumen Desain Terkait

| Dokumen | Isi |
| --- | --- |
| architecture-overview-design.md | Tech stack, repo structure, conventions, roadmap |
| data-model-and-phi-design.md | 22 tabel + PHI strategy |
| decision-engine-design.md | DT-01..DT-10 + R1-R17 + co-design |
| sprint-1-foundation-design.md | Detail Sprint 1 |
| color-system-and-tokens-design.md | Color system + design tokens |
| adr/README.md | Index 14 ADR |
| operations/ | Git workflow, commit, PR, release, branch protection, setup |
| reference/01_Rule_Based_Design_source.md | Sumber rule base original |
