# Decision Engine Design - EKG-Insight CDSS v2

| Item | Keterangan |
| --- | --- |
| Dokumen | Decision Engine Design |
| Versi | 1.0 |
| Tanggal | 2026-05-30 |
| Status | Approved design |
| Referensi | reference/01_Rule_Based_Design_source.md, Grand_PRD_CDSS_EKG_HiResCAM_v3.md |
| Pedoman klinis | ESC 2023 ACS, Thygesen 2018 (4th Universal Definition of MI), Wellens 1989 |

## 1. Filosofi Desain

Decision Engine menerjemahkan output AI menjadi risk/triage level + saran tindakan umum. Engine bersifat rule-based simbolik, bukan classifier neural network akhir.

| Prinsip | Alasan |
| --- | --- |
| Transparansi | Setiap keputusan dapat dijelaskan oleh aturan eksplisit |
| Auditability | Dokter dapat melihat rule mana yang fire, menyetujui/menyangkal dengan dasar klinis |
| Adaptable | Aturan diperbarui saat pedoman (ESC/AHA) berubah, tanpa retraining |
| Defensible | Rule-based decision lebih mudah dipertanggungjawabkan secara medico-legal |
| Konservatif MI | False negative MI lebih berbahaya daripada false positive; aturan sensitif terhadap MI |
| Screening not diagnosis | Output = rekomendasi triase, bukan label diagnostik definitif |

## 2. Dua Phase, Dua Engine

| Phase | Engine | Input | Output Level | Status |
| --- | --- | --- | --- | --- |
| Phase 1 | decision_tree_engine | Predicted class, confidence, probability, image quality, HiResCAM status, clinical input | risk_level (low/moderate/high/need-review/uncertain) | Aktif |
| Phase 2 | triage_engine | Bounding box, lead location, feature vector morfologi | triage_level (green/yellow/red) + class_4 | Dormant (butuh anotasi Sp.JP) |

Public API stabil: `recommendation.generate(ctx) -> Recommendation`. Internal memilih engine berdasarkan phase aktif.

### Arsitektur Service

```
backend/app/services/recommendation/
  __init__.py                 # public API: generate(ctx)
  orchestrator.py             # pilih engine berdasarkan phase
  result.py                   # Recommendation DTO (common)
  i18n.py                     # bilingual template loader (id/en)
  engines/
    base_engine.py            # AbstractEngine
    decision_tree_engine/     # PHASE 1 (active)
      engine.py
      context.py
      decision_path.py
      templates.py
      rules/                  # DT-01..DT-10 (one file per rule)
    triage_engine/            # PHASE 2 (dormant, schema-ready)
      engine.py
      feature_aggregator.py
      adjacency_map.py
      lead_zones.py
      rules/                  # R1..R17 (one file per rule)
```

## 3. Phase 1 - Decision Tree (DT-01..DT-10)

### Input Context

| Field | Sumber |
| --- | --- |
| predicted_class | AIAnalysis |
| confidence_score | AIAnalysis |
| probability_distribution | AIAnalysis |
| image_quality_status | ECGStudy |
| hirescam_explanation_status | HiResCAMArtifact |
| clinical_input (chest pain, dyspnea, history) | ClinicalContext |

### Risk Level

| Risk Level | Makna |
| --- | --- |
| Low | Tidak ada indikasi abnormal kuat |
| Moderate | Perlu evaluasi klinis lanjutan / manual review |
| High | Perlu tinjauan klinis segera, terutama bila gejala mendukung |
| Need Review | Hasil tidak cukup yakin / explanation tidak informatif |
| Uncertain | Input/model tidak cukup dapat diandalkan |

### Rule Table DT-01..DT-10

| Rule | Kondisi | Risk Level | Recommendation |
| --- | --- | --- | --- |
| DT-01 | Kualitas citra buruk | Uncertain | Unggah ulang atau pemeriksaan ulang |
| DT-02 | Confidence < 0.60 | Need Review | Manual review, pertimbangkan upload ulang |
| DT-03 | MI, confidence >= 0.80 | High | Tinjauan klinis segera; rujukan sesuai SOP bila gejala mendukung |
| DT-04 | MI, confidence 0.60-0.79 | Moderate to High | Evaluasi klinis lanjutan + manual review |
| DT-05 | Normal, confidence >= 0.80 | Low | Tidak ada indikasi abnormal kuat; korelasikan klinis |
| DT-06 | Normal, confidence 0.60-0.79 | Need Review | Interpretasi manual jika ada gejala |
| DT-07 | Abnormal Heartbeat, confidence >= 0.60 | Moderate | Evaluasi klinis + interpretasi manual |
| DT-08 | History of MI, confidence >= 0.60 | Moderate | Review riwayat klinis + evaluasi elektif |
| DT-09 | HiResCAM off-target/diffuse | Need Review | Visual explanation tidak informatif; tinjau manual |
| DT-10 | Gejala akut walau confidence rendah/sedang | Need Review / High | Prioritaskan evaluasi klinis manual |

### Batasan Phase 1

Tidak menggunakan bounding box, tidak menggunakan lokasi sadapan, tidak mendeteksi ST elevation/T inversion/Q patologis spesifik, tidak memberi diagnosis final, tidak memberi terapi spesifik.

### File Mapping (one file per rule)

```
rules/
  dt_01_image_quality.py
  dt_02_low_confidence.py
  dt_03_mi_high_conf.py
  dt_04_mi_mid_conf.py
  dt_05_normal_high.py
  dt_06_normal_mid.py
  dt_07_abnormal_beat.py
  dt_08_history_mi.py
  dt_09_hirescam_status.py
  dt_10_acute_symptoms.py
```

## 4. Phase 2 - Triage Engine (R1-R17)

Dormant sampai tersedia model YOLO detection + anotasi Sp.JP. Pipeline:

```
[Citra EKG 2D] -> [YOLOv8 Detector] -> bounding boxes {class_code, confidence, bbox, lead_location}
-> [Feature Aggregator] -> per-image feature vector
-> [Triage Engine R1-R17] -> {class_4, triage_level, rules_fired, rationale}
```

### Feature Vector (dari Feature Aggregator)

| Feature | Tipe | Definisi |
| --- | --- | --- |
| n_st_elev_anterior | int | Anomali ST di V1-V4 |
| n_st_elev_inferior | int | Anomali ST di II, III, aVF |
| n_st_elev_lateral | int | Anomali ST di I, aVL, V5, V6 |
| n_st_elev_total | int | Total anomali ST |
| n_t_inversions | int | Inversi gelombang T |
| t_inv_locations | list | Lokasi inversi T |
| n_pathological_q | int | Q patologis |
| q_locations | list | Lokasi Q patologis |
| qrs_widening | bool | QRS lebar |
| rhythm_anomaly | enum | none/AF/VT/SVT/brady/blok |
| pr_prolonged, qt_prolonged | bool | Interval memanjang |
| artifact_severity | enum | none/mild/severe |
| mean_yolo_confidence | float | Rata-rata confidence bbox |

Lokasi sadapan ditentukan dari posisi bbox via template matching layout EDAN SERIES-3 (3x4 grid + rhythm strip).

### Rule Set R1-R17

| Rule | Kondisi | Class | Triage | Sumber |
| --- | --- | --- | --- | --- |
| R1 | n_st_elev_anterior >= 2 (V1-V4) | MI Anterior STEMI | RED | ESC 2023; Thygesen 2018 |
| R2 | n_st_elev_inferior >= 2 (II,III,aVF) | MI Inferior STEMI | RED | ESC 2023 |
| R3 | n_st_elev_lateral >= 2 (I,aVL,V5,V6) | MI Lateral STEMI | RED | ESC 2023 |
| R4 | n_st_elev_total >= 2 sadapan kontigu | MI STEMI | RED | ESC 2023 |
| R5 | n_t_inversions >= 2 kontigu tanpa ST elevasi | MI NSTEMI/iskemia | YELLOW | ESC 2023 |
| R6 | ST depresi >= 0.5mm di >= 2 kontigu | MI NSTEMI | YELLOW | ESC 2023 |
| R7 | T inversion V1-V4 + nyeri dada | MI Wellens suspect | YELLOW+flag | Wellens 1989 |
| R8 | n_pathological_q >= 1 inferior/anterior tanpa ST | HoMI | YELLOW elektif | Thygesen 2018 |
| R9 | Q patologis + T inversion tanpa ST | HoMI iskemia residual | YELLOW | ESC 2023 |
| R10 | rhythm_anomaly = AF | Abnormal (AF) | YELLOW | ESC AF 2024 |
| R11 | rhythm_anomaly = VT | Abnormal | RED | ESC VT |
| R12 | rhythm_anomaly = SVT/brady/blok | Abnormal | YELLOW | ESC arrhythmia |
| R13 | qrs_widening (LBBB/RBBB baru) | Abnormal (BBB) | YELLOW | ESC |
| R14 | artifact_severity = severe | Tidak dapat diinterpretasi | Manual | Quality gate |
| R15 | mean_yolo_confidence < 0.4 | Tidak dapat diinterpretasi | Manual | Quality gate |
| R16 | Tidak ada bbox terdeteksi | Uncertain | Manual | Quality gate |
| R17 | Tidak ada R1-R16 fire | Normal | GREEN | Default |

### File Mapping

```
rules/
  r_01_stemi_anterior.py ... r_17_normal_default.py
```

## 5. Resolusi Konflik

Prioritas: RED > YELLOW > GREEN. Semua rule yang fire tetap dilaporkan, namun class dan triage final diambil dari level tertinggi. Aturan tidak saling overwrite.

Contoh: R1 (Anterior STEMI) + R10 (AF) fire bersamaan -> Class: MI, Triage: RED, rules_fired: [R1, R10].

## 6. Output Format (Bilingual)

```json
{
  "image_id": "ECG_0042",
  "engine_type": "triage_engine",
  "class_4": "MI",
  "triage_level": "RED",
  "rules_fired": [
    {
      "rule_id": "R1",
      "rule_text": "Anterior STEMI: ST elevasi >=1mm di >=2 sadapan V1-V4",
      "evidence": {"n_st_elev_anterior": 3, "lead_locations": ["V2","V3","V4"]}
    }
  ],
  "rationale_id": "Pola konsisten dengan STEMI anterior di sadapan V2, V3, V4.",
  "rationale_en": "Pattern consistent with anterior STEMI at leads V2, V3, V4.",
  "recommended_action_id": "RUJUK SEGERA ke fasilitas dengan PCI primer <90 menit.",
  "recommended_action_en": "URGENT REFERRAL to facility with primary PCI capability within 90 minutes.",
  "confidence_yolo_avg": 0.84,
  "disclaimer": "Output ini adalah hasil skrining otomatis dan bukan pengganti diagnosis klinis."
}
```

### Context-Aware Recommendation (Faskes Terpencil)

Recommended action menyesuaikan SystemConfig faskes:
- Jika `nearest_pci_facility_distance_minutes` <= 90: "Rujuk PCI primer"
- Jika > 90 atau tidak ada: "Rujuk RS terdekat dengan kapabilitas ICCU"

Ini mengakomodasi temuan rule base bahwa PCI primer <90 menit sering tidak feasible dari puskesmas terpencil.

## 7. Bilingual Strategy

| Komponen | Implementasi |
| --- | --- |
| DB | rationale_id/en, recommended_action_id/en di Recommendation; template_id/en di DecisionRule |
| Service | i18n.py memuat template per bahasa |
| UI | Default id, toggle ke en |
| Default | Bahasa Indonesia (sesuai PRD language: id) |

## 8. Co-Design Process dengan Sp.JP (Phase 2)

| Tahap | Aktivitas |
| --- | --- |
| 1 Review awal | 2 Sp.JP independen baca R1-R17, isi form review (agree/modify/disagree) |
| 2 Konsensus | Pertemuan 1-2 jam + arbitrator, resolve threshold |
| 3 Konteks Indonesia | Review recommended_action realistis untuk puskesmas pratama |
| 4 Sign-off | Versi final ditandatangani Sp.JP A1, A2, arbitrator -> Lampiran 1 skripsi |

Tracking via tabel ExpertReview (lihat data-model doc): reviewer_user_id, rule_id, decision, modification_note, signature_path, arbitrated_by_user_id.

### Form Review Template

```
Rule ID: R___
Kondisi: [auto-fill]
Output diusulkan: [auto-fill]
[ ] Setuju sebagaimana tertulis
[ ] Setuju dengan modifikasi: ____
[ ] Tidak setuju (alasan): ____
Sumber pedoman tambahan: ____
Tanda tangan / Nama / SIP / Tanggal
```

## 9. Validasi (Publication-Grade)

### Terhadap Pedoman
Setiap rule R1-R17 ditandatangani 2 Sp.JP independen (konfirmasi ESC 2023 / Thygesen 2018).

### Empiris pada Dataset
| Metrik | Definisi |
| --- | --- |
| Sensitivitas MI | P(triage=RED \| true=MI) |
| Spesifisitas Normal | P(triage=GREEN \| true=Normal) |
| Cohen's kappa | Rule-based vs label 4-kelas |
| Cohen's kappa | Rule-based vs penilaian Sp.JP (subset) |

### Coverage Analysis
Persentase test set diputuskan tiap rule. Rule tidak pernah fire -> review threshold. R17 default berlebihan -> audit.

### Edge Cases Wajib Diuji
1. STEMI silent (ST elevasi minimal 1 sadapan) -> risiko false negative diakui.
2. LBBB existing -> R13 fire -> YELLOW.
3. NSTEMI dengan T-wave normal -> batasan modalitas EKG.
4. Multiple anomali (AF + Q patologis) -> R10 + R8 fire.

## 10. Future Work
- Rule learning (decision tree / RIPPER induction) dibandingkan rule manual.
- Fuzzy rules untuk threshold ambigu (ST elevasi 0.9-1.1mm).
- Konteks regional (atlet early repolarization, pediatrik, lansia).
