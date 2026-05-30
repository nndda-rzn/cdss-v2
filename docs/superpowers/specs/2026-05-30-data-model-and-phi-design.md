# Data Model & PHI Design - EKG-Insight CDSS v2

| Item | Keterangan |
| --- | --- |
| Dokumen | Data Model & PHI Design |
| Versi | 1.0 |
| Tanggal | 2026-05-30 |
| Status | Approved design |
| Referensi | architecture-overview-design.md, Grand_PRD_CDSS_EKG_HiResCAM_v3.md |

## 1. Konteks Klinis

Sistem dipasang per fasilitas kesehatan primer/terpencil (single-facility per instance). Workflow bersifat encounter-driven dan AI-only:

- Encounter-driven: kunjungan pasien dibuat lebih dulu sebagai konteks klinis.
- AI-only: sistem hanya menangani alur skrining EKG berbasis AI. Tidak ada lab order, e-prescribing, billing, atau HIS lengkap. Output klinis adalah saran tindakan lanjutan dari Rule-Based System + Decision Tree.

### User Journey (Phase 1)

```
1. Nurse/Clinician login
2. Daftarkan/temukan Patient
3. Buat Encounter (kunjungan)
4. Input ClinicalContext (chief complaint, gejala) + VitalSigns
5. Upload citra EKG -> ECGStudy
6. Sistem validasi file + image quality check
7. AI Analysis (3 model YOLO) -> predicted class + confidence + probabilities
8. HiResCAM -> heatmap + overlay + explanation status
9. Decision Tree -> risk level + recommendation (id/en) + rationale + decision path
10. Clinician review -> ClinicalInterpretation (agree/disagree + note)
11. Disposition (pulang/observasi/rujuk) -> Referral jika perlu
12. Audit trail + PDF report
```

## 2. Domain Model (ERD Tekstual)

```
HealthcareFacility (1) -< User (M)
HealthcareFacility (1) -< Patient (M)

Patient (1) -< Encounter (M)
Patient (1) -< PatientHistory (M)
Patient (1) -< Consent (M)

Encounter (1) -- ClinicalContext (1)
Encounter (1) -< VitalSigns (M)
Encounter (1) -< ECGStudy (M)
Encounter (1) -- Disposition (1)

ECGStudy (1) -< AIAnalysis (M)        # 1 study, N model
ECGStudy (1) -< ClinicalInterpretation (M)

AIAnalysis (1) -- HiResCAMArtifact (1)
AIAnalysis (1) -- Recommendation (1)
Recommendation (1) -- DecisionPath (1)

Disposition (1) -- Referral (0..1)

ModelMetadata (1) -< AIAnalysis (M)
DecisionRule (referensi rule katalog)

# Audit & config (global)
AuditLog, PHIAccessLog, SystemConfig

# Phase 2 (dormant)
ExpertReview, DetectionResult
```

## 3. PHI Tier Classification

| Tier | Field | Treatment |
| --- | --- | --- |
| T1 Direct identifier | name, phone, address, NIK full, photo | Encrypted at rest (Fernet), decrypt on demand, masked di UI |
| T2 Quasi-identifier | DOB, gender, MRN, NIK last-4 | Plaintext + RBAC + access log, boleh index/search |
| T3 Hash-only | NIK full untuk dedup | HMAC-SHA256, tidak reversible |
| T4 Clinical context | vital signs, symptoms, diagnosis impression | Plaintext (anonim by itself) |
| T5 System metadata | timestamps, IDs, audit | Plaintext |

## 4. Tabel Specification (22 Tabel)

### 4.1 Identity Domain

**HealthcareFacility** (1 row seeded saat install)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| code | str | Kode faskes BPJS (opsional) |
| name | str | Nama faskes |
| type | enum | puskesmas / pustu / klinik / rs_pratama |
| address | str | |
| province_code, regency_code, subdistrict_code | str | Wilayah |
| is_active | bool | |
| created_at | datetime | |

**User**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| name | str | |
| email | str unique | Login |
| password_hash | str | bcrypt |
| role | enum | admin/clinician/nurse/researcher/expert_reviewer |
| facility_id | int FK | |
| profession | str | dokter umum/perawat/sp.jp/peneliti |
| license_number | str | SIP/STR (opsional) |
| is_active | bool | |
| created_at, updated_at | datetime | |

### 4.2 Patient Domain

**Patient**
| Field | Tipe | Tier | Catatan |
| --- | --- | --- | --- |
| id | uuid PK | T5 | Internal ID |
| mrn | str | T2 | Medical record number per faskes |
| nik_hash | str unique idx | T3 | HMAC-SHA256 NIK |
| nik_last4 | str | T2 | 4 digit terakhir (display) |
| name_encrypted | bytes | T1 | Fernet |
| dob | date | T2 | |
| gender | enum | T2 | male/female |
| phone_encrypted | bytes | T1 | Fernet |
| address_encrypted | bytes | T1 | Fernet |
| facility_id | int FK | T5 | |
| is_pseudonymized | bool | T5 | Research/demo mode |
| created_at, updated_at, deleted_at | datetime | T5 | Soft delete (retention) |

**PatientHistory**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| patient_id | uuid FK | |
| condition_code | enum | MI/DM/HT/CKD/dyslipidemia/smoker/other |
| onset_date_approx | date | |
| note_encrypted | bytes | T1 |
| recorded_by | int FK User | |
| recorded_at | datetime | |

**Consent**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| patient_id | uuid FK | |
| consent_type | enum | data_use/research/ai_analysis |
| status | enum | given/revoked/pending |
| given_at, revoked_at | datetime | |
| evidence_path | str | Scan tanda tangan |
| recorded_by | int FK User | |

### 4.3 Encounter Domain

**Encounter**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| patient_id | uuid FK | |
| facility_id | int FK | |
| attending_user_id | int FK User | |
| encounter_type | enum | rawat_jalan/igd |
| status | enum | open/closed |
| chief_complaint | text | T4 |
| started_at, ended_at | datetime | |

**ClinicalContext** (1:1 ke Encounter)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| encounter_id | int FK | |
| symptom_chest_pain | bool | Untuk DT-10 + R7 |
| symptom_dyspnea | bool | |
| symptom_palpitation | bool | |
| symptom_syncope | bool | |
| symptom_other | text | |
| pain_onset_minutes | int | |
| pain_duration_minutes | int | |
| recorded_by | int FK User | |
| recorded_at | datetime | |

**VitalSigns** (M ke Encounter)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| encounter_id | int FK | |
| measured_at | datetime | |
| bp_systolic, bp_diastolic | int | |
| heart_rate, respiratory_rate | int | |
| spo2 | int | |
| temperature | float | |
| weight, height | float | |
| recorded_by | int FK User | |

### 4.4 ECG & AI Domain

**ECGStudy**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| encounter_id | int FK | |
| patient_id | uuid FK | Redundant untuk query |
| study_uid | str unique | DICOM-like UID |
| image_original_path | str | |
| image_processed_path | str | |
| image_quality_status | enum | good/acceptable/poor |
| image_quality_score | float | |
| image_quality_metrics_json | json | blur/noise/brightness/contrast |
| acquired_at | datetime | |
| recorded_by | int FK User | |
| device_info | str | Opsional |

**AIAnalysis** (1 study, N model)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| ecg_study_id | int FK | |
| model_metadata_id | int FK | |
| predicted_class | enum | normal/mi/homi/abnormal |
| confidence_score | float | |
| probability_json | json | Per-class probability |
| inference_time_ms | int | |
| device_used | enum | cpu/gpu |
| inference_started_at, inference_finished_at | datetime | |
| status | enum | success/failed/skipped |

**HiResCAMArtifact** (1:1 ke AIAnalysis)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| ai_analysis_id | int FK | |
| heatmap_path, overlay_path, side_by_side_path | str | |
| explanation_status | enum | good/diffuse/off-target/low-confidence/need-review |
| focus_metric | float | |
| colormap_used | str | |
| generated_at | datetime | |

### 4.5 Decision Domain

**Recommendation** (1:1 ke AIAnalysis)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| ai_analysis_id | int FK | |
| engine_type | enum | decision_tree / triage_engine |
| engine_version | str | DT-v1.0 / R1-R17-v2.0 |
| risk_level | enum nullable | low/moderate/high/need-review/uncertain (Phase 1) |
| triage_level | enum nullable | green/yellow/red (Phase 2) |
| class_4 | enum nullable | normal/mi/homi/abnormal (Phase 2) |
| rationale_id | text | Bahasa Indonesia |
| rationale_en | text | English |
| recommended_action_id | text | |
| recommended_action_en | text | |
| disclaimer_text | text | |
| rules_fired_json | json | Daftar rule + evidence |
| generated_at | datetime | |

**DecisionPath** (1:1 ke Recommendation)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| recommendation_id | int FK | |
| path_json | json | Rules evaluated + branches taken |

**ClinicalInterpretation**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| ecg_study_id | int FK | |
| ai_analysis_id | int FK nullable | |
| clinician_user_id | int FK | |
| agreement_status | enum | agree/disagree/partial |
| clinician_diagnosis_impression | text | T4 |
| note_text_encrypted | bytes | T1 |
| validation_status | enum | validated/needs-review |
| interpreted_at | datetime | |

### 4.6 Disposition Domain

**Disposition** (1:1 ke Encounter)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| encounter_id | int FK | |
| decision | enum | pulang/observasi_24h/rujuk_sp_jp/rujuk_igd_rs/rawat_inap |
| decided_by_user_id | int FK | |
| decided_at | datetime | |
| note_text_encrypted | bytes | T1 |

**Referral** (1:1 ke Disposition, opsional)
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| disposition_id | int FK | |
| referred_to_facility_id | int FK nullable | |
| referred_specialty | enum | jantung/penyakit_dalam/igd |
| urgency | enum | segera/elektif |
| letter_path | str | |
| created_at | datetime | |

### 4.7 Audit Domain

**AuditLog**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| user_id | int FK nullable | |
| facility_id | int FK | |
| action | str | login/upload/inference/export/... |
| entity_type, entity_id | str/int | |
| description | text | |
| ip_address, user_agent | str | |
| request_id | str | Correlation ID |
| created_at | datetime | |

**PHIAccessLog**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| user_id | int FK | |
| patient_id | uuid FK | |
| access_type | enum | view/edit/export |
| purpose | enum | treatment/research/audit |
| accessed_field | str | nama/nik/alamat/kontak |
| ip_address | str | |
| accessed_at | datetime | |

### 4.8 Config Domain

**ModelMetadata**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| model_name | str | yolov8n-cls/yolov11n-cls/yolov26n-cls |
| model_version | str | |
| architecture | str | |
| task_type | enum | classification/detection |
| dataset_version | str | |
| input_size | int | |
| model_file_path | str | |
| model_checksum | str | SHA256 untuk reproducibility |
| threshold_config_json | json | |
| model_size_mb | float | |
| is_active | bool | |
| training_date | date | |

**DecisionRule**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| rule_code | str | DT-01.../R1... |
| phase | enum | phase_1/phase_2 |
| condition_json | json | |
| output_risk_level | str | |
| output_triage_level | str | |
| recommendation_template_id, recommendation_template_en | text | |
| rationale_template_id, rationale_template_en | text | |
| guideline_reference | str | ESC 2023/Thygesen 2018 |
| version | str | |
| is_active | bool | |

**SystemConfig**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| key | str unique | |
| value_json | json | |
| updated_by | int FK | |
| updated_at | datetime | |

Contoh key: `default_model_id`, `confidence_threshold_override`, `enable_clinical_mode`, `nearest_pci_facility_distance_minutes`, `available_referral_destinations`.

### 4.9 Phase 2 Domain (Dormant)

**ExpertReview**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| reviewer_user_id | int FK | Sp.JP |
| rule_id | int FK | |
| rule_version | str | |
| decision | enum | agree/agree_with_modification/disagree |
| modification_note | text | |
| alternative_guideline_ref | str | |
| arbitrated_by_user_id | int FK nullable | Arbitrator |
| signature_path | str | Scan/digital signature |
| reviewed_at | datetime | |

**DetectionResult**
| Field | Tipe | Catatan |
| --- | --- | --- |
| id | int PK | |
| ecg_study_id | int FK | |
| bbox_x, bbox_y, bbox_width, bbox_height | float | |
| class_code | str | C1..C6 |
| confidence | float | |
| lead_location | str | V1-V6/I/II/III/aVR/aVL/aVF |
| created_at | datetime | |

## 5. PHI Encryption Strategy (5 Layer)

| Layer | Mekanisme |
| --- | --- |
| L1 Field tiering | Klasifikasi T1-T5 (lihat Section 3) |
| L2 Encryption | T1 = Fernet (AES-128-CBC + HMAC); T3 = HMAC-SHA256. Via SQLAlchemy TypeDecorator (EncryptedString, HashedString) |
| L3 Access control | RBAC + PHIAccessLog tiap dekripsi T1; UI masking default; JWT expiry 30m |
| L4 Research export | Endpoint export tanpa T1/T3 (hanya T4/T5 + dummy patient_id) |
| L5 OS hardening | BitLocker/LUKS recommended (runbook), backup terenkripsi |

### Custom SQLAlchemy Types

```
backend/app/db/types/
  encrypted_string.py    # TypeDecorator: encrypt on write, decrypt on read
  hashed_string.py       # TypeDecorator: HMAC on write, no read-back
```

Penggunaan:
```python
name_encrypted: Mapped[str] = mapped_column(EncryptedString)
nik_hash: Mapped[str] = mapped_column(HashedString, unique=True, index=True)
```

## 6. Key Management Lifecycle

| Tahap | Aksi |
| --- | --- |
| First-run setup | `scripts/init_secrets.py` generate master key -> `secrets/master.key` (mode 0600) |
| Storage | File terpisah, NEVER commit ke git, NEVER masuk DB |
| Loading | `core/encryption/key_loader.py` load dari env var atau file |
| Rotation | Re-encrypt batch script offline; backup key lama untuk dekripsi data lama |
| Backup | Master key di-backup TERPISAH dari DB backup |
| Compromise | Rotate key -> re-encrypt -> ganti backup |

Dependensi: hanya `cryptography` (pure Python, ~5MB). Tidak butuh HSM/crypto server eksternal.

## 7. RBAC Matrix

| Resource / Aksi | admin | clinician | nurse | researcher | expert_reviewer |
| --- | --- | --- | --- | --- | --- |
| User management | CRUD | - | - | - | - |
| Model management | CRUD | R | - | R | - |
| System config | CRUD | - | - | - | - |
| Patient register/edit | RU | CRU | CRU | - | - |
| Encounter create | C | C | C | - | - |
| VitalSigns/ClinicalContext | - | CRU | CRU | - | - |
| Upload EKG / AI analysis | - | C | C | - | - |
| View result + HiResCAM | R | R | R | R (anonim) | R |
| ClinicalInterpretation | - | CRU | - | - | R |
| Disposition + Referral | - | CRU | - | - | - |
| Research dashboard | R | R | - | R | - |
| Research export (anonim) | R | - | - | R | - |
| Expert review (Phase 2) | R | - | - | - | CRU |
| Audit log | R | - | - | R | - |
| PHI full reveal | R+log | R+log | R+log | - | - |

C=Create, R=Read, U=Update, D=Delete.

## 8. Migration Strategy per Sprint

| Sprint | Tabel Migrasi |
| --- | --- |
| 1 | HealthcareFacility, User, AuditLog, PHIAccessLog, SystemConfig |
| 2 | Patient, PatientHistory, Consent, Encounter, ClinicalContext, VitalSigns, ECGStudy |
| 3 | ModelMetadata, AIAnalysis |
| 4 | HiResCAMArtifact |
| 5 | Recommendation, DecisionPath, DecisionRule, ClinicalInterpretation, Disposition, Referral |
| 9 | ExpertReview, DetectionResult |

Alembic additive migration; tiap sprint menambah tabel saat benar-benar diimplementasikan. Foreign key constraint diaktifkan via SQLite pragma (`PRAGMA foreign_keys=ON`). Soft delete (`deleted_at`) untuk entitas dengan retention requirement (Patient).
