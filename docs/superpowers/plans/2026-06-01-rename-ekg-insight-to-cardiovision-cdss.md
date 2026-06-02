# Rename EKG-Insight → CardioVision-CDSS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the application brand from "EKG-Insight" to "CardioVision-CDSS" across all frontend source code, config files, and the header description.

**Architecture:** Pure string replacement — no logic, API, database, or styling changes. Touches 9 files: 6 TSX components, 1 JSON config, 2 HTML entry points. Post-edit verification via `npm install` (regenerate lockfile) + `npm run build` + `npm run lint` + `npm run typecheck`.

**Tech Stack:** React 18, TypeScript, Vite 5, Tailwind CSS 3, shadcn/ui

---

## File Structure

| File | Responsibility | Change |
|------|---------------|--------|
| `frontend/src/components/layout/Header.tsx` | Top header bar with brand wordmark + description | Wordmark line 30; description line 34 |
| `frontend/src/components/layout/AppShell.tsx` | App shell with mobile Sheet sidebar brand | Wordmark line 70 |
| `frontend/src/components/layout/FocusShell.tsx` | Sidebar-less focus layout for analysis page | Wordmark line 36 |
| `frontend/src/routes/login.tsx` | Login page mobile brand block | Wordmark line 31 |
| `frontend/src/features/auth/components/LoginBrandPanel.tsx` | Login page desktop brand panel | Wordmark line 26 |
| `frontend/src/components/brand/EcgSweep.tsx` | ECG wave motif SVG component | aria-label line 36 |
| `frontend/package.json` | NPM package metadata | Package name line 2 |
| `frontend/index.html` | Vite entry HTML | Page title line 6 |
| `backend/app/static/index.html` | Backend static fallback HTML | Page title line 6 |

---

## Git Flow & PR Strategy

### Branch

| Item | Value |
|------|-------|
| Branch name | `refactor/ui/rename-cardiovision-cdss` |
| Branch from | `main` (always up-to-date) |
| Naming convention | `<type>/<area>/<short-kebab>` per `docs/operations/git-workflow.md` |

### Commit

| Item | Value |
|------|-------|
| Type | `refactor` (no behavior change) |
| Scope | `ui` |
| Subject | `rename EKG-Insight to CardioVision-CDSS` |
| Full message | `refactor(ui): rename EKG-Insight to CardioVision-CDSS` |
| Convention | Conventional Commits per `docs/operations/commit-convention.md` |
| Version bump | None (`refactor` type = no version bump per release-please) |

### PR

| Item | Value |
|------|-------|
| Title | `refactor(ui): rename EKG-Insight to CardioVision-CDSS` |
| Labels | `type/refactor`, `area/ui`, `size/s` |
| Size | `size/s` (< 100 LOC changed) |
| Cooldown | **Same-day merge** (size/s <100 LOC, zero logic change) |
| Merge strategy | Squash merge (1 PR = 1 commit on main) |
| CI gates | secret-scan, backend (lint/type/test), frontend (lint/type/test/build) |
| Clinical safety gate | N/A (no clinical output change) |

### PR Description Template

```markdown
## What

Rename application brand from "EKG-Insight" to "CardioVision-CDSS" across
all frontend source code, config files, and the header description.

## Why

User requested brand rename to better reflect the application's identity as
a clinical decision support system for cardiovascular screening.

## Changes

- 6 TSX components: wordmark string replacement
- 1 package.json: package name `ekg-insight-frontend` → `cardio-vision-cdss-frontend`
- 2 HTML entry points: page title update
- Header description: "CDSS demo" → "Clinical Decision Support System" (bilingual)

## Scope

- Frontend + config only (9 files)
- Documentation (README, CONTRIBUTING, SECURITY, docs/) excluded — follow-up PR
- No logic, API, database, or styling changes

## Verification

- [ ] `npm run typecheck` — pass
- [ ] `npm run lint` — pass
- [ ] `npm run test -- --run` — pass
- [ ] `npm run build` — pass
- [ ] `rg "EKG-Insight" frontend/src/` — no matches
```

### Execution Sequence

```
1.  git switch main && git pull
2.  git switch -c refactor/ui/rename-cardiovision-cdss
3.  Edit 9 files (Tasks 1–8)
4.  npm install di frontend/ (regenerate lockfile)
5.  Full gate: npm run typecheck && npm run lint && npm run test -- --run && npm run build
6.  git add + git commit (conventional commit)
7.  git push -u origin refactor/ui/rename-cardiovision-cdss
8.  Open PR (auto-load template)
9.  CI runs → all green
10. Self-review (same-day, size/s)
11. Squash merge to main
12. Delete branch (local + remote)
```

---

## Task 1: Rename wordmark in Header component

**Files:**
- Modify: `frontend/src/components/layout/Header.tsx:30,34`

- [ ] **Step 1: Update brand wordmark**

In `frontend/src/components/layout/Header.tsx`, replace the wordmark on line 30:

```diff
- <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
+ <span className="text-base font-semibold tracking-tight">CardioVision-CDSS</span>
```

- [ ] **Step 2: Update header description**

In the same file, replace the description on line 34:

```diff
- {t("CDSS demo", "CDSS demo")}
+ {t("Sistem Pendukung Keputusan Klinis", "Clinical Decision Support System")}
```

- [ ] **Step 3: Verify TypeScript compiles**

Run: `npm run typecheck` in `frontend/`
Expected: No errors

---

## Task 2: Rename wordmark in AppShell (mobile sheet)

**Files:**
- Modify: `frontend/src/components/layout/AppShell.tsx:70`

- [ ] **Step 1: Update mobile sheet brand**

In `frontend/src/components/layout/AppShell.tsx`, replace the wordmark on line 70:

```diff
- <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
+ <span className="text-base font-semibold tracking-tight">CardioVision-CDSS</span>
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `npm run typecheck` in `frontend/`
Expected: No errors

---

## Task 3: Rename wordmark in FocusShell

**Files:**
- Modify: `frontend/src/components/layout/FocusShell.tsx:36`

- [ ] **Step 1: Update focus shell brand**

In `frontend/src/components/layout/FocusShell.tsx`, replace the wordmark on line 36:

```diff
- <span className="text-sm font-semibold tracking-tight">EKG-Insight</span>
+ <span className="text-sm font-semibold tracking-tight">CardioVision-CDSS</span>
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `npm run typecheck` in `frontend/`
Expected: No errors

---

## Task 4: Rename wordmark in Login page

**Files:**
- Modify: `frontend/src/routes/login.tsx:31`

- [ ] **Step 1: Update mobile brand block wordmark**

In `frontend/src/routes/login.tsx`, replace the wordmark on line 31:

```diff
- <h1 className="text-lg font-semibold tracking-tight">EKG-Insight</h1>
+ <h1 className="text-lg font-semibold tracking-tight">CardioVision-CDSS</h1>
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `npm run typecheck` in `frontend/`
Expected: No errors

---

## Task 5: Rename wordmark in LoginBrandPanel

**Files:**
- Modify: `frontend/src/features/auth/components/LoginBrandPanel.tsx:26`

- [ ] **Step 1: Update desktop brand panel wordmark**

In `frontend/src/features/auth/components/LoginBrandPanel.tsx`, replace the wordmark on line 26:

```diff
- <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
+ <span className="text-base font-semibold tracking-tight">CardioVision-CDSS</span>
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `npm run typecheck` in `frontend/`
Expected: No errors

---

## Task 6: Update aria-label in EcgSweep component

**Files:**
- Modify: `frontend/src/components/brand/EcgSweep.tsx:36`

- [ ] **Step 1: Update aria-label**

In `frontend/src/components/brand/EcgSweep.tsx`, replace the aria-label on line 36:

```diff
- aria-label="EKG-Insight wave motif"
+ aria-label="CardioVision-CDSS wave motif"
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `npm run typecheck` in `frontend/`
Expected: No errors

---

## Task 7: Update package name

**Files:**
- Modify: `frontend/package.json:2`

- [ ] **Step 1: Update package name**

In `frontend/package.json`, replace the name on line 2:

```diff
- "name": "ekg-insight-frontend",
+ "name": "cardio-vision-cdss-frontend",
```

- [ ] **Step 2: Regenerate package-lock.json**

Run: `npm install` in `frontend/`
Expected: `package-lock.json` regenerated with new name; no new dependencies added

---

## Task 8: Update page titles

**Files:**
- Modify: `frontend/index.html:6`
- Modify: `backend/app/static/index.html:6`

- [ ] **Step 1: Update frontend page title**

In `frontend/index.html`, replace the title on line 6:

```diff
- <title>EKG-Insight CDSS</title>
+ <title>CardioVision-CDSS</title>
```

- [ ] **Step 2: Update backend static page title**

In `backend/app/static/index.html`, replace the title on line 6:

```diff
- <title>EKG-Insight CDSS</title>
+ <title>CardioVision-CDSS</title>
```

---

## Task 9: Final verification and commit

- [ ] **Step 1: Run full frontend gate**

Run in `frontend/`:
```bash
npm run typecheck && npm run lint && npm run test -- --run && npm run build
```
Expected: All pass with zero errors

- [ ] **Step 2: Verify no remaining "EKG-Insight" references in source**

Run in `frontend/src/`:
```bash
rg "EKG-Insight" src/
```
Expected: No matches

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/layout/Header.tsx \
        frontend/src/components/layout/AppShell.tsx \
        frontend/src/components/layout/FocusShell.tsx \
        frontend/src/routes/login.tsx \
        frontend/src/features/auth/components/LoginBrandPanel.tsx \
        frontend/src/components/brand/EcgSweep.tsx \
        frontend/package.json \
        frontend/package-lock.json \
        frontend/index.html \
        backend/app/static/index.html
git commit -m "refactor(brand): rename EKG-Insight to CardioVision-CDSS" -m "" -m "Update wordmark in Header, AppShell, FocusShell, Login, LoginBrandPanel." -m "Update header description from 'CDSS demo' to 'Clinical Decision" -m "Support System'. Update package name and page titles."
```

---

## Execution Notes

- **Zero risk:** Pure string replacements, no logic changes
- **No API/database changes:** Backend only touched for static HTML title
- **i18n:** The Indonesian translation "Sistem Pendukung Keputusan Klinis" already exists in `login.tsx` and `LoginBrandPanel.tsx`; reusing the same pattern in Header.tsx
- **Documentation:** README, CONTRIBUTING, SECURITY, docs/ are intentionally excluded per user decision — can be updated in a follow-up
