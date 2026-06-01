# Frontend FSD-lite Refactor Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task.

**Goal:** Apply a uniform Feature-Sliced Design (FSD-lite) layout to all 11 directories under `frontend/src/features/`.

**Architecture:** Each feature gets `api.ts`, `types.ts`, optional `schemas.ts`, and the optional subfolders `hooks/`, `components/`, `pages/`, `__tests__/`. We use `git mv` to preserve blame and update consumer imports in the same commit.

**Tech Stack:** React, TypeScript, Vite, Tailwind, React Query, Zustand.

---

## File Structure (target)

```
features/<feature>/
  api.ts
  types.ts
  schemas.ts          # optional
  hooks/              # optional
  components/         # optional
  pages/              # optional
  __tests__/          # optional
```

---

## Tasks

Each task: extract types, `git mv` files into subfolders, fix imports, run gate, commit.

### Task 1: ai_analysis
- Move: `AnalysisPanel.tsx`, `AnalysisTable.tsx` -> `components/`
- Move: `AnalysisPanel.test.tsx` -> `__tests__/`
- Create: `types.ts` (extract `PredictedClass`, `AnalysisRow` from `api.ts`)
- Update consumers (encounter detail page, search trigger).
- Verify: `npm run typecheck && npm run test -- --run && npm run build`.
- Commit: `refactor(ai_analysis): adopt fsd-lite layout`.

### Task 2: auth
- Move: `LoginForm.tsx`, `LoginBrandPanel.tsx`, `ProtectedRoute.tsx`, `RoleGate.tsx` -> `components/`
- Move: `LoginForm.test.tsx`, `ProtectedRoute.test.tsx`, `RoleGate.test.tsx`, `store.test.ts` -> `__tests__/`
- Create: `types.ts` (extract `LoginValues`, `JwtClaims`).
- Update consumers (App.tsx, login route, UserMenu).
- Commit: `refactor(auth): adopt fsd-lite layout`.

### Task 3: clinical_context
- Move: `ContextForm.tsx` -> `components/`
- Create: `types.ts` (extract `ClinicalContextRow`).
- Update consumers (encounter detail).
- Commit: `refactor(clinical_context): adopt fsd-lite layout`.

### Task 4: consent
- Move: `ConsentPanel.tsx` -> `components/`
- Create: `types.ts`.
- Update consumers (patient detail).
- Commit: `refactor(consent): adopt fsd-lite layout`.

### Task 5: dashboard
- Move: `DashboardPage.tsx` -> `pages/`
- Move: `KpiCard.tsx`, `QuickActions.tsx`, `RecentEncountersList.tsx` -> `components/`
- Create: `types.ts` (extract `RecentEncounter`, `DashboardStats`).
- Update consumers (App.tsx).
- Commit: `refactor(dashboard): adopt fsd-lite layout`.

### Task 6: ecg_study
- Move: `EcgStudyList.tsx`, `EcgUploadForm.tsx` -> `components/`
- Move: `EcgStudyList.test.tsx`, `EcgUploadForm.test.tsx` -> `__tests__/`
- Create: `types.ts` (extract `EcgStudy`, quality enums).
- Update consumers (encounter detail).
- Commit: `refactor(ecg_study): adopt fsd-lite layout`.

### Task 7: encounter
- Move: `Detail.tsx`, `CreateForm.tsx` -> `pages/`
- Create: `types.ts` (extract `Encounter`, `EncounterCreateValues`).
- Update consumers (App.tsx routes).
- Commit: `refactor(encounter): adopt fsd-lite layout`.

### Task 8: patient
- Move: `PatientList.tsx`, `PatientDetail.tsx` -> `pages/`
- Move: `DedupDialog.tsx`, `DeleteDialog.tsx`, `IdentitySidebar.tsx`, `RegisterForm.tsx` -> `components/`
- Move: `RegisterForm.test.tsx` -> `__tests__/`
- Create: `types.ts` (extract patient shapes).
- Update consumers (App.tsx, search results).
- Commit: `refactor(patient): adopt fsd-lite layout`.

### Task 9: patient_history
- Move: `HistoryPanel.tsx` -> `components/`
- Create: `types.ts`.
- Update consumers (patient detail).
- Commit: `refactor(patient_history): adopt fsd-lite layout`.

### Task 10: search
- Move: `GlobalSearch.tsx`, `GlobalSearchTrigger.tsx`, `SearchResultList.tsx` -> `components/`
- Create: `types.ts` (extract `PatientHit`, `EncounterHit`, `SearchResults`).
- Keep `hooks.ts` at root (pure utility hooks, not React Query).
- Update consumers (Header).
- Commit: `refactor(search): adopt fsd-lite layout`.

### Task 11: vital_signs
- Move: `VitalsPanel.tsx`, `MiniCard.tsx` -> `components/`
- Move: `ranges.test.ts` -> `__tests__/`
- Create: `types.ts` (extract `VitalRow`, `VitalsInput`).
- Update consumers (encounter detail).
- Commit: `refactor(vital_signs): adopt fsd-lite layout`.

### Task 12: Final gate + PR
- Run `npm run typecheck && npm run lint && npm run test -- --run && npm run build`.
- Run `python scripts/check_file_size.py`.
- Push branch `refactor/fsd-features`.
- Open PR titled `refactor(frontend): apply fsd-lite layout to all features`.

---

## Per-Task Step Pattern

Each feature task follows the same five steps:

1. **Extract `types.ts`**: Read existing `api.ts` (and any component-local shapes). Move pure type/interface definitions into a new `types.ts`. Re-export from `api.ts` if other consumers still expect them there.
2. **`git mv` files into subfolders**: For each component/test file, run `git mv frontend/src/features/<feature>/<File>.tsx frontend/src/features/<feature>/<subfolder>/<File>.tsx`. This preserves git history.
3. **Update imports inside the moved files**: Relative `./api` becomes `../api`, `./schemas` becomes `../schemas`, etc.
4. **Update consumers**: Use `grep` to find `from "@/features/<feature>/<File>"` and update to the new path.
5. **Verify**: `npm run typecheck` must pass before committing the task.

---

## Acceptance Criteria

- AC-1: Every feature folder uses `components/`, `pages/`, `__tests__/` (where applicable).
- AC-2: No `.tsx` lives at a feature root.
- AC-3: Each feature exposes `types.ts`.
- AC-4: All imports resolve.
- AC-5: typecheck + lint + test + build pass.
- AC-6: file-size guard exits 0.
- AC-7: No behavioural change.
