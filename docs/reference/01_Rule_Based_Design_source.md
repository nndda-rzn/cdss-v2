# RULE-BASED TRIAGE SYSTEM — DESAIN FORMAL

**Studi**: Pengembangan Interpretable CDSS Berbasis Citra EKG 12-Lead untuk Skrining Myocardial Infarction
**Versi**: 1.0 (draft untuk co-design dengan Sp.JP)
**Tanggal**: 2026-05-19
**Referensi pedoman utama**:
- ESC Guidelines 2023 for the Management of Acute Coronary Syndromes
- Fourth Universal Definition of Myocardial Infarction (Thygesen et al., 2018)
- WHF Roadmap for Secondary Prevention of CVD 2023
- Konteks operasional: Pedoman Praktik Klinis (PPK) Puskesmas Indonesia, Permenkes terkait

---

## 1. Posisi Rule-Based System dalam Pipeline

```
[Citra EKG 2D]
      │
      ▼
[YOLOv8 Detector]
      │
      │ output: list of bounding boxes per class
      │   {class_code, confidence, bbox, lead_location}
      ▼
[Feature Aggregator]
      │
      │ output: per-image feature vector
      │   {n_st_anomalies, st_locations, t_inversions, ...}
      ▼
[Rule-Based Triage Engine]   ← FOKUS DOKUMEN INI
      │
      │ output: triage decision
      │   {class_4: {Normal/MI/HoMI/Abnormal},
      │    triage_level: {green/yellow/red},
      │    rule_fired: [R1, R3, ...],
      │    rationale_text}
      ▼
[Output ke User: Klinisi/Dokter Umum Puskesmas]
      │
      ├── Visual: bounding box overlay
      ├── Visual: HiResCAM heatmap
      └── Text: "Pola konsisten dengan STEMI di sadapan V1-V4. Segera rujuk."
```

**Pemisahan tugas yang jelas**:
- YOLOv8 mengerjakan **deteksi morfologi** (tugas visual, terlatih pada anotasi Sp.JP)
- Rule-based engine mengerjakan **inferensi klinis** (tugas simbolik, dirancang oleh Sp.JP)
- Pemisahan ini = transparansi penuh; setiap rule yang memicu keputusan dapat ditelusuri

---

## 2. Filosofi Desain Rule-Based

### Mengapa rule-based, bukan classifier neural network akhir?

1. **Transparansi**: setiap keputusan harus dapat dijelaskan oleh aturan eksplisit, bukan bobot tersembunyi.
2. **Auditability**: dokter dapat melihat aturan mana yang memicu rekomendasi, sehingga dapat menyangkal/menyetujui dengan dasar klinis.
3. **Adaptable**: aturan dapat diperbarui ketika pedoman klinis (ESC/AHA) berubah, tanpa perlu retraining model.
4. **Defensible**: dalam konteks medico-legal, rule-based decisions lebih mudah dipertanggungjawabkan daripada blackbox.
5. **Cocok untuk small dataset**: dengan dataset kecil (1.937 citra), model klasifikasi end-to-end berisiko overfit; rule-based dengan input dari detection lebih robust.

### Prinsip yang dianut

- **Konservatif untuk MI**: false negative MI lebih berbahaya daripada false positive. Aturan dirancang untuk *sensitif* terhadap MI, dengan toleransi false positive yang diakui.
- **Transparansi total**: setiap rekomendasi triase disertai daftar rule yang fired.
- **Sesuai pedoman**: aturan bersumber pada ESC 2023 dan Thygesen 2018; modifikasi untuk konteks operasional puskesmas didokumentasikan eksplisit.
- **Skrining, bukan diagnosis**: keluaran adalah rekomendasi triase (rujuk/observasi/normal), bukan label diagnostik definitif.

---

## 3. Input ke Rule Engine: Feature Aggregation

YOLOv8 menghasilkan list bounding box. Sebelum masuk ke rule engine, di-agregasi menjadi feature vector berikut:

| Feature | Tipe | Definisi | Sumber dari YOLO |
|---|---|---|---|
| `n_st_elev_anterior` | int | Jumlah anomali ST di lead anterior (V1-V4) | C1 + lead V1-V4 |
| `n_st_elev_inferior` | int | Jumlah anomali ST di lead inferior (II, III, aVF) | C1 + lead II/III/aVF |
| `n_st_elev_lateral` | int | Jumlah anomali ST di lead lateral (I, aVL, V5, V6) | C1 + lead I/aVL/V5/V6 |
| `n_st_elev_total` | int | Total anomali ST | sum dari atas |
| `n_t_inversions` | int | Jumlah inversi gelombang T | C2 |
| `t_inv_locations` | list | Lokasi sadapan inversi T | C2 + lead |
| `n_pathological_q` | int | Jumlah Q patologis | C3 |
| `q_locations` | list | Lokasi Q patologis | C3 + lead |
| `qrs_widening` | bool | QRS lebar terdeteksi | C3 + flag |
| `rhythm_anomaly` | enum | {none, AF, VT, SVT, brady, blok} | C4 + sub-classifier |
| `pr_prolonged` | bool | PR memanjang | C5 |
| `qt_prolonged` | bool | QT memanjang | C5 |
| `artifact_severity` | enum | {none, mild, severe} | C6 |
| `mean_yolo_confidence` | float | Rata-rata confidence YOLO untuk semua bbox | aggregated |

**Catatan implementasi**:
- Lokasi sadapan ditentukan dari posisi bounding box pada citra menggunakan template matching standar EDAN SERIES-3 layout (3×4 grid + rhythm strip).
- Sub-classifier untuk `rhythm_anomaly` dapat berupa rule sederhana berbasis R-R interval interpolasi atau model ringan tambahan.

---

## 4. Rule Set Lengkap

### 4.1 Aturan Deteksi STEMI (Triage Level: RED — RUJUK SEGERA)

**Rasional klinis**: STEMI memerlukan reperfusi <90 menit (door-to-balloon). False negative = mortalitas tinggi.

| Rule ID | Kondisi | Output Class | Triage | Sumber Pedoman |
|---|---|---|---|---|
| **R1** | `n_st_elev_anterior` ≥ 2 (di V1-V4) | MI (Anterior STEMI) | RED | ESC 2023 §6.1; Thygesen 2018 §2.2 |
| **R2** | `n_st_elev_inferior` ≥ 2 (di II, III, aVF) | MI (Inferior STEMI) | RED | ESC 2023 §6.1 |
| **R3** | `n_st_elev_lateral` ≥ 2 (di I, aVL, V5, V6) | MI (Lateral STEMI) | RED | ESC 2023 §6.1 |
| **R4** | `n_st_elev_total` ≥ 2 di sadapan kontigu manapun | MI (STEMI tidak terlokalisasi standar) | RED | ESC 2023 §6.1 (default) |

**Catatan**: "kontigu" = lead yang berdekatan secara anatomis (V1-V2-V3, II-III-aVF, dll). Ini akan diimplementasikan sebagai lookup adjacency map.

### 4.2 Aturan Deteksi NSTEMI / Iskemia (Triage Level: YELLOW — OBSERVASI 6-12 JAM)

**Rasional klinis**: NSTEMI tidak memerlukan reperfusi segera tapi tetap perlu rawat dan kerja-up troponin.

| Rule ID | Kondisi | Output Class | Triage | Sumber Pedoman |
|---|---|---|---|---|
| **R5** | `n_t_inversions` ≥ 2 di sadapan kontigu, **tanpa** ST elevasi | MI (kemungkinan NSTEMI/iskemia) | YELLOW | ESC 2023 §6.2 |
| **R6** | ST depresi ≥ 0.5 mm di ≥ 2 sadapan kontigu | MI (NSTEMI) | YELLOW | ESC 2023 §6.2 |
| **R7** | T inversion di V1-V4 + nyeri dada (info dari user input) | MI (Wellens syndrome suspect) | YELLOW + flag | Wellens 1989; ESC 2023 |

**Catatan**: R7 memerlukan input klinis dari user (apakah pasien nyeri dada). Ini akan disediakan melalui form sederhana di UI.

### 4.3 Aturan Deteksi History of MI (Triage Level: YELLOW)

**Rasional klinis**: Q patologis menetap = jaringan parut MI lampau. Bukan emergensi tapi perlu workup.

| Rule ID | Kondisi | Output Class | Triage | Sumber Pedoman |
|---|---|---|---|---|
| **R8** | `n_pathological_q` ≥ 1 di sadapan inferior **atau** anterior, **tanpa** ST elevasi/depresi | HoMI | YELLOW (referral elektif) | Thygesen 2018 §6 |
| **R9** | Q patologis + T inversion (tanpa ST anomaly) | HoMI dengan iskemia residual | YELLOW | ESC 2023 |

### 4.4 Aturan Deteksi Abnormal Heartbeat (Triage Level: YELLOW)

**Rasional klinis**: Aritmia non-MI tetap memerlukan evaluasi.

| Rule ID | Kondisi | Output Class | Triage | Sumber Pedoman |
|---|---|---|---|---|
| **R10** | `rhythm_anomaly` = AF | Abnormal Heartbeat (AF) | YELLOW | ESC AF Guidelines 2024 |
| **R11** | `rhythm_anomaly` = VT | Abnormal Heartbeat | RED (jeopardy) | ESC VT Guidelines |
| **R12** | `rhythm_anomaly` = SVT, brady, blok | Abnormal Heartbeat | YELLOW | ESC arrhythmia |
| **R13** | `qrs_widening` = true (LBBB/RBBB baru) | Abnormal Heartbeat (BBB) | YELLOW | ESC; LBBB baru → suspect MI |

### 4.5 Aturan Reject / Quality Gate

**Rasional**: Citra dengan artefak parah tidak boleh diproses lanjut.

| Rule ID | Kondisi | Output Class | Triage | Action |
|---|---|---|---|---|
| **R14** | `artifact_severity` = severe | TIDAK DAPAT DIINTERPRETASIKAN | — | Minta rekam ulang |
| **R15** | `mean_yolo_confidence` < 0.4 | TIDAK DAPAT DIINTERPRETASIKAN | — | Minta rekam ulang atau referral manual |
| **R16** | Tidak ada bbox terdeteksi sama sekali (bukan karena Normal) | UNCERTAIN | — | Manual review |

### 4.6 Aturan Default — Normal

| Rule ID | Kondisi | Output Class | Triage |
|---|---|---|---|
| **R17** | Tidak ada rule R1-R16 yang fire | Normal | GREEN |

---

## 5. Resolusi Konflik Aturan

Jika multiple rule fire, prioritas berdasarkan triage level:

```
RED > YELLOW > GREEN
```

Contoh: jika R1 (Anterior STEMI) dan R10 (AF) fire bersamaan, output:
- Class: MI
- Triage: RED
- Rule fired: [R1, R10]
- Rationale: "Pola STEMI anterior teramati. Aritmia AF juga terdeteksi sebagai temuan tambahan."

**Catatan**: aturan tidak saling overwrite—semua yang fire dilaporkan, namun decision class dan triage diambil dari level tertinggi.

---

## 6. Output Format

```python
{
    "image_id": "ECG_0042",
    "class_4": "MI",
    "triage_level": "RED",
    "rules_fired": [
        {
            "rule_id": "R1",
            "rule_text": "Anterior STEMI: ST elevasi ≥1mm di ≥2 sadapan V1-V4",
            "evidence": {
                "n_st_elev_anterior": 3,
                "lead_locations": ["V2", "V3", "V4"]
            }
        }
    ],
    "rationale_id": "Pola konsisten dengan STEMI anterior teramati di sadapan V2, V3, V4.",
    "rationale_en": "Pattern consistent with anterior STEMI observed at leads V2, V3, V4.",
    "recommended_action_id": "RUJUK SEGERA ke fasilitas dengan kemampuan PCI primer dalam <90 menit.",
    "recommended_action_en": "URGENT REFERRAL to facility with primary PCI capability within 90 minutes.",
    "confidence_yolo_avg": 0.84,
    "disclaimer": "Output ini adalah hasil skrining otomatis dan bukan pengganti diagnosis klinis. Konfirmasi dengan troponin, riwayat klinis, dan EKG serial."
}
```

---

## 7. Validasi Rule-Based System

### 7.1 Validasi terhadap Pedoman

Setiap rule (R1-R17) ditandatangani secara tertulis oleh **2 orang Sp.JP independen** sebagai konfirmasi kesesuaian dengan pedoman ESC 2023 / Thygesen 2018. Form persetujuan disertakan di Lampiran skripsi.

### 7.2 Validasi Empiris pada Dataset

- Setelah model end-to-end dijalankan pada test set, perhitungkan:
  - **Sensitivitas MI**: P(triage=RED | true label = MI)
  - **Spesifisitas Normal**: P(triage=GREEN | true label = Normal)
  - **Cohen's kappa** keluaran rule-based vs label dataset 4-kelas
  - **Cohen's kappa** keluaran rule-based vs penilaian Sp.JP independen pada subset

### 7.3 Coverage Analysis

Laporkan persentase test set yang diputuskan oleh masing-masing rule:
- Citra yang tidak ter-cover oleh rule manapun → R17 (Normal default) → audit jika persentase tidak masuk akal.
- Rule yang tidak pernah fire selama testing → review apakah threshold terlalu ketat atau memang kasus jarang di dataset.

### 7.4 Edge Cases yang Wajib Diuji

1. **STEMI silent**: kasus dengan ST elevasi minimal di hanya 1 sadapan → tidak terdeteksi R1-R4 → R17 (Normal). Risiko false negative diakui.
2. **LBBB existing**: pasien dengan LBBB lama, ST elevasi sulit dinilai. R13 fire → YELLOW (sesuai pedoman ESC: LBBB baru atau ekuivalen STEMI = perlu referral).
3. **NSTEMI dengan T-wave normal**: sebagian NSTEMI tidak menunjukkan perubahan EKG. Rule-based tidak akan tangkap; ini batasan modalitas EKG, bukan failure rule-based.
4. **Multiple anomali**: pasien dengan AF + Q patologis → R10 + R8 fire. Output: HoMI + Abnormal, triage YELLOW.

---

## 8. Co-Design Process dengan Sp.JP

**Tahap 1 — Review awal** (dilakukan setelah dokumen ini diberikan):
- Sp.JP A1 dan A2 membaca rule R1-R17 secara independen.
- Mengisi form review (Bagian 9) dengan: setuju/setuju dengan modifikasi/tidak setuju.

**Tahap 2 — Diskusi konsensus**:
- Pertemuan 1-2 jam (online OK) dengan kedua Sp.JP + arbitrator.
- Resolve perbedaan interpretasi/nilai threshold.
- Update dokumen ini → versi 2.0.

**Tahap 3 — Konteks Indonesia**:
- Sp.PD opsional: review apakah recommended_action realistis untuk fasilitas puskesmas tipe pratama (mis. apakah "PCI primer <90 menit" feasible dari puskesmas terpencil — kemungkinan tidak; perlu modifikasi ke "rujuk RS terdekat dengan ICCU").

**Tahap 4 — Sign-off**:
- Versi final ditandatangani Sp.JP A1, A2, dan arbitrator.
- Dijadikan **Lampiran 1** skripsi: "Rule-Based Triage Table — Validated by Cardiologists".

---

## 9. Form Review untuk Sp.JP (template)

Untuk setiap rule R1-R17:

```
Rule ID: R___
Kondisi: [otomatis fill]
Output yang diusulkan: [otomatis fill]

[ ] Saya setuju dengan rule ini sebagaimana tertulis
[ ] Saya setuju dengan modifikasi (sebutkan):
    _________________________________________________
[ ] Saya tidak setuju (alasan):
    _________________________________________________

Sumber pedoman tambahan yang relevan:
    _________________________________________________

Tanda tangan: _____________________
Nama:        _____________________
SIP:         _____________________
Tanggal:     _____________________
```

---

## 10. Future Work

- **Rule learning**: setelah dataset terkumpul cukup, eksplorasi induksi rule otomatis (decision tree atau RIPPER) untuk dibandingkan dengan rule manual.
- **Fuzzy rules**: untuk threshold yang ambigu (mis. ST elevasi 0.9-1.1 mm), pertimbangkan fuzzy logic alih-alih hard threshold.
- **Konteks regional**: rule untuk populasi atlet (early repolarization), pediatrik, atau lansia yang umumnya memerlukan modifikasi threshold.
