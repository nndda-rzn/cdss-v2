# Design Spec: Frontend Feature-Sliced Design (FSD-lite) Refactor

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: 2026-05-31-ui-ux-audit-pass-1, 2026-06-01-saas-ui-polish-design

## Context

The frontend feature folders started flat — all files live directly under
`frontend/src/features/<feature>/`. Over five sprints they have grown to a
mixed bag of API clients, schemas, page components, embedded widgets, hooks
(occasionally), tests, and pure helpers, with no internal organization.

Reading any one feature now requires opening every file to understand which
piece is a route page, which is a building block, which is data layer, and
which is a pure helper. New features have copied this flat shape, so the
problem is structural and growing.

The maintainer requested an explicit Feature-Sliced Design (FSD-lite) layout
for `patient/` and asked to apply the same shape to **every** feature. This
spec captures the standard layout and the per-feature mapping.

## Decision

Adopt a uniform internal layout for every folder under `frontend/src/features/`:

```text
<feature>/
├── api.ts          // fetch wrappers + react-query keys
├── types.ts        // domain TypeScript types (no Zod)
├── schemas.ts      // optional — Zod schemas + form values
├── hooks/          // optional — useQuery / useMutation hooks
│   └── use<X>.ts
├── components/     // UI building blocks specific to the feature
│   └── <X>.tsx
├── pages/          // optional — route-level components rendered by /routes
│   └── <X>.tsx
└── __tests__/      // optional — colocated tests
    └── <X>.test.tsx
```

Each subfolder is **optional**: a feature without a route page (e.g. `consent`,
`search`) skips `pages/`; a feature without form validation skips `schemas.ts`;
a feature without React Query usage skips `hooks/`.

`types.ts` is required when the feature exposes domain shapes that are
referenced from more than one file. Pure helper files (e.g. `vital_signs/ranges.ts`,
`ai_analysis/labels.ts`) keep their existing names and stay at the feature
root because they are not "types".

The page/component split follows one rule: a file goes in `pages/` if and only
if it is mounted directly by a `<Route>` element in `App.tsx`. Everything else
is `components/`, even if it is large.

## Out of Scope

- Renaming files (we move them but don't rename, to keep the diff readable).
- Splitting any file beyond what the file-size budget already enforces.
- Moving or renaming files under `frontend/src/components/`, `lib/`,
  `routes/`, or `store/` — those layers are already healthy.
- Backend changes — this is purely a frontend refactor.
- New features or behaviour — purely structural.

## Per-Feature Mapping

The 11 features land in the new layout as follows. `→` shows the new path
relative to the feature root.

### ai_analysis
- `AnalysisPanel.tsx` → `components/`
- `AnalysisTable.tsx` → `components/`
- `AnalysisPanel.test.tsx` → `__tests__/`
- `api.ts`, `labels.ts` stay at root
- new: `types.ts` (extract `PredictedClass`, `AnalysisRow`, `RunResponse`)

### auth
- `LoginForm.tsx`, `LoginBrandPanel.tsx`, `ProtectedRoute.tsx`,
  `RoleGate.tsx` → `components/`
- `LoginForm.test.tsx`, `ProtectedRoute.test.tsx`, `RoleGate.test.tsx`,
  `store.test.ts` → `__tests__/`
- `api.ts`, `store.ts` stay at root
- new: `types.ts` (extract `LoginValues`, `JwtClaims`)

### clinical_context
- `ContextForm.tsx` → `components/`
- `api.ts` stays at root
- new: `types.ts` (extract `ClinicalContextRow`)

### consent
- `ConsentPanel.tsx` → `components/`
- `api.ts` stays at root
- new: `types.ts`

### dashboard
- `DashboardPage.tsx` → `pages/`
- `KpiCard.tsx`, `QuickActions.tsx`, `RecentEncountersList.tsx` →
  `components/`
- `api.ts` stays at root
- new: `types.ts` (extract `RecentEncounter`, `DashboardStats`)

### ecg_study
- `EcgStudyList.tsx`, `EcgUploadForm.tsx` → `components/`
- `EcgStudyList.test.tsx`, `EcgUploadForm.test.tsx` → `__tests__/`
- `api.ts` stays at root
- new: `types.ts` (extract `EcgStudy`, `Quality`)

### encounter
- `Detail.tsx`, `CreateForm.tsx` → `pages/`
- `api.ts` stays at root
- new: `types.ts` (extract `Encounter`, `EncounterCreateValues`)

### patient
- `PatientList.tsx`, `PatientDetail.tsx` → `pages/`
- `DedupDialog.tsx`, `DeleteDialog.tsx`, `IdentitySidebar.tsx`,
  `RegisterForm.tsx` → `components/`
- `RegisterForm.test.tsx` → `__tests__/`
- `api.ts`, `schemas.ts` stay at root
- new: `types.ts` (extract `PatientListItem`, `PatientDetail`,
  `DuplicateSuggestion`)

### patient_history
- `HistoryPanel.tsx` → `components/`
- `api.ts` stays at root
- new: `types.ts`

### search
- `GlobalSearch.tsx`, `GlobalSearchTrigger.tsx`, `SearchResultList.tsx` →
  `components/`
- `api.ts`, `hooks.ts` stay at root (`hooks.ts` is two pure utility hooks,
  not React-Query — leave it alone)
- new: `types.ts` (extract `PatientHit`, `EncounterHit`, `SearchResults`)

### vital_signs
- `VitalsPanel.tsx`, `MiniCard.tsx` → `components/`
- `ranges.test.ts` → `__tests__/`
- `api.ts`, `ranges.ts` stay at root
- new: `types.ts` (extract `VitalRow`, `VitalsInput`)

## Acceptance Criteria

- AC-1: Every folder under `frontend/src/features/` matches the layout above.
  No `.tsx` file lives at a feature root.
- AC-2: All page-level files (mounted by `<Route>` in `App.tsx`) live under
  `pages/`; all other components live under `components/`.
- AC-3: Each feature exposes a `types.ts` that re-exports its public domain
  shapes (consumers import from `@/features/<feature>/types`, not from
  `api.ts`).
- AC-4: All existing imports across the codebase resolve (no broken paths).
- AC-5: `npm run typecheck`, `npm run lint`, `npm run test`, and
  `npm run build` all succeed.
- AC-6: `python scripts/check_file_size.py` exits 0.
- AC-7: No behavioural change — existing tests pass without modification
  beyond import-path updates.

## Implementation Notes

- Use `git mv` for every relocation so blame history follows the file.
- Keep one feature per commit so review and rollback stay tractable.
- Update consumers (App.tsx, routes/, other features) in the same commit
  that moves the files, otherwise typecheck breaks mid-refactor.
- The file-size budget guard does **not** check docs, but it does check
  every TS/TSX file. Watch out when extracting `types.ts` from large
  `api.ts` files — the new file plus the trimmed `api.ts` should each
  stay well under 200 code lines.
- Subagents handling each feature receive the per-feature mapping above
  verbatim. Don't let them improvise a different shape.
