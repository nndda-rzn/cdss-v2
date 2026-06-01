# Design Spec: Medical-Grade Focus Mode (AI Analysis)

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: 2026-06-01-ai-analysis-full-page-design, ADR-0010, ADR-0012, ADR-0006

## Context

The AI analysis page (`/encounters/:id/ecg-studies/:studyId/analyses`) is still
wrapped by `AppShell` — the full app chrome with the left sidebar nav, global
search, language toggle, and user menu. When a clinician reads ECG analysis
results, that chrome competes for attention. The maintainer asked for a
"medical instrument" feel: like a Philips / GE / Schiller ECG workstation,
focused entirely on the patient and the reading.

## Decision

Introduce a `FocusShell` layout (no sidebar) and mount the analysis page under
it. Decisions, per the maintainer:

- **Header (B): minimal medical-style.** Small brand mark + patient identity
  strip + an "Keluar" (Exit) button. No global search, language toggle, or
  user menu.
- **Background (A): `bg-charcoal-50`** — a clinical neutral, cooler than stark
  white, still light mode (no dark mode per project decision).
- **Patient identity (A): shown** — name (masked per role), MRN, DOB, gender +
  computed age.
- **Scope:** the analysis page only for now. `FocusShell` is reusable so
  Sprint 4 (HiResCAM heatmap inspection) can adopt it.
- **Exit button (A):** navigates to `/encounters/:id` (the parent encounter),
  not to dashboard and not a system logout.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│ ⚡EKG-Insight │ Budi S*** · MRN-P1-001 · 1965-03-12 (♂ 60th) │ Keluar │
├──────────────────────────────────────────────────────────────┤
│  (bg-charcoal-50, px-6 md:px-10 py-6)                          │
│  Analisis AI · Studi ECG-P1-...                                │
│  ┌────────────────────────────┐  ┌──────────────────┐         │
│  │ StudyHeaderCard (3fr)      │  │ ConsensusCard 1fr │         │
│  └────────────────────────────┘  └──────────────────┘         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ AnalysisDetailTable (full width)                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│  [Analisis ulang] [Cetak] [Kembali]   (.no-print)             │
└──────────────────────────────────────────────────────────────┘
```

## New Components

| File | Responsibility |
|------|----------------|
| `frontend/src/components/layout/FocusShell.tsx` | Sidebar-less layout: minimal sticky header (h-12, brand + Exit) + `bg-charcoal-50` main with `<Outlet />`. |
| `frontend/src/components/layout/PatientIdentityStrip.tsx` | Horizontal identity strip: masked name, MRN, DOB, gender + computed age. Anonymised for researcher. Print-friendly. |

## Changed

- `frontend/src/App.tsx`: move the analysis route out of the `<AppShell>` group
  into a new `<FocusShell>` group (both under `<ProtectedRoute>`).
- `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`: fetch the
  patient (via `study.patient_id`), render `<PatientIdentityStrip>` at the top,
  widen the main grid to `lg:grid-cols-[3fr_1fr]`.

## RBAC / Privacy

- Patient identity is fetched via the existing `GET /api/patients/:id`, which
  already enforces role-based field stripping (researcher / expert_reviewer
  receive an anonymised, sidebar-less variant with `is_pseudonymized`).
- The strip renders "Pasien Anonim" (no MRN, no name) when `is_pseudonymized`
  is true or name/MRN are absent.
- The "Analisis ulang" button remains gated to clinician/nurse via RoleGate
  (unchanged from the previous page).

## Out of Scope

- Removing other pages from the sidebar (dashboard, patients, encounter detail
  stay in `AppShell`).
- Dark mode.
- Backend changes (existing patient + study + analyses endpoints suffice).
- New print button (the existing footer one stays).
- Changing `AnalysisDetailTable` columns.

## Acceptance Criteria

- AC-1: The analysis route renders in `FocusShell` — no left sidebar, minimal
  header.
- AC-2: Header shows small brand + `PatientIdentityStrip` + "Keluar" button;
  no global search, language toggle, or user menu.
- AC-3: Strip shows masked name, MRN, DOB, gender + computed age.
- AC-4: For researcher (pseudonymised), the strip shows "Pasien Anonim · DOB ·
  gender" (no MRN / name).
- AC-5: Page background is `bg-charcoal-50`, outer padding `px-6 md:px-10 py-6`.
- AC-6: ECG image column is wider than before (`3fr_1fr` vs `2fr_1fr`).
- AC-7: Other pages keep `AppShell` + sidebar (no regression).
- AC-8: Print mode works: footer buttons hidden via `.no-print`; strip prints.
- AC-9: "Keluar" navigates to `/encounters/:id` (not logout, not dashboard).
- AC-10: Frontend gate green (typecheck + lint + tests + build); file-size
  guard exits 0.

## Implementation Notes

- `AnalysisDetailPage` owns the patient query and renders the strip itself;
  `FocusShell` stays a dumb layout (brand + Exit + Outlet). This avoids passing
  patient data through router context.
- Compute age client-side from `dob`; bilingual "tahun" / "yo".
- The patient query is `enabled` only after the study query resolves (needs
  `study.patient_id`). If patient fetch fails (e.g. researcher field-strip),
  render the strip in a minimal/anon form rather than erroring the page.
- Keep each new file under the 200-line budget.
