# Design Spec: AI Analysis Full-Page View

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: ADR-0004 (5 YOLO models), ADR-0012 (bilingual), ADR-0013 (inferno heatmap, Sprint 4), 2026-06-01-saas-ui-polish-design

## Context

The AI analysis comparison (5 YOLO models) currently renders inside the ECG
study card, behind a `<details>` toggle, in a `lg:grid-cols-3` column. The
table is cramped: it scrolls horizontally (the "Prediksi" header clipped to
"EDIKSI"), the confidence bar is capped at 120px, and the consensus is a
single small line. The maintainer asked to move this onto a large, dedicated
screen while keeping all five models (multi-model comparison is the research
selling point per ADR-0004).

## Decision

Introduce a dedicated route `/encounters/:id/ecg-studies/:studyId/analyses`
that renders the AI analysis full-page. The ECG study card keeps a
"Lihat Analisis AI →" link instead of an inline panel.

Why a route (not a dialog): shareable URL, browser back/forward, print-friendly
(clinicians print summaries), bookmarkable. All decisive for a clinical
context.

## Layout

```
← Kembali ke Kunjungan #<id>
Analisis AI · <study_uid>
<acquired_at> · Kualitas: <status> (<score>)
─────────────────────────────────────────────
┌─────────────────────────┐  ┌────────────────┐
│ StudyHeaderCard         │  │ ConsensusCard  │
│ ECG image (zoomable,    │  │ dominant class │
│ ~600px) + metadata      │  │ X of N agree   │
│ + QualityBadge          │  │ avg confidence │
└─────────────────────────┘  └────────────────┘
┌──────────────────────────────────────────────┐
│ AnalysisDetailTable (full width, 8 columns)   │
│ Arsitektur · Prediksi · Keyakinan · Inferensi │
│ · Status · Normal · MI · Riwayat MI · Aritmia │
└──────────────────────────────────────────────┘
[Analisis ulang] [Cetak] [Kembali]   (.no-print)
```

## New Components

| File | Responsibility |
|------|----------------|
| `routes/AnalysisDetailRoute.tsx` | Thin wrapper, reads `:id` + `:studyId` |
| `features/ai_analysis/pages/AnalysisDetailPage.tsx` | Full-page layout, data orchestration, mutation |
| `features/ai_analysis/components/ConsensusCard.tsx` | Large consensus card with tone by dominant class |
| `features/ai_analysis/components/AnalysisDetailTable.tsx` | 8-column table incl. per-class probabilities + a11y caption |
| `features/ai_analysis/components/StudyHeaderCard.tsx` | Large zoomable ECG image + study metadata |

## Changed

- `App.tsx`: add the new route under ProtectedRoute + AppShell.
- `features/ecg_study/components/EcgStudyList.tsx`: replace inline
  `<details><AnalysisPanel/></details>` with a `<Link>` to the detail page.
- `features/ecg_study/api.ts`: add `fetchEcgStudy(encounterId, studyId)` +
  `ecgKeys.detail(...)`.
- `backend/app/api/ecg_studies.py`: add `GET /<encounter_id>/ecg-studies/<study_id>`.

## Removed (YAGNI — no consumers after migration)

- `features/ai_analysis/components/AnalysisPanel.tsx`
- `features/ai_analysis/components/AnalysisTable.tsx`
- `features/ai_analysis/__tests__/AnalysisPanel.test.tsx`

## RBAC Matrix

| Role | Page access | "Analisis ulang" | Cetak / Kembali |
|------|-------------|------------------|-----------------|
| clinician | yes | yes | yes |
| nurse | yes | yes | yes |
| admin | yes (read) | hidden (RoleGate) | yes |
| researcher | yes (read) | hidden (RoleGate) | yes |
| expert_reviewer | 403 from API → empty state "Akses ditolak" | — | — |

The "Analisis ulang" button is wrapped in `<RoleGate allow={["clinician","nurse"]}>`.
The page shows an access-denied empty state if the analyses query 403s.

## Out of Scope

- HiResCAM heatmap overlay (Sprint 4).
- PDF export (window.print only).
- Side-by-side study comparison.
- Editing/deleting individual analyses.
- Changing the model count (stays 5).

## Acceptance Criteria

- AC-1: "Lihat Analisis AI →" navigates to the route; page renders full viewport.
- AC-2: Page renders StudyHeaderCard, ConsensusCard, and an 8-column table.
- AC-3: Footer has Analisis ulang · Cetak · Kembali, all `.no-print`.
- AC-4: Table does not scroll horizontally at >= md (768px).
- AC-5: Confidence bar is full column width (not capped at 120px).
- AC-6: Consensus shows dominant class + agreement count + avg confidence;
  bilingual low-agreement warning when agreement < 60%.
- AC-7: `<table>` has an sr-only `<caption>` and `aria-describedby` to the
  consensus card.
- AC-8: window.print produces clean output (buttons hidden via `.no-print`).
- AC-9: Bilingual ID/EN via the existing toggle.
- AC-10: "Analisis ulang" hidden for roles outside clinician/nurse.
- AC-11: A 403 from the analyses query renders an access-denied empty state.
- AC-12: Backend full suite passes (+2 new tests), ruff + mypy clean; frontend
  typecheck + lint + tests + build clean; file-size guard exits 0.
- AC-13: The three legacy files are removed.

## Implementation Notes

- The detail page fetches the study via the new single-study endpoint and the
  analyses via the existing list endpoint.
- Per-class probabilities come from `AnalysisRow.probability_json` keyed by
  `normal | mi | homi | abnormal`.
- Keep each new file under the 200-line budget; extract a `ProbabilityBar`
  helper if `AnalysisDetailTable` approaches it.
- Reuse `computeConsensus()` from `labels.ts`, `CLASS_CHIP`/`CLASS_LABEL`,
  `AuthedImage`, and `QualityBadge`.
