# Clinical Split-Screen Login Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the centered-card login with a split-screen layout that
reads as a clinical instrument front door (left: dark petrol brand panel
with the EcgSweep motif; right: clean white form panel with the existing
`LoginForm`), while preserving the bilingual UI and the existing JWT auth
flow.

**Architecture:** Pure Tailwind grid (`lg:grid lg:grid-cols-2`) with a
component split — `LoginRoute` owns the layout and the right panel; a new
`LoginBrandPanel.tsx` owns the dark left panel content. The existing
`LoginForm` keeps its responsibilities; only its visual chrome (Card wrap,
button width) changes.

**Tech Stack:** React, React Router, Tailwind CSS, Zustand i18n store,
existing `EcgSweep` brand SVG, existing `LanguageToggle` component.

---

### Task 1: Brand panel component (left side)

**Files:**
- Create: `frontend/src/features/auth/LoginBrandPanel.tsx`

- [ ] **Step 1: Write the panel component**

```tsx
// frontend/src/features/auth/LoginBrandPanel.tsx
import { ShieldCheck } from "lucide-react";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { useI18nStore } from "@/lib/i18n/store";

/**
 * Dark petrol panel rendered on the left half of the login screen at lg+.
 * Pure presentation: brand wordmark, sub-headline, trust line + disclaimer,
 * and an oversized EcgSweep watermark behind everything.
 */
export function LoginBrandPanel() {
  const t = useI18nStore((s) => s.t);

  return (
    <aside
      aria-hidden="false"
      className="relative hidden flex-col justify-between overflow-hidden bg-petrol-900 px-10 py-10 text-white lg:flex"
    >
      <EcgSweep
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white/[0.06]"
        width={900}
        height={240}
        thickness={3}
      />

      <header className="relative z-10 flex items-center gap-2">
        <EcgSweep className="text-white" width={36} height={18} thickness={2.5} />
        <span className="text-base font-semibold tracking-tight">EKG-Insight</span>
      </header>

      <div className="relative z-10 flex flex-col gap-4">
        <h1 className="text-3xl font-semibold tracking-tight text-white">
          {t(
            "Sistem Pendukung Keputusan Klinis",
            "Clinical Decision Support System",
          )}
        </h1>
        <p className="max-w-md text-sm leading-relaxed text-white/75">
          {t(
            "Analisis EKG berbasis AI untuk membantu klinisi mengambil keputusan triage yang lebih cepat dan terstandar.",
            "AI-assisted ECG analysis to help clinicians make faster, more standardized triage decisions.",
          )}
        </p>
      </div>

      <footer className="relative z-10 flex items-start gap-2 text-xs text-white/60">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <span>
          {t(
            "Akses aman untuk tenaga kesehatan. Hasil AI bersifat membantu — keputusan klinis tetap di tangan dokter.",
            "Secure access for healthcare professionals. AI output is advisory — clinical decisions remain with the clinician.",
          )}
        </span>
      </footer>
    </aside>
  );
}
```

- [ ] **Step 2: Format + lint**

```bash
npx prettier --write src/features/auth/LoginBrandPanel.tsx
npm run lint
```

Expected: prettier silent, lint exits 0.

---

### Task 2: Form chrome polish (LoginForm)

**Files:**
- Modify: `frontend/src/features/auth/LoginForm.tsx`

- [ ] **Step 1: Submit button stays `w-full` (already done in pass 1)**

No edit required — the button already has `className="w-full cursor-pointer"`.
Confirmed by reading the current file.

- [ ] **Step 2: Verify the existing tests still pass**

```bash
npm run test -- --run src/features/auth/LoginForm.test.tsx
```

Expected: 3/3 pass.

---

### Task 3: Split-screen LoginRoute

**Files:**
- Modify: `frontend/src/routes/login.tsx`

- [ ] **Step 1: Replace the route to use the split layout**

```tsx
// frontend/src/routes/login.tsx
import { useNavigate } from "react-router-dom";

import { EcgSweep } from "@/components/brand/EcgSweep";
import { LanguageToggle } from "@/components/layout/LanguageToggle";
import { LoginBrandPanel } from "@/features/auth/LoginBrandPanel";
import { LoginForm } from "@/features/auth/LoginForm";
import { useI18nStore } from "@/lib/i18n/store";

export function LoginRoute() {
  const navigate = useNavigate();
  const t = useI18nStore((s) => s.t);

  return (
    <main className="grid min-h-screen bg-paper lg:grid-cols-2">
      <LoginBrandPanel />

      <section className="relative flex items-center justify-center px-6 py-10">
        <div className="absolute right-4 top-4 z-20">
          <LanguageToggle />
        </div>

        <div className="w-full max-w-sm">
          <div className="mb-6 flex flex-col items-center gap-2 text-center lg:hidden">
            <EcgSweep
              className="text-primary"
              width={36}
              height={18}
              thickness={2.5}
            />
            <h1 className="text-lg font-semibold tracking-tight">EKG-Insight</h1>
            <p className="text-xs text-muted-foreground">
              {t(
                "Sistem Pendukung Keputusan Klinis",
                "Clinical Decision Support System",
              )}
            </p>
          </div>

          <div className="mb-5 hidden flex-col gap-1 lg:flex">
            <h2 className="text-xl font-semibold tracking-tight">
              {t("Selamat datang", "Welcome back")}
            </h2>
            <p className="text-sm text-muted-foreground">
              {t(
                "Masuk dengan akun klinik Anda.",
                "Sign in with your facility account.",
              )}
            </p>
          </div>

          <LoginForm onSuccess={() => navigate("/dashboard")} />
        </div>
      </section>
    </main>
  );
}
```

- [ ] **Step 2: Format + typecheck + build**

```bash
npx prettier --write src/routes/login.tsx
npm run typecheck
npm run build
```

Expected: all silent / built in N s.

- [ ] **Step 3: Run full frontend test + lint gate**

```bash
npm run lint
npm run test -- --run
```

Expected: 0 lint errors (warnings allowed), 33/33 tests pass.

- [ ] **Step 4: File-size guard**

```bash
backend/.venv/Scripts/python.exe scripts/check_file_size.py
```

Expected: EXIT 0.

---

### Task 4: Commit + push

**Files:**
- Modify: existing branch `feat/saas-ui-polish`

- [ ] **Step 1: Stage + commit**

```bash
git add docs/superpowers/specs/2026-06-01-clinical-split-login-design.md \
        docs/superpowers/plans/2026-06-01-clinical-split-login.md \
        frontend/src/features/auth/LoginBrandPanel.tsx \
        frontend/src/routes/login.tsx
git commit -m "feat(ui): clinical split-screen login layout" \
  -m "Left dark petrol panel with the EcgSweep watermark hosts the brand" \
  -m "and a clinical disclaimer; right white panel keeps the existing" \
  -m "LoginForm without a Card wrap. Below lg the dark panel collapses" \
  -m "and the form recenters on a clean white background. All copy" \
  -m "bilingual via useI18nStore."
```

Expected: commit hook autopasses (lint-staged ruff/eslint).

- [ ] **Step 2: Push (existing PR auto-updates)**

```bash
git push
```

Expected: pushes to `feat/saas-ui-polish`; PR #17 picks up the new commit.
