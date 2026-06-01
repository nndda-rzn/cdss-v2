# Medical-Grade Focus Mode Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task.

**Goal:** Render the AI analysis page in a sidebar-less, medical-instrument
"focus mode" with a minimal header that pins patient identity, while keeping
every other route on the normal `AppShell`.

**Architecture:** New `FocusShell` layout route (no sidebar) + reusable
`PatientIdentityStrip`. The analysis page owns the patient query and renders
the strip itself; `FocusShell` is a dumb layout (brand + Exit + Outlet).

**Tech Stack:** React, React Router v6 nested layout routes, Tailwind, Zustand
i18n, existing patient/study/analyses query layer.

---

## Task 1: PatientIdentityStrip component

**Files:** `frontend/src/components/layout/PatientIdentityStrip.tsx` (new)

- Props: `patient: PatientDetail`
- Compute age from `dob` (floor of year diff).
- If `is_pseudonymized` or no `name`: render "Pasien Anonim" / "Anonymous
  Patient" + DOB + gender only.
- Otherwise: masked name (from `name` field — already masked server-side for
  list contexts; detail reveals decrypted for clinician/nurse), MRN, DOB,
  gender + age.
- Bilingual via `useI18nStore`.
- Verify: `npm run typecheck`.
- Commit: `feat(ui): add PatientIdentityStrip for medical-grade headers`.

## Task 2: FocusShell layout

**Files:** `frontend/src/components/layout/FocusShell.tsx` (new)

- `useParams<{ id: string }>()` for the Exit target.
- Minimal sticky header (`h-12`, `bg-paper`, border-bottom): EcgSweep brand +
  wordmark on the left; "Keluar"/"Exit" button on the right linking to
  `/encounters/:id`.
- Main: `bg-charcoal-50 px-6 md:px-10 py-6` with `<Outlet />` wrapped in
  `animate-fadeIn`.
- Skip-to-content link for a11y (same pattern as AppShell).
- Verify: typecheck.
- Commit: `feat(layout): add FocusShell for medical-grade focus mode`.

## Task 3: Wire route under FocusShell

**Files:** `frontend/src/App.tsx`

- Move `<Route path="/encounters/:id/ecg-studies/:studyId/analyses">` out of the
  `<AppShell>` group into a new sibling `<Route element={<FocusShell />}>` group,
  both under `<ProtectedRoute>`.
- Verify: `npm run build`.
- Commit: `feat(routing): mount analysis detail under FocusShell`.

## Task 4: AnalysisDetailPage — strip + wider grid

**Files:** `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`

- Add a 3rd query: `patientKeys.detail(study.data.patient_id)` →
  `fetchPatient`, `enabled` only when `study.data?.patient_id` exists.
- Render `<PatientIdentityStrip patient={patient.data} />` above the heading
  when patient data is present.
- Change main grid `lg:grid-cols-[2fr_1fr]` → `lg:grid-cols-[3fr_1fr]`.
- Verify: typecheck + lint + `npm run test -- --run src/features/ai_analysis`.
- Commit: `feat(ai-analysis): pin patient identity strip and widen ecg column`.

## Task 5: Full gate

```bash
cd frontend
npm run typecheck && npm run lint && npm run test -- --run && npm run build

cd ..
backend/.venv/Scripts/python.exe scripts/check_file_size.py
```

Expected: all green, file-size guard EXIT 0.

## Task 6: Manual verification

- clinician → encounter → "Lihat Analisis AI →" → sidebar gone, minimal header
  with patient identity, Exit returns to encounter.
- background cooler (`bg-charcoal-50`), ECG image wider.
- Print → footer buttons hidden, strip prints.
- researcher → "Pasien Anonim" in strip; "Analisis ulang" hidden.

## Task 7: Push + PR

- Push branch `feat/focus-shell-analysis`.
- `gh pr create` with before/after note, AC checklist, spec link.
- Wait for CI, squash-merge.

---

## Acceptance Criteria

Mirrors the spec — see `2026-06-01-focus-shell-analysis-design.md`.
