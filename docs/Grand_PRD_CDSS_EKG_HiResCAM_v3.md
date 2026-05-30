---
title: "Grand PRD EKG-Insight CDSS v3"
version: "3.0 Final Draft"
status: "Research Prototype - bukan diagnosis final"
product: "EKG-Insight CDSS"
focus: "YOLO Classification, HiResCAM, Decision Tree, Low-Resource Readiness"
language: "id"
---

Grand Product Requirements Document v3

# Interpretable Clinical Decision Support System Berbasis Citra EKG 12-Lead

## Menggunakan YOLOv8n-cls, YOLOv11n-cls, YOLOv26n-cls, HiResCAM, dan Decision Tree Rule-Based Recommendation untuk Skrining Myocardial Infarction pada Low-Resource Settings

**Produk**  
EKG-Insight CDSS

**Status**  
Research Prototype - bukan diagnosis final

**Fokus**  
YOLO Classification, HiResCAM, Decision Tree, Low-Resource Readiness

**Versi**  
3.0 Final Draft

# Document Control

| Item | Keterangan |
| --- | --- |
| Judul Dokumen | Grand PRD EKG-Insight CDSS v3 |
| Produk | Interpretable CDSS Berbasis Citra EKG 12-Lead |
| Tujuan | Dokumen induk kebutuhan produk, arsitektur, evaluasi, safety, dan roadmap penelitian. |
| Penggunaan | Proposal/skripsi, pengembangan prototype, dokumentasi riset, dan bahan diskusi dengan pembimbing/evaluator. |

# Daftar Isi

- [1. Identitas Dokumen](#sec-identitas)
- [2. Ringkasan Eksekutif](#sec-eksekutif)
- [3. Latar Belakang dan Problem Statement](#sec-latar)
- [4. Tujuan Produk dan Prinsip Desain](#sec-tujuan)
- [5. Definisi Operasional Low-Resource Settings](#sec-lowresource)
- [6. Scope Produk dan Strategi Pengembangan](#sec-scope)
- [7. Target Pengguna dan User Journey](#sec-users)
- [8. Arsitektur Sistem](#sec-arsitektur)
- [9. Model AI Requirement](#sec-model)
- [10. HiResCAM Explainability Requirement](#sec-hirescam)
- [11. Decision Tree Rule-Based Recommendation Phase 1](#sec-dt)
- [12. Rule-Based Triage Engine Phase 2](#sec-rulephase2)
- [13. Functional Requirements](#sec-fr)
- [14. Non-Functional Requirements](#sec-nfr)
- [15. Database dan API Requirement](#sec-dbapi)
- [16. UI/UX Requirement](#sec-ui)
- [17. Evaluation Protocol](#sec-eval)
- [18. Clinical Safety Requirement](#sec-safety)
- [19. Acceptance Criteria](#sec-acceptance)
- [20. Risk Register dan Roadmap Development](#sec-riskroadmap)
- [21. Novelty, Batasan, dan Deliverables](#sec-novelty)
- [22. Kesimpulan](#sec-kesimpulan)

Catatan: nomor halaman otomatis bergantung pada renderer PDF. Struktur section digunakan sebagai navigasi utama dokumen.

# 1. Identitas Dokumen

| Elemen | Keterangan |
| --- | --- |
| Nama Produk | **EKG-Insight CDSS** |
| Jenis Produk | Research Prototype / Clinical Decision Support System |
| Domain | Informatika Kesehatan, Computer Vision, Explainable AI, Clinical Decision Support System |
| Fokus Penelitian | Pengembangan CDSS berbasis citra EKG 12-lead menggunakan YOLO classification, HiResCAM, dan Decision Tree Rule-Based Recommendation untuk membantu skrining awal Myocardial Infarction dan abnormalitas EKG lain pada low-resource settings. |
| Status Produk | Prototype penelitian, bukan medical device produksi. |
| Tahap Pengembangan Saat Ini | Phase 1 - Classification-Based CDSS |
| Tahap Lanjutan | Phase 2 - Detection-Based CDSS setelah anotasi dokter spesialis jantung tersedia. |
| Target Pengguna | Dokter umum, tenaga kesehatan primer, peneliti, admin sistem, evaluator klinis, dan dokter spesialis jantung sebagai reviewer. |
| Versi Dokumen | 3.0 |

### Revision History

| Versi | Perubahan Utama | Status |
| --- | --- | --- |
| 1.0 | Grand PRD awal CDSS EKG dengan HiResCAM dan Decision Tree. | Draft |
| 2.0 | Penambahan scope Phase 1 classification dan Phase 2 detection. | Revised |
| 3.0 | Penulisan ulang profesional, integrasi low-resource readiness, API, database, safety, evaluasi, dan roadmap. | Final Draft |

# 2. Ringkasan Eksekutif

EKG-Insight CDSS adalah prototype sistem pendukung keputusan klinis berbasis web yang dirancang untuk membantu skrining awal abnormalitas pada citra EKG 12-lead. Sistem ini menggunakan model YOLO berbasis klasifikasi, yaitu **YOLOv8n-cls**, **YOLOv11n-cls**, dan **YOLOv26n-cls**, untuk mengklasifikasikan citra EKG ke dalam beberapa kelas seperti Normal, Myocardial Infarction, History of Myocardial Infarction, dan Abnormal Heartbeat.

Untuk meningkatkan interpretabilitas, sistem menggunakan **HiResCAM** sebagai visual explanation. HiResCAM menampilkan area visual pada citra EKG yang berkontribusi terhadap prediksi model. Dengan demikian, pengguna tidak hanya menerima label prediksi, tetapi juga mendapatkan penjelasan visual yang dapat ditinjau.

Sistem juga memiliki **Decision Tree Rule-Based Recommendation Layer**. Lapisan ini mengubah output model AI, confidence score, status kualitas citra, dan status HiResCAM menjadi saran tindakan lanjutan secara umum. Saran tersebut tidak bersifat diagnosis final, tidak memberikan terapi, dan tidak menggantikan keputusan dokter.

**Prinsip safety utama:** sistem ini menghasilkan skrining awal dan saran umum. Sistem tidak boleh digunakan sebagai diagnosis final, tidak memberi resep obat, dan tidak menggantikan validasi tenaga kesehatan.

Sistem dirancang untuk **low-resource settings**, yaitu lingkungan layanan kesehatan dengan keterbatasan dokter spesialis, perangkat komputasi, konektivitas internet, biaya operasional, dan kualitas input citra. Karena itu, sistem harus ringan, dapat berjalan secara lokal, tidak wajib bergantung pada cloud, dapat digunakan pada perangkat CPU-only, serta memiliki UI sederhana yang dapat digunakan oleh tenaga kesehatan primer.

# 3. Latar Belakang dan Problem Statement

EKG 12-lead merupakan pemeriksaan penting dalam skrining penyakit jantung, terutama Myocardial Infarction. Namun, interpretasi EKG membutuhkan keahlian klinis yang tidak selalu tersedia di fasilitas kesehatan primer atau daerah dengan sumber daya terbatas. Pada banyak kondisi, tenaga kesehatan primer perlu mengambil keputusan awal berdasarkan hasil EKG, gejala pasien, dan ketersediaan rujukan.

Model deep learning dapat membantu membaca pola visual pada citra EKG. Namun, model AI yang hanya menghasilkan label prediksi memiliki kelemahan karena sulit dijelaskan, sulit diaudit, dan berisiko menimbulkan overtrust. Dalam konteks medis, sistem AI harus dirancang sebagai alat bantu, bukan pengganti keputusan klinis.

### Masalah Utama

1. Interpretasi EKG membutuhkan keahlian klinis yang tidak selalu tersedia di fasilitas kesehatan primer.
2. Model AI berbasis citra EKG sering hanya memberikan label prediksi tanpa penjelasan visual.
3. Sistem yang tidak explainable sulit dipercaya dan sulit dievaluasi secara klinis.
4. Output model AI perlu diterjemahkan menjadi saran tindakan umum yang aman dan mudah dipahami.
5. Lingkungan low-resource memiliki keterbatasan komputasi, internet, biaya, dan akses dokter spesialis.
6. Model deteksi morfologi EKG membutuhkan anotasi dokter spesialis, sehingga perlu strategi pengembangan bertahap.
7. Sistem CDSS harus memiliki batasan jelas agar tidak memberikan diagnosis final atau terapi spesifik.

### Komponen Solusi

| Komponen | Fungsi | Status |
| --- | --- | --- |
| YOLO Classification | Mengklasifikasikan citra EKG 12-lead. | Phase 1 |
| HiResCAM | Memberikan visual explanation untuk prediksi model. | Phase 1 |
| Decision Tree | Menghasilkan risk level dan saran tindakan umum. | Phase 1 |
| YOLO Detection | Mendeteksi fitur morfologi EKG berbasis bounding box. | Phase 2 |
| Rule-Based Triage R1-R17 | Menghasilkan triage berbasis evidence morfologi dan lead location. | Phase 2 |

# 4. Tujuan Produk dan Prinsip Desain

### Tujuan Utama

Mengembangkan prototype CDSS berbasis web untuk membantu skrining awal abnormalitas citra EKG 12-lead menggunakan YOLO classification, HiResCAM, dan Decision Tree Rule-Based Recommendation pada low-resource settings.

### Tujuan Khusus

1. Menyediakan sistem upload dan analisis citra EKG 12-lead.
2. Mengintegrasikan model YOLOv8n-cls, YOLOv11n-cls, dan YOLOv26n-cls.
3. Membandingkan performa model berdasarkan accuracy, precision, recall, F1-score, inference time, dan model size.
4. Menghasilkan visual explanation menggunakan HiResCAM.
5. Menghasilkan risk level dan saran tindakan umum menggunakan Decision Tree.
6. Menyediakan audit trail, metadata model, dan dashboard evaluasi.
7. Mengukur kesiapan sistem untuk low-resource settings.
8. Menyiapkan arsitektur Phase 2 untuk detection-based CDSS setelah anotasi Sp.JP tersedia.

### Prinsip Produk

| Prinsip | Implikasi Desain |
| --- | --- |
| Human-in-the-loop | Semua hasil AI harus ditinjau oleh pengguna klinis. |
| Screening, not diagnosis | Sistem hanya membantu skrining awal, bukan diagnosis final. |
| General recommendation only | Sistem hanya memberikan saran umum, bukan terapi, resep, atau keputusan klinis definitif. |
| Explainability-first | Setiap hasil prediksi disertai HiResCAM. |
| Low-resource readiness | Sistem ringan, lokal-capable, CPU-friendly, dan tidak wajib cloud. |
| Auditability | Model version, confidence, heatmap, decision path, dan audit log harus disimpan. |
| Phased development | Phase 1 classification, Phase 2 detection setelah anotasi pakar. |

# 5. Definisi Operasional Low-Resource Settings

Dalam penelitian ini, **low-resource settings** didefinisikan sebagai lingkungan layanan kesehatan primer atau semi-primer yang memiliki keterbatasan pada akses dokter spesialis jantung, perangkat komputasi, koneksi internet, biaya operasional, kualitas input citra EKG, fasilitas pemeriksaan lanjutan, akses rujukan cepat, dan waktu tenaga kesehatan.

### Parameter Low-Resource

| Dimensi | Parameter | Implikasi Sistem |
| --- | --- | --- |
| Klinis | Tidak selalu tersedia Sp.JP | Output harus mudah dipahami dokter umum. |
| Komputasi | Perangkat terbatas | Sistem harus dapat berjalan CPU-only. |
| Model | Model harus ringan | Menggunakan YOLOv8n-cls, YOLOv11n-cls, YOLOv26n-cls. |
| Koneksi | Internet tidak stabil | Inferensi lokal harus memungkinkan. |
| Biaya | Biaya operasional terbatas | Tidak wajib cloud/GPU server. |
| Input | Citra EKG bervariasi | Perlu image quality check. |
| Usability | Pengguna sibuk | Alur upload sampai hasil harus singkat. |
| Safety | Risiko overtrust AI | Disclaimer dan manual review wajib. |
| Auditability | Perlu transparansi | Simpan model version, confidence, HiResCAM, decision path. |

### Target Low-Resource

CPU

CPU-only inference harus memungkinkan.

Offline

Internet tidak wajib saat inferensi lokal.

8 GB

Target minimum RAM untuk prototype.

15s

Target maksimal inference CPU per citra.

10s

Target maksimal generate HiResCAM/PDF.

3-5

Langkah dari upload sampai hasil.

### Low-Resource Readiness Score

| Parameter | Skor Maksimal |
| --- | --- |
| CPU-only inference feasible | 2 |
| Tidak wajib internet saat inferensi | 2 |
| Model ringan | 2 |
| UI sederhana | 2 |
| Input JPG/JPEG/PNG | 2 |
| HiResCAM tersedia | 2 |
| Decision Tree recommendation tersedia | 2 |
| Tidak memberi diagnosis final | 2 |
| Image quality check tersedia | 2 |
| Audit trail tersedia | 2 |
| Export laporan tersedia | 2 |
| Local deployment memungkinkan | 2 |
| Total | 24 |

| Total Skor | Kategori |
| --- | --- |
| 0-8 | Tidak siap low-resource |
| 9-16 | Cukup siap, perlu optimasi |
| 17-24 | Siap sebagai prototype low-resource |

# 6. Scope Produk dan Strategi Pengembangan

### In Scope - Phase 1 Classification-Based CDSS

1. Login dan role-based access.
2. Upload citra EKG 12-lead.
3. Validasi file dan image quality check.
4. Preprocessing citra.
5. Klasifikasi menggunakan YOLOv8n-cls, YOLOv11n-cls, dan YOLOv26n-cls.
6. Output predicted class, confidence score, dan class probability.
7. Generate HiResCAM dan overlay.
8. Decision Tree Recommendation.
9. Risk level dan general follow-up recommendation.
10. Manual review note.
11. Riwayat pemeriksaan.
12. Export laporan PDF.
13. Dashboard evaluasi model.
14. Model comparison.
15. Audit trail.
16. Low-resource readiness evaluation.

### In Scope - Phase 2 Detection-Based CDSS

1. Dataset detection berbasis bounding box.
2. Training YOLO detection model.
3. Deteksi fitur morfologi EKG.
4. Bounding box abnormalitas.
5. Lead location mapping.
6. Feature Aggregator.
7. Rule-Based Triage Engine R1-R17.
8. Output rules fired, evidence, dan rationale.
9. Validasi rule oleh Sp.JP.
10. Perbandingan classification-based dan detection-based CDSS.

### Out of Scope

1. Diagnosis final otomatis.
2. Terapi atau resep obat.
3. Keputusan tindakan klinis definitif.
4. Integrasi langsung dengan alat EKG real-time.
5. Integrasi penuh dengan SIMRS/HIS produksi.
6. Sertifikasi medical device.
7. Deployment klinis resmi.
8. Monitoring pasien real-time.
9. Analisis sinyal EKG mentah.
10. Cloud server atau GPU server sebagai syarat wajib.

# 7. Target Pengguna dan User Journey

### Target Pengguna

| Pengguna | Kebutuhan | Ekspektasi Sistem |
| --- | --- | --- |
| Dokter umum / tenaga kesehatan primer | Bantuan skrining awal EKG. | Output ringkas, mudah dipahami, dan aman. |
| Peneliti | Evaluasi model, XAI, rule, dan low-resource readiness. | Dashboard evaluasi, metadata, dan audit trail. |
| Sp.JP / expert reviewer | Validasi rule dan kelayakan output. | Evidence, rationale, rule fired, dan form review. |
| Admin sistem | Pengelolaan pengguna, model, dan data. | Kontrol role, model, audit log, dan penyimpanan. |

### User Journey - Analisis EKG

1. Pengguna login.
2. Pengguna membuka halaman analisis EKG.
3. Pengguna mengunggah citra EKG.
4. Sistem memvalidasi file dan kualitas citra.
5. Sistem melakukan preprocessing.
6. Sistem menjalankan model YOLO classification.
7. Sistem menghasilkan predicted class dan confidence score.
8. Sistem menghasilkan HiResCAM.
9. Decision Tree menghasilkan risk level dan recommendation.
10. Pengguna meninjau hasil dan menambahkan catatan manual.
11. Sistem menyimpan hasil, audit trail, dan laporan PDF.

### User Journey - Evaluasi Model

1. Peneliti memilih model.
2. Peneliti menjalankan evaluasi.
3. Sistem menghitung metrik model.
4. Sistem menampilkan confusion matrix dan model comparison.
5. Sistem menampilkan hasil HiResCAM.
6. Peneliti melakukan error analysis dan mengekspor hasil.

# 8. Arsitektur Sistem

### Arsitektur Phase 1

Phase 1 - Classification-Based CDSS
Citra EKG 12-Lead
-> Upload & File Validation
-> Image Quality Check
-> Preprocessing
-> YOLOv8n-cls / YOLOv11n-cls / YOLOv26n-cls
-> Predicted Class + Confidence Score
-> HiResCAM Visual Explanation
-> Decision Tree Rule-Based Recommendation
-> Risk Level + General Follow-Up Recommendation
-> Manual Review + Audit Trail + PDF Report

### Arsitektur Phase 2

Phase 2 - Detection-Based CDSS
Citra EKG 12-Lead
-> YOLO Detection Model
-> Bounding Box + Class Code + Confidence
-> Lead Location Mapping
-> Feature Aggregator
-> Rule-Based Triage Engine R1-R17
-> Rules Fired + Evidence + Rationale
-> Clinician Review + Audit Trail

### Komponen Sistem

| Komponen | Tanggung Jawab |
| --- | --- |
| Frontend Web | Login, upload EKG, result visualization, HiResCAM viewer, history, research dashboard, PDF export. |
| Backend API | Authentication, authorization, examination management, model management, report generation, audit logging. |
| AI Inference Service | Load model, preprocessing, classification inference, HiResCAM generation, output formatting. |
| Decision Tree Service | Rule execution, risk level generation, recommendation generation, decision path trace. |
| Database | User, examination, model metadata, decision rule, evaluation result, audit log. |
| File Storage | Original image, processed image, heatmap, overlay, PDF report. |

# 9. Model AI Requirement

### Model yang Digunakan

| Model | Task | Peran | Status |
| --- | --- | --- | --- |
| YOLOv8n-cls | Image classification | Baseline model ringan. | Phase 1 |
| YOLOv11n-cls | Image classification | Model pembanding generasi lebih baru. | Phase 1 |
| YOLOv26n-cls | Image classification | Model pembanding terbaru sesuai eksperimen. | Phase 1 |
| YOLO Detection | Object detection | Deteksi morfologi EKG berbasis bounding box. | Phase 2 |

### Kelas Target Awal

1. Normal.
2. Myocardial Infarction.
3. History of Myocardial Infarction.
4. Abnormal Heartbeat.

### Output Model

1. Predicted class.
2. Confidence score.
3. Probability per class.
4. Model name dan model version.
5. Input size.
6. Inference time.
7. Device used.
8. Timestamp.
9. Preprocessing configuration.

### Kriteria Pemilihan Model Terbaik

| Aspek | Metrik |
| --- | --- |
| Akurasi klasifikasi | Accuracy, precision, recall, F1-score, macro F1-score. |
| Kelas kritis | Recall kelas Myocardial Infarction dan false negative analysis. |
| Efisiensi | Model size, CPU inference time, GPU inference time, RAM usage. |
| Explainability | Stabilitas dan relevansi HiResCAM. |
| Low-resource | Kemampuan berjalan lokal, CPU-only, dan tanpa cloud. |

# 10. HiResCAM Explainability Requirement

### Tujuan HiResCAM

HiResCAM digunakan untuk memberikan visual explanation terhadap prediksi model. Modul ini membantu pengguna melihat area visual pada citra EKG yang memengaruhi prediksi.

### Output HiResCAM

1. Original image.
2. Heatmap.
3. Overlay heatmap.
4. Side-by-side comparison.
5. Explanation status.
6. Confidence score.

### Explanation Status

| Status | Keterangan | Implikasi |
| --- | --- | --- |
| Good | Heatmap relatif fokus pada area sinyal EKG. | Dapat ditampilkan sebagai explanation utama. |
| Diffuse | Heatmap terlalu menyebar. | Perlu manual review. |
| Off-target | Heatmap muncul pada area non-sinyal. | Perlu warning dan manual review. |
| Low-confidence | Confidence model rendah. | Jangan jadikan output sebagai dasar kuat. |
| Need Review | Explanation tidak cukup informatif. | Pengguna wajib meninjau manual. |

### Batasan

1. HiResCAM menjelaskan keputusan model, bukan membuktikan diagnosis klinis.
2. Heatmap tidak boleh menjadi satu-satunya dasar keputusan.
3. Heatmap harus ditinjau bersama predicted class, confidence score, dan penilaian pengguna klinis.
4. Heatmap yang tidak informatif harus mengarah ke status Need Review.

# 11. Decision Tree Rule-Based Recommendation Phase 1

### Tujuan

Decision Tree digunakan untuk menerjemahkan output model classification menjadi risk level dan saran tindakan lanjutan secara umum. Modul ini bukan diagnosis engine dan tidak memberikan terapi.

### Input Decision Tree

1. Predicted class.
2. Confidence score.
3. Probability distribution.
4. Image quality status.
5. HiResCAM explanation status.
6. Optional clinical input seperti nyeri dada, sesak, atau riwayat penyakit jantung.

### Output Decision Tree

1. Risk level.
2. General follow-up recommendation.
3. Rationale text.
4. Decision path.
5. Safety disclaimer.

### Risk Level

| Risk Level | Makna |
| --- | --- |
| Low | Tidak ada indikasi abnormal kuat berdasarkan model. |
| Moderate | Perlu evaluasi klinis lanjutan atau manual review. |
| High | Perlu tinjauan klinis segera, terutama bila gejala mendukung. |
| Need Review | Hasil tidak cukup yakin atau explanation tidak informatif. |
| Uncertain | Input/model tidak cukup dapat diandalkan. |

### Rule Decision Tree Phase 1

| Rule | Kondisi | Risk Level | Recommendation |
| --- | --- | --- | --- |
| DT-01 | Kualitas citra buruk | Uncertain | Unggah ulang atau pemeriksaan ulang. |
| DT-02 | Confidence < 0.60 | Need Review | Manual review dan pertimbangkan upload ulang. |
| DT-03 | MI, confidence >= 0.80 | High | Tinjauan klinis segera; pertimbangkan rujukan sesuai SOP jika gejala mendukung. |
| DT-04 | MI, confidence 0.60-0.79 | Moderate to High | Evaluasi klinis lanjutan dan manual review. |
| DT-05 | Normal, confidence >= 0.80 | Low | Tidak ditemukan indikasi abnormal kuat; tetap korelasikan dengan kondisi klinis. |
| DT-06 | Normal, confidence 0.60-0.79 | Need Review | Pertimbangkan interpretasi manual jika terdapat gejala klinis. |
| DT-07 | Abnormal Heartbeat, confidence >= 0.60 | Moderate | Evaluasi klinis lanjutan dan interpretasi manual. |
| DT-08 | History of MI, confidence >= 0.60 | Moderate | Review riwayat klinis dan evaluasi elektif sesuai konteks. |
| DT-09 | HiResCAM off-target atau diffuse | Need Review | Visual explanation tidak cukup informatif; tinjau manual. |
| DT-10 | Gejala akut walaupun confidence rendah/sedang | Need Review / High | Prioritaskan evaluasi klinis manual. |

### Batasan Decision Tree Phase 1

1. Tidak menggunakan bounding box.
2. Tidak menggunakan lokasi sadapan.
3. Tidak mendeteksi ST elevation, T inversion, atau Q patologis spesifik.
4. Tidak memberikan diagnosis final.
5. Tidak memberikan terapi spesifik.

# 12. Rule-Based Triage Engine Phase 2

### Tujuan

Rule-Based Triage Engine Phase 2 digunakan setelah tersedia model detection berbasis anotasi dokter spesialis. Engine ini memproses hasil deteksi morfologi EKG menjadi triage level dan rationale yang lebih detail.

### Input Phase 2

1. Bounding box.
2. Class code.
3. Confidence per bounding box.
4. Lead location.
5. ST elevation count.
6. ST depression count.
7. T inversion count.
8. Pathological Q count.
9. QRS widening.
10. Rhythm anomaly.
11. Artifact severity.
12. Mean YOLO confidence.

### Rule Set Phase 2

| Kelompok Rule | Fungsi | Triage |
| --- | --- | --- |
| R1-R4 | Deteksi STEMI berbasis ST elevation pada lead terkait. | RED |
| R5-R7 | Deteksi NSTEMI / iskemia berbasis T inversion, ST depression, atau input klinis. | YELLOW |
| R8-R9 | Deteksi History of MI dan kemungkinan iskemia residual. | YELLOW |
| R10-R13 | Deteksi abnormal heartbeat seperti AF, VT, SVT, bradikardia, blok, BBB. | YELLOW / RED |
| R14-R16 | Quality gate untuk artefak, confidence rendah, atau tidak ada deteksi. | Manual Review |
| R17 | Default normal jika tidak ada rule aktif. | GREEN |

### Output Phase 2

1. Class 4.
2. Triage level.
3. Rules fired.
4. Evidence.
5. Rationale.
6. General recommended action.
7. Disclaimer.

### Conflict Resolution

Jika lebih dari satu rule aktif, prioritas triage adalah **RED > YELLOW > GREEN**. Semua rule yang aktif tetap ditampilkan, tetapi triage akhir mengikuti level risiko tertinggi.

**Status saat ini:** Rule R1-R17 diposisikan sebagai Phase 2 karena membutuhkan model detection, bounding box, lead location, dan anotasi dokter spesialis jantung.

# 13. Functional Requirements

| ID | Requirement | Deskripsi |
| --- | --- | --- |
| FR-01 | Authentication | Login berbasis email dan password. |
| FR-02 | Role-Based Access Control | Role Admin, Clinician, Researcher, dan Expert Reviewer. |
| FR-03 | Upload ECG Image | Menerima JPG, JPEG, PNG; ukuran awal maksimal 10 MB. |
| FR-04 | File Validation | Validasi format, ukuran, resolusi, dan file rusak. |
| FR-05 | Image Quality Check | Menilai blur, noise, brightness, contrast, orientation, readability. |
| FR-06 | Preprocessing | Resize, normalisasi, konversi warna, padding/cropping, simpan processed image. |
| FR-07 | Model Selection | Admin/Researcher memilih YOLOv8n-cls, YOLOv11n-cls, atau YOLOv26n-cls. |
| FR-08 | Classification Inference | Menghasilkan predicted class, confidence, probabilities, inference time, metadata. |
| FR-09 | HiResCAM Generation | Menghasilkan heatmap, overlay image, explanation status. |
| FR-10 | Decision Tree Recommendation | Menghasilkan risk level, recommendation, rationale, decision path. |
| FR-11 | Result Display | Menampilkan original ECG, heatmap, overlay, prediction, confidence, risk, recommendation, metadata. |
| FR-12 | Manual Note | Pengguna dapat menambahkan catatan dan status validasi manual. |
| FR-13 | Examination History | Menyimpan riwayat pemeriksaan dan dapat difilter. |
| FR-14 | PDF Report | Export laporan dengan citra, heatmap, hasil, rekomendasi, disclaimer, metadata. |
| FR-15 | Evaluation Dashboard | Metrics, confusion matrix, model comparison, inference time, low-resource score. |
| FR-16 | Audit Trail | Catat login, upload, inference, HiResCAM, Decision Tree, note, export, model switching. |
| FR-17 | Expert Review Module | Phase 2: daftar rule, status persetujuan, revisi, sign-off. |

# 14. Non-Functional Requirements

| Kategori | Requirement |
| --- | --- |
| Performance | Inference GPU < 5 detik/citra; inference CPU < 15 detik/citra; HiResCAM < 10 detik; PDF < 10 detik. |
| Usability | Alur singkat, hasil jelas, rekomendasi umum, disclaimer eksplisit, menghindari istilah diagnosis pasti. |
| Interpretability | HiResCAM, original image, overlay, confidence, decision path, rationale, rules fired untuk Phase 2. |
| Safety | Tidak memberi diagnosis final, terapi, resep, atau menggantikan dokter; hasil tidak pasti diarahkan ke manual review. |
| Security | Authentication, password hashing, RBAC, upload validation, sanitasi input, akses data terbatas. |
| Maintainability | Modular: frontend, backend API, AI service, Decision Tree service, database, storage, report generator. |
| Reproducibility | Simpan model name/version, dataset version, input size, preprocessing config, threshold, device, timestamp, Decision Tree version, HiResCAM config. |

# 15. Database dan API Requirement

### Database Requirement

| Tabel | Field Utama |
| --- | --- |
| User | id, name, email, password\_hash, role, is\_active, created\_at, updated\_at. |
| Examination | id, user\_id, image paths, predicted\_class, confidence\_score, probability\_json, risk\_level, recommendation, rationale, clinician\_note, validation\_status, model\_id, decision\_tree\_version, inference\_time, image\_quality\_status, explanation\_status, low\_resource\_score, timestamps. |
| Model Metadata | id, model\_name, model\_version, architecture, task\_type, dataset\_version, input\_size, model\_file\_path, threshold\_config, model\_size, training\_date. |
| Decision Rule | id, rule\_code, phase, condition\_json, output\_risk\_level, recommendation\_template, rationale\_template, version, is\_active. |
| Audit Log | id, user\_id, action, entity\_type, entity\_id, description, ip\_address, user\_agent, created\_at. |
| Expert Review | id, reviewer\_id, rule\_id, decision, modification\_note, rejection\_reason, reviewed\_at. |
| Detection Result Phase 2 | id, examination\_id, bbox\_x, bbox\_y, bbox\_width, bbox\_height, class\_code, confidence, lead\_location, created\_at. |

### API Contract Ringkas

| Endpoint | Method | Fungsi |
| --- | --- | --- |
| /api/auth/login | POST | Login dan mendapatkan token. |
| /api/auth/logout | POST | Logout pengguna. |
| /api/ecg/analyze | POST | Upload dan analisis citra EKG. |
| /api/examinations | GET | Daftar riwayat pemeriksaan. |
| /api/examinations/:id | GET | Detail pemeriksaan. |
| /api/examinations/:id/note | PATCH | Update catatan dan validasi manual. |
| /api/examinations/:id/report | GET | Export PDF report. |
| /api/models | GET | Daftar model tersedia. |
| /api/models/active | PATCH | Set model aktif. |
| /api/research/evaluation | GET | Metrik, confusion matrix, model comparison, low-resource score. |
| /api/research/batch-evaluate | POST | Evaluasi batch dataset. |
| /api/detection/analyze | POST | Phase 2 detection-based analysis. |

# 16. UI/UX Requirement

| Halaman | Komponen Utama |
| --- | --- |
| Login Page | Email, password, login button, disclaimer prototype penelitian. |
| Dashboard | Total pemeriksaan, high risk count, need review count, average confidence, average inference time, low-resource readiness status, shortcut upload. |
| Upload Page | Drag and drop upload, preview image, file validation, image quality warning, model selector, optional clinical input, analyze button. |
| Result Page | Original ECG, HiResCAM heatmap, overlay, predicted class, confidence, probabilities, risk badge, recommendation, rationale, decision path, explanation status, disclaimer, manual note, save, export PDF. |
| History Page | Table pemeriksaan, filter tanggal, filter model, filter risk level, detail button, export report. |
| Research Dashboard | Model comparison, confusion matrix, metrics table, error analysis, HiResCAM gallery, inference time chart, model size comparison, CPU/GPU comparison, low-resource readiness score. |
| Expert Review Page Phase 2 | Rule list, evidence, rules fired, agreement form, modification note, sign-off status. |

# 17. Evaluation Protocol

### Model Evaluation

1. Accuracy.
2. Precision.
3. Recall.
4. F1-score.
5. Macro average.
6. Weighted average.
7. Sensitivity.
8. Specificity.
9. Confusion matrix.
10. ROC-AUC jika memungkinkan.

**Prioritas medis:** recall kelas Myocardial Infarction, false negative analysis, dan error analysis pada kelas abnormal.

### HiResCAM Evaluation

1. Visual inspection.
2. Relevance of highlighted region.
3. Perbandingan true positive dan false positive.
4. Perilaku heatmap pada false negative.
5. Expert review jika tersedia.

### Decision Tree Evaluation

1. Rule coverage.
2. Distribusi risk level.
3. Jumlah kasus Need Review.
4. Consistency check.
5. Agreement dengan reviewer klinis jika tersedia.
6. Decision path audit.

### Low-Resource Readiness Evaluation

| Metrik | Tujuan |
| --- | --- |
| CPU inference time | Menilai kelayakan tanpa GPU. |
| GPU inference time | Menilai performa jika GPU tersedia. |
| RAM usage | Menilai kesesuaian dengan perangkat standar. |
| Model size | Menilai efisiensi model. |
| Local deployment feasibility | Menilai kemampuan berjalan lokal/LAN. |
| Internet independence | Menilai kemampuan inferensi tanpa cloud. |
| User flow length | Menilai kesederhanaan workflow. |
| HiResCAM/PDF generation time | Menilai kelayakan operasional. |

### System and Usability Evaluation

1. API response time.
2. Upload failure rate.
3. Error rate.
4. Storage usage.
5. System Usability Scale.
6. Task completion rate.
7. Time on task.
8. User satisfaction.
9. Qualitative feedback.

# 18. Clinical Safety Requirement

### Disclaimer Wajib

**Disclaimer:** Hasil ini merupakan skrining otomatis berbasis AI dan bukan diagnosis final. Keputusan klinis tetap harus dikonfirmasi oleh tenaga kesehatan dengan mempertimbangkan gejala, riwayat klinis, EKG serial, dan pemeriksaan pendukung.

### Forbidden Output

Sistem tidak boleh menghasilkan:

1. Diagnosis final.
2. Instruksi terapi definitif.
3. Resep obat.
4. Dosis obat.
5. Keputusan tindakan invasif.
6. Pernyataan bahwa pasien pasti menderita penyakit tertentu.
7. Pernyataan bahwa pasien pasti aman tanpa evaluasi klinis.

### Safe Recommendation Pattern

1. “Perlu tinjauan klinis.”
2. “Pertimbangkan evaluasi lanjutan sesuai SOP setempat.”
3. “Disarankan manual review.”
4. “Disarankan unggah ulang citra jika kualitas tidak memadai.”
5. “Korelasikan dengan gejala dan pemeriksaan pendukung.”

# 19. Acceptance Criteria

### MVP Phase 1 Accepted Jika

1. User dapat login.
2. User dapat upload citra EKG.
3. Sistem memvalidasi file.
4. Sistem menjalankan image quality check.
5. Sistem menjalankan YOLO classification.
6. Sistem menampilkan predicted class, confidence score, dan class probabilities.
7. Sistem menghasilkan HiResCAM dan overlay.
8. Decision Tree menghasilkan risk level dan saran tindakan umum.
9. Sistem menampilkan disclaimer.
10. User dapat menambahkan catatan.
11. Sistem menyimpan riwayat.
12. Sistem dapat export PDF.
13. Dashboard evaluasi dan model comparison tersedia.
14. Audit trail berjalan.
15. Sistem tidak memberi diagnosis final atau terapi spesifik.
16. Sistem dapat berjalan secara lokal.
17. Sistem dapat melakukan inferensi tanpa internet.
18. Sistem memperoleh low-resource readiness score minimal 17 dari 24.

### Phase 2 Accepted Jika

1. Dataset detection sudah dianotasi.
2. YOLO detection model dapat dilatih.
3. Sistem menghasilkan bounding box.
4. Sistem dapat melakukan lead location mapping.
5. Feature Aggregator menghasilkan feature vector.
6. Rule R1-R17 dapat dijalankan.
7. Rules fired dan rationale ditampilkan.
8. Expert validation form tersedia.
9. Rule dapat direvisi berdasarkan masukan Sp.JP.

# 20. Risk Register dan Roadmap Development

### Risk Register

| ID | Risiko | Dampak | Mitigasi |
| --- | --- | --- | --- |
| R-01 | False negative MI | Tinggi | Prioritaskan recall MI, Need Review untuk confidence rendah, error analysis. |
| R-02 | False positive MI | Sedang | Tampilkan confidence dan HiResCAM; arahkan ke clinical review. |
| R-03 | Overtrust terhadap AI | Tinggi | Human-in-the-loop, disclaimer, manual review, uncertainty display. |
| R-04 | HiResCAM menyesatkan | Sedang | Explanation status, off-target warning, evaluasi heatmap. |
| R-05 | Kualitas citra buruk | Sedang | Image quality check, re-upload recommendation, manual review. |
| R-06 | Rule terlalu klinis | Tinggi | Gunakan general recommendation, hindari terapi, validasi Sp.JP. |
| R-07 | Anotasi detection belum tersedia | Sedang | Phase 1 tetap berjalan, Phase 2 sebagai roadmap. |
| R-08 | Sistem tidak layak low-resource | Tinggi | Model lightweight, uji CPU-only, local deployment, UI ringkas. |
| R-09 | Internet tidak stabil | Sedang | Inferensi lokal, sinkronisasi opsional, cloud hanya tambahan. |
| R-10 | Perangkat tidak memadai | Sedang | Model nano, optimasi input size, evaluasi RAM, fallback manual review. |

### Roadmap Sprint

| Sprint | Fokus | Output |
| --- | --- | --- |
| 1 | Project Foundation | Repository, frontend, backend, database, storage. |
| 2 | Authentication and Upload | Login, role, upload, validation, preview, image quality check. |
| 3 | AI Inference | Load YOLOv8n-cls, YOLOv11n-cls, YOLOv26n-cls; prediction endpoint. |
| 4 | HiResCAM | Generate heatmap, overlay, display, storage. |
| 5 | Decision Tree | Rule DT-01 sampai DT-10, risk level, recommendation, decision path. |
| 6 | History and PDF | Save examination, history, detail, PDF report. |
| 7 | Research Dashboard | Confusion matrix, metrics, model comparison, error analysis, low-resource score. |
| 8 | Audit and Finalization | Audit trail, security hardening, documentation, demo-ready prototype. |
| 9 | Phase 2 Preparation | Annotation protocol, detection schema, expert review form, rule validation workflow. |

# 21. Novelty, Batasan, dan Deliverables

### Novelty Penelitian

1. CDSS berbasis citra EKG 12-lead untuk low-resource settings.
2. Integrasi YOLOv8n-cls, YOLOv11n-cls, dan YOLOv26n-cls untuk klasifikasi citra EKG.
3. Integrasi HiResCAM untuk interpretabilitas visual.
4. Penggunaan Decision Tree sebagai general follow-up recommendation layer.
5. Evaluasi low-resource readiness melalui parameter teknis, klinis, usability, safety, dan auditability.
6. Strategi bertahap dari classification-based CDSS menuju detection-based CDSS.
7. Persiapan Rule-Based Triage R1-R17 untuk validasi Sp.JP.
8. Audit trail dan model metadata untuk reproducibility.

### Batasan Penelitian

1. Sistem menggunakan citra EKG, bukan sinyal EKG mentah.
2. Fase awal hanya menggunakan classification model.
3. Detection model menunggu anotasi dokter spesialis.
4. Sistem bukan medical device resmi.
5. Sistem tidak memberi diagnosis final atau terapi spesifik.
6. Validasi klinis eksternal belum menjadi bagian MVP.
7. Performa sistem bergantung pada kualitas dataset.
8. HiResCAM hanya menjelaskan keputusan model.
9. Decision Tree hanya menghasilkan saran tindakan umum.
10. Low-resource readiness diuji sebagai prototype, bukan klaim implementasi klinis penuh.

### Product Deliverables

1. Web CDSS prototype.
2. YOLO classification inference service.
3. HiResCAM module.
4. Decision Tree Recommendation Layer.
5. Dashboard evaluasi.
6. Riwayat pemeriksaan.
7. Export PDF.
8. Audit trail.
9. Model metadata management.
10. Low-resource readiness dashboard.

### Research Deliverables

1. Grand PRD.
2. System Architecture Document.
3. Dataset & Evaluation Protocol.
4. Decision Tree Rule Specification.
5. HiResCAM Explainability Protocol.
6. Clinical Safety & Risk Management.
7. Low-Resource Settings Parameter & Evaluation Protocol.
8. API Contract & Database Schema.
9. Annotation Protocol Phase 2.
10. Expert Validation Form Sp.JP.
11. Hasil eksperimen model.
12. Draft artikel ilmiah.

# 22. Kesimpulan

EKG-Insight CDSS v3 merupakan rancangan prototype penelitian yang menggabungkan model YOLO classification, HiResCAM, Decision Tree Rule-Based Recommendation, dan parameter low-resource settings. Sistem ini dirancang sebagai clinical decision support system untuk membantu skrining awal abnormalitas EKG 12-lead, bukan sebagai alat diagnosis final.

Pada Phase 1, sistem menggunakan YOLOv8n-cls, YOLOv11n-cls, dan YOLOv26n-cls untuk klasifikasi citra EKG. HiResCAM digunakan untuk visual explanation, sedangkan Decision Tree digunakan untuk menghasilkan risk level dan saran tindakan umum. Sistem juga mengevaluasi kesiapan implementasi pada low-resource settings melalui parameter CPU-only inference, local deployment, model size, RAM usage, usability, safety, dan auditability.

Pada Phase 2, sistem akan dikembangkan menjadi detection-based CDSS setelah anotasi dokter spesialis jantung tersedia. Phase 2 akan menggunakan YOLO detection, Feature Aggregator, dan Rule-Based Triage Engine R1-R17 yang divalidasi oleh Sp.JP.

**Kesimpulan utama:** penelitian ini tidak hanya menghasilkan model klasifikasi EKG, tetapi juga prototype CDSS yang explainable, auditable, safety-aware, dan relevan untuk lingkungan dengan sumber daya terbatas.
