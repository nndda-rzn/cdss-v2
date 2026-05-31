# Sprint 2A: Clinical Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the clinical-context layer (Patient, Encounter, ClinicalContext, VitalSigns, Consent, PatientHistory) so a clinician can register a patient, capture encounter context and vitals, and have all PHI encrypted at rest with audit logging — before any ECG image enters the system.

**Architecture:** Vertical slice with encryption-first (Approach C). Phase S1 validates the full stack (ORM -> service -> API -> UI -> audit) on the simplest entity (Patient register), proving encryption + PHIAccessLog wiring work end-to-end before building S2-S6. Each phase is a self-contained domain that adds one Alembic migration, one or more service files, one API blueprint, and one or more React components.

**Tech Stack:** Flask, SQLAlchemy 2.0 (typed), Alembic, Pydantic v2, Flask-JWT-Extended, bcrypt, Fernet (encryption), HMAC-SHA256 (hashing), React 18, Vite, TypeScript, TanStack Query 5 (already installed in Sprint 1), Zustand 4, Tailwind CSS 3, shadcn/ui, react-hook-form 7, zod, Playwright (e2e).

---

## Design Summary

### Scope

**In scope (Sprint 2A):**
- 6 new ORM models: Patient, PatientHistory, Consent, Encounter, ClinicalContext, VitalSigns
- 6 Alembic migrations (one per phase S1-S6)
- 18 new backend service files across 6 domains
- 16 new API endpoints
- 10+ new React components (Patient register/search/detail, Encounter create/detail, ConsentForm, ContextForm, VitalsForm)
- PHIAccessLog first production caller (3 log rows per patient detail view)
- shadcn/ui + react-hook-form + zod frontend stack established
- Tailwind CSS configured (Sprint 1 had it in devDependencies but no config)
- Playwright e2e introduced (5 critical flows)
- ADR-0015: dedup strategy documented

**Out of scope (explicit):**
- ECGStudy + image upload + image quality (Sprint 2B)
- AI inference (Sprint 3), HiResCAM (Sprint 4)
- Recommendation, Disposition, Referral (Sprint 5)
- PDF report (Sprint 6), Research dashboard (Sprint 7)
- Auto-close encounter (Sprint 5)
- Research consent flow (Sprint 7)
- i18n library (Sprint 5/6)

### Acceptance Criteria (10 ACs)

| # | Kriteria |
| --- | --- |
| AC-1 | Migration alembic upgrade head from Sprint 1 baseline adds 6 tables; alembic downgrade -1 succeeds without data loss for Sprint 1 tables |
| AC-2 | Patient register endpoint accepts full form, stores T1 fields encrypted (verifiable: dump SQLite blob field, no plaintext name/phone/address) |
| AC-3 | Patient list endpoint returns T1 fields masked; PHIAccessLog NOT written for list |
| AC-4 | Patient detail endpoint returns plaintext T1; PHIAccessLog written with user_id, patient_id, accessed_field, ip, timestamp (3 rows for name/phone/address) |
| AC-5 | NIK optional: register without NIK succeeds; register with duplicate NIK at same facility returns 409 with code PATIENT_NIK_DUPLICATE |
| AC-6 | MRN auto-generated format MRN-{FACILITY_CODE}-{6-digit zero-padded}, unique per facility |
| AC-7 | Encounter create + close end-to-end; close idempotent; ClinicalContext 1:1 and VitalSigns M:1 per schema |
| AC-8 | Consent capture: data_use at register (status given), ai_analysis at first encounter (separate row), research opt-in (separate, default pending) |
| AC-9 | RBAC enforced: clinician/nurse can CRU patient, admin can RUD; researcher/expert_reviewer get 403 for Patient ops; nurse gets 403 for Patient delete |
| AC-10 | Soft delete admin: DELETE /patients/{id} sets deleted_at, audit log with reason mandatory; all read endpoints filter deleted_at IS NULL by default |

### Key Decisions

| Aspek | Keputusan |
| --- | --- |
| NIK | Optional, partial unique per facility (UNIQUE WHERE nik_hash IS NOT NULL) |
| MRN | Auto-gen MRN-{FACILITY_CODE}-{6-digit}, unique per facility |
| PHI reveal | Masked in list, plaintext in detail, 1 PHIAccessLog per T1 field (3 rows for name/phone/address) |
| Encounter close | Manual only (PATCH .../close idempotent), auto-close deferred to Sprint 5 |
| VitalSigns | M:1, latest-wins for decision engine (Sprint 5) |
| Consent | Granular per type, progressive capture |
| Delete | Admin-only soft-delete Patient with mandatory reason; no delete Encounter |
| Dedup | Limited to dob+gender index then decrypt-in-memory fuzzy match (ADR-0015) |
| Migration | Per phase (002 Patient through 007 VitalSigns) |

### File Structure Map

```
backend/app/
  api/
    patients.py                        (NEW)
    patient_history.py                 (NEW)
    consent.py                         (NEW)
    encounters.py                      (NEW)
    clinical_context.py                (NEW)
    vital_signs.py                     (NEW)
  schemas/
    patient.py                         (NEW)
    patient_history.py                 (NEW)
    consent.py                         (NEW)
    encounter.py                       (NEW)
    clinical_context.py                (NEW)
    vital_signs.py                     (NEW)
  services/
    audit/phi_access_writer.py         (NEW)
    patient/register.py                (NEW)
    patient/search.py                  (NEW)
    patient/reveal.py                  (NEW)
    patient/mask.py                    (NEW)
    patient/dedup.py                   (NEW)
    patient/delete.py                  (NEW)
    patient_history/writer.py          (NEW)
    consent/capture.py                 (NEW)
    consent/revoke.py                  (NEW)
    consent/query.py                   (NEW)
    encounter/create.py                (NEW)
    encounter/close.py                 (NEW)
    encounter/query.py                 (NEW)
    clinical_context/writer.py         (NEW)
    vital_signs/capture.py             (NEW)
    vital_signs/query.py               (NEW)
  db/
    models/patient.py                  (NEW)
    models/patient_history.py          (NEW)
    models/consent.py                  (NEW)
    models/encounter.py                (NEW)
    models/clinical_context.py         (NEW)
    models/vital_signs.py              (NEW)
    mrn_generator.py                   (NEW)
  core/rbac/patient_policy.py          (NEW)
  core/phi/masking.py                  (NEW)

frontend/src/
  features/patient/
    api.ts, hooks.ts, schemas.ts       (NEW)
    RegisterForm.tsx                   (NEW)
    SearchForm.tsx                     (NEW)
    PatientList.tsx                    (NEW)
    PatientDetail.tsx                  (NEW)
    DeleteDialog.tsx                   (NEW)
  features/encounter/
    api.ts, hooks.ts, schemas.ts       (NEW)
    CreateForm.tsx                     (NEW)
    Detail.tsx                         (NEW)
    CloseDialog.tsx                    (NEW)
  features/clinical_context/
    api.ts, hooks.ts, schemas.ts       (NEW)
    ContextForm.tsx                    (NEW)
  features/vital_signs/
    api.ts, hooks.ts, schemas.ts       (NEW)
    VitalsForm.tsx                     (NEW)
    VitalsList.tsx                     (NEW)
  features/consent/
    api.ts, hooks.ts, schemas.ts       (NEW)
    ConsentForm.tsx                    (NEW)
  features/patient_history/
    api.ts, hooks.ts, schemas.ts       (NEW)
    HistoryForm.tsx                    (NEW)
    HistoryList.tsx                    (NEW)
  components/ui/                       (NEW - shadcn primitives)
  components/composed/                 (NEW - DatePickerField, NIKInput, etc.)
  components/layout/                   (NEW - sidebar nav extension)
  routes/PatientsRoute.tsx             (NEW)
  routes/PatientRegisterRoute.tsx      (NEW)
  routes/PatientDetailRoute.tsx        (NEW)
  routes/EncounterCreateRoute.tsx      (NEW)
  routes/EncounterDetailRoute.tsx      (NEW)

tests/
  e2e/playwright.config.ts             (NEW)
  e2e/fixtures/seed.ts                 (NEW)
  e2e/specs/                           (NEW - 5 spec files)
```

### Backend Component Data Flow

```
[Patient Register Form (UI)]
  -> POST /api/patients
  -> patients.py blueprint
  -> services/patient/register.py
     -> dedup_check (services/patient/dedup.py)
     -> if duplicate suggestion: return 200 + suggestions[]
     -> else: encrypt T1, MRN auto-gen, INSERT
     -> services/audit/writer.py (action="patient_register")
     -> services/consent/capture.py (data_use, given)
  -> response PatientOut

[Patient Detail (UI)]
  -> GET /api/patients/{id}
  -> patients.py blueprint
  -> services/patient/reveal.py
     -> SELECT patient (decrypt T1)
     -> services/audit/phi_access_writer.py (each T1 field)
  -> response PatientOut (plaintext)

[Encounter Create (UI)]
  -> POST /api/encounters
  -> encounters.py blueprint
  -> services/encounter/create.py
     -> verify patient exists + not deleted
     -> verify consent.data_use given
     -> INSERT encounter (status=open)
  -> response EncounterOut
```

---

## Phase H0 - Frontend Foundation Upgrade

### Task H0-1: Configure Tailwind CSS

Sprint 1 installed Tailwind CSS as a devDependency but never created config files or a global CSS entry. This task wires it up.

**Files:**
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/src/index.css`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Create tailwind.config.js**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```

- [ ] **Step 2: Create postcss.config.js**

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

- [ ] **Step 3: Create src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 4: Import index.css in main.tsx**

Add `import "./index.css";` as the first import in `frontend/src/main.tsx`:

```tsx
import "./index.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
```

- [ ] **Step 5: Verify Tailwind works**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no CSS errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/tailwind.config.js frontend/postcss.config.js frontend/src/index.css frontend/src/main.tsx
git commit -m "feat(ui): configure Tailwind CSS with PostCSS and global entry"
```

---

### Task H0-2: Initialize shadcn/ui and Add Primitives

**Files:**
- Create: `frontend/components.json` (shadcn config)
- Create: `frontend/src/components/ui/` (shadcn primitives)
- Modify: `frontend/tsconfig.json` (shadcn may add path aliases)
- Modify: `frontend/src/index.css` (shadcn CSS variables)

- [ ] **Step 1: Initialize shadcn/ui**

Run from `frontend/`:
```bash
npx shadcn@latest init --defaults --force
```

This creates `components.json` and modifies `tsconfig.json` and `src/index.css` (adds CSS variables for theming).

- [ ] **Step 2: Add required primitives**

Run from `frontend/`:
```bash
npx shadcn@latest add button input label form select calendar card dialog sheet sonner skeleton alert badge
```

This creates files under `src/components/ui/`.

- [ ] **Step 3: Verify build**

Run: `npm run build`
Expected: Build succeeds.

- [ ] **Step 4: Verify tests still pass**

Run: `npm run test`
Expected: All 10 existing tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/components.json frontend/src/components/ui/ frontend/tsconfig.json frontend/src/index.css
git commit -m "feat(ui): initialize shadcn/ui with 11 primitives"
```

---

### Task H0-3: Install react-hook-form + zod + date-fns

Note: TanStack Query 5 and QueryClientProvider are already set up from Sprint 1 (`main.tsx` and `package.json`). No action needed.

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install dependencies**

Run from `frontend/`:
```bash
npm install react-hook-form @hookform/resolvers zod date-fns react-day-picker
```

- [ ] **Step 2: Verify build**

Run: `npm run build`
Expected: Build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat(ui): add react-hook-form, zod, date-fns, react-day-picker"
```

---

### Task H0-4: Refactor LoginForm to shadcn Form + zod

This validates the entire H0 stack (shadcn Form + react-hook-form + zod) on the existing Sprint 1 LoginForm before building new forms.

**Files:**
- Modify: `frontend/src/features/auth/LoginForm.tsx`
- Modify: `frontend/src/features/auth/LoginForm.test.tsx`

- [ ] **Step 1: Write the failing test for zod validation**

Add to `frontend/src/features/auth/LoginForm.test.tsx`:

```tsx
it("shows validation error for invalid email", async () => {
  const user = userEvent.setup();
  render(<LoginForm onSuccess={vi.fn()} />);
  await user.type(screen.getByLabelText(/email/i), "not-an-email");
  await user.type(screen.getByLabelText(/password/i), "pass");
  await user.click(screen.getByRole("button", { name: /masuk/i }));
  expect(await screen.findByText(/email tidak valid/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm run test -- --run`
Expected: FAIL (no zod schema yet, no shadcn Form)

- [ ] **Step 3: Rewrite LoginForm with shadcn Form + zod**

```tsx
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { login } from "./api";
import { useState } from "react";

const LoginSchema = z.object({
  email: z.string().email("Email tidak valid"),
  password: z.string().min(1, "Password wajib diisi"),
});

type LoginValues = z.infer<typeof LoginSchema>;

export function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const [serverError, setServerError] = useState<string | null>(null);
  const form = useForm<LoginValues>({
    resolver: zodResolver(LoginSchema),
    defaultValues: { email: "", password: "" },
  });

  async function onSubmit(values: LoginValues) {
    setServerError(null);
    try {
      await login(values);
      onSuccess();
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {serverError && (
          <p role="alert" className="text-sm text-destructive">
            {serverError}
          </p>
        )}
        <Button type="submit" disabled={form.formState.isSubmitting}>
          Masuk
        </Button>
      </form>
    </Form>
  );
}
```

- [ ] **Step 4: Update existing tests for new markup**

The existing tests use `getByLabelText` and `getByRole("button")`. shadcn Form renders the same label/button semantics, but the error display changes from `<p role="alert">` to shadcn `FormMessage`. Update the existing `test_login_bad_password` test to check for the server error message instead of the role="alert" pattern, since the markup changed. Run existing tests and fix any that break due to markup changes.

- [ ] **Step 5: Run all tests**

Run: `cd frontend && npm run test -- --run`
Expected: All tests pass (existing + new validation test).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/auth/LoginForm.tsx frontend/src/features/auth/LoginForm.test.tsx
git commit -m "refactor(ui): rewrite LoginForm with shadcn Form + zod validation"
```

---

### Task H0-5: Add App Shell with Sidebar Navigation

**Files:**
- Create: `frontend/src/components/layout/AppShell.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create AppShell component**

```tsx
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/patients", label: "Pasien" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const clear = useAuthStore((s) => s.clear);

  return (
    <div className="flex h-screen">
      <aside className="w-56 border-r bg-muted/40 p-4 flex flex-col gap-2">
        <h2 className="text-lg font-semibold mb-4">EKG-Insight</h2>
        {navItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={cn(
              "rounded-md px-3 py-2 text-sm",
              location.pathname.startsWith(item.to)
                ? "bg-primary text-primary-foreground"
                : "hover:bg-accent"
            )}
          >
            {item.label}
          </Link>
        ))}
        <div className="mt-auto">
          <Button variant="outline" className="w-full" onClick={() => clear()}>
            Keluar
          </Button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}
```

- [ ] **Step 2: Wrap ProtectedRoute children with AppShell**

Modify `frontend/src/App.tsx`:

```tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { LoginRoute } from "@/routes/login";
import { ProtectedRoute } from "@/features/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell>{null}</AppShell>}>
            <Route path="/dashboard" element={<div>Dashboard (Sprint 2+)</div>} />
            <Route path="/patients" element={<div>Pasien (Sprint 2A)</div>} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
```

Note: The AppShell needs to render an `<Outlet />` from react-router-dom for nested routes to work. Adjust the component to use `<Outlet />` instead of `{children}`.

- [ ] **Step 3: Verify build + tests**

Run: `npm run build && npm run test -- --run`
Expected: Build succeeds, all tests pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/AppShell.tsx frontend/src/App.tsx
git commit -m "feat(ui): add App shell with sidebar navigation"
```

---

## Phase S1 - Patient Register Vertical Slice

This is the most important phase. It validates the entire encryption + PHIAccessLog + MRN + dedup stack on the simplest entity before building S2-S6. Every bug found here prevents compound bugs later.

### Task S1-1: Patient ORM Model + Migration 002

**Files:**
- Create: `backend/app/db/models/patient.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/002_patient.py` (generated by alembic)

- [ ] **Step 1: Write the failing test for Patient model**

Create `backend/tests/unit/db/models/test_patient.py` with tests for:
- T1 fields stored as encrypted bytes (no plaintext in raw SQLite blob)
- NIK hash deterministic (same input = same hash, duplicate rejected)
- NIK nullable allows multiple patients without NIK

- [ ] **Step 2: Run test to verify it fails**

Run: ``cd backend && pytest tests/unit/db/models/test_patient.py -v``
Expected: FAIL (Patient model does not exist)

- [ ] **Step 3: Create Patient ORM model**

Create `backend/app/db/models/patient.py` with UUID PK, facility_id FK, mrn, nik_hash (HashedString, nullable), nik_last4, name_encrypted (EncryptedString), dob, gender (enum male/female), phone_encrypted (EncryptedString, nullable), address_encrypted (EncryptedString, nullable), is_pseudonymized, deleted_at, created_at, updated_at. Table args: UniqueConstraint(facility_id, mrn), partial unique index on (facility_id, nik_hash) WHERE nik_hash IS NOT NULL, composite index on (dob, gender).

Follow existing model patterns: inherit from `Base`, use `Mapped[T]` typed columns, `EncryptedString` and `HashedString` from `app.db.types`. Use `datetime.now(datetime.UTC)` for defaults (match TimestampMixin pattern).

- [ ] **Step 4: Register model in __init__.py**

Add `from app.db.models.patient import Patient` and `"Patient"` to `__all__` in `backend/app/db/models/__init__.py`.

- [ ] **Step 5: Generate Alembic migration**

Run from `backend/`: ``alembic revision --autogenerate -m "add patient table"``

Review generated migration: Patient table with all columns, partial unique index uses `sqlite_where`, downgrade drops table.

- [ ] **Step 6: Run tests**

Run: ``cd backend && pytest tests/unit/db/models/test_patient.py -v``
Expected: All 3 tests PASS.

- [ ] **Step 7: Verify migration roundtrip**

Run: ``cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head``
Expected: No errors.

- [ ] **Step 8: Commit**

``git commit -m "feat(db): add Patient model with encrypted T1 fields and migration 002"``

---

### Task S1-2: MRN Generator

**Files:**
- Create: `backend/app/db/mrn_generator.py`
- Create: `backend/tests/unit/db/test_mrn_generator.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- MRN format `MRN-P1-000001` (zero-padded 6-digit)
- Sequence increments after insert
- Per-facility isolation (facility 1 and 2 get independent sequences)

- [ ] **Step 2: Run tests to verify they fail**

Run: ``cd backend && pytest tests/unit/db/test_mrn_generator.py -v``
Expected: FAIL

- [ ] **Step 3: Implement MRN generator**

`generate_mrn(session, facility_id, facility_code) -> str`: SELECT MAX(CAST(SUBSTR(mrn, -6) AS INT)) FROM patient WHERE facility_id = ?, then format `MRN-{code}-{next:06d}`. Handle empty table (start at 1). Raise MRN_GENERATION_EXHAUSTED if > 999999.

- [ ] **Step 4: Run tests**

Run: ``cd backend && pytest tests/unit/db/test_mrn_generator.py -v``
Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(db): add MRN auto-generator with per-facility sequence"``

---

### Task S1-3: PHIAccessLog Writer Service

**Files:**
- Create: `backend/app/services/audit/phi_access_writer.py`
- Create: `backend/tests/unit/services/audit/test_phi_access_writer.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `log_phi_access` writes row with correct user_id, patient_id, accessed_field, ip_address
- Multiple calls write multiple rows (one per field)

- [ ] **Step 2: Run tests to verify they fail**

Run: ``cd backend && pytest tests/unit/services/audit/test_phi_access_writer.py -v``
Expected: FAIL

- [ ] **Step 3: Implement phi_access_writer**

```python
def log_phi_access(session, *, user_id, patient_id, access_type="view",
                   purpose="treatment", accessed_field, ip_address=None):
```

Insert row into `PHIAccessLog`. Follow `writer.py` pattern (explicit session.add, return entry).

- [ ] **Step 4: Run tests**

Run: ``cd backend && pytest tests/unit/services/audit/test_phi_access_writer.py -v``
Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(audit): add PHIAccessLog writer service"``

---

### Task S1-4: Patient Masking Helpers

**Files:**
- Create: `backend/app/services/patient/mask.py`
- Create: `backend/tests/unit/services/patient/test_mask.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `mask_name("Budi Santoso")` returns `"B*** S******"`
- `mask_name("A")` returns `"A"` (single char stays)
- `mask_nik("3201123456780001")` returns `"************0001"`
- `mask_phone("0812345678")` returns `"******5678"` (last 4 visible)
- `mask_phone(None)` returns `None`

- [ ] **Step 2: Run tests to verify they fail**

Run: ``cd backend && pytest tests/unit/services/patient/test_mask.py -v``
Expected: FAIL

- [ ] **Step 3: Implement masking helpers**

Pure functions, no DB dependency. Each function: `mask_name(s: str|None) -> str|None`, etc. First char visible, rest replaced with `*`, space preserved as separator.

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add T1 field masking helpers"``

---

### Task S1-5: Patient Dedup Service

**Files:**
- Create: `backend/app/services/patient/dedup.py`
- Create: `backend/tests/unit/services/patient/test_dedup.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `find_potential_duplicates(session, facility_id, name, dob, gender)` returns matching patients by dob+gender, then fuzzy-matches name in-memory
- Returns empty list when no match
- Excludes deleted patients (deleted_at IS NOT NULL)

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement dedup service**

Query: `SELECT * FROM patient WHERE facility_id=? AND dob=? AND gender=? AND deleted_at IS NULL`. Decrypt name_encrypted in-memory. Compare with Levenshtein distance <= 2 or exact match. Return list of matches (id, mrn, masked_name, dob, gender).

Note: No external Levenshtein library needed for Sprint 2A. Use simple character-by-character comparison for short names, or implement a minimal edit distance function (< 30 LOC). Document the limitation in ADR-0015.

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add dedup service with dob+gender lookup and in-memory fuzzy match"``

---

### Task S1-6: Patient Register Service

**Files:**
- Create: `backend/app/services/patient/register.py`
- Create: `backend/tests/unit/services/patient/test_register.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `register_patient(session, ...)` creates patient with encrypted T1, auto-generated MRN, audit log
- Duplicate NIK at same facility raises ConflictError PATIENT_NIK_DUPLICATE
- Without NIK, register succeeds
- Consent data_use auto-captured with status "given"

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement register service**

```python
def register_patient(session, *, facility_id, facility_code, name, dob, gender,
                     nik=None, phone=None, address=None, recorded_by_user_id,
                     ip_address=None, request_id=None) -> Patient:
```

Flow:
1. If nik provided, check existing nik_hash at facility -> raise ConflictError if duplicate
2. Generate MRN via mrn_generator
3. Create Patient (ORM handles encryption via TypeDecorator)
4. Set nik_last4 = nik[-4:] if nik provided
5. Write audit (action="patient_register")
6. Capture consent data_use (given)
7. Return patient

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add register service with MRN, encryption, audit, consent"``

---

### Task S1-7: Patient Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/patient.py`

- [ ] **Step 1: Create schemas**

```python
class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    dob: date
    gender: Literal["male", "female"]
    nik: str | None = Field(None, pattern=r"^\d{16}$")
    phone: str | None = None
    address: str | None = None

class PatientOut(BaseModel):
    id: str  # UUID as string
    mrn: str
    name: str
    dob: date
    gender: str
    nik_last4: str | None
    phone: str | None
    address: str | None
    facility_id: int

class PatientMasked(BaseModel):
    id: str
    mrn: str
    name_masked: str
    dob: date
    gender: str
    nik_last4: str | None
    phone_masked: str | None

class DuplicateSuggestion(BaseModel):
    id: str
    mrn: str
    name_masked: str
    dob: date
    gender: str

class RegisterResponse(BaseModel):
    patient: PatientOut | None = None
    duplicates: list[DuplicateSuggestion] | None = None
    action: str  # "created" or "confirm"
```

- [ ] **Step 2: Write schema validation tests**

Create `backend/tests/unit/schemas/test_patient_schema.py`:
- NIK regex rejects 15 and 17 digit strings
- NIK None/empty passes
- name min_length=2 enforced
- dob future date rejected (add custom validator)

- [ ] **Step 3: Run tests**

Expected: PASS.

- [ ] **Step 4: Commit**

``git commit -m "feat(api): add Patient Pydantic schemas with validation"``

---

### Task S1-8: Patient Register API Endpoint

**Files:**
- Create: `backend/app/api/patients.py`
- Modify: `backend/app/api/__init__.py`
- Create: `backend/tests/integration/test_patient_register.py`

- [ ] **Step 1: Write failing integration tests**

Test cases (using Flask test_client pattern from Sprint 1):
- POST /api/patients with valid data -> 201, patient returned, encrypted in DB
- POST /api/patients without NIK -> 201, success
- POST /api/patients with duplicate NIK -> 409 PATIENT_NIK_DUPLICATE
- POST /api/patients by researcher -> 403 AUTH_FORBIDDEN
- POST /api/patients by nurse -> 201 (allowed)
- Verify PHIAccessLog NOT written for register (write, not read)
- Verify consent data_use auto-captured

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement patients.py blueprint**

```python
bp = Blueprint("patients", __name__, url_prefix="/api/patients")

@bp.post("/")
@require_role(Role.CLINICIAN, Role.NURSE)
def register_patient():
    data = PatientCreate(**(request.get_json() or {}))
    session = _session()
    # Check for duplicates first
    dupes = find_potential_duplicates(session, facility_id=..., name=data.name, ...)
    if dupes and not request.args.get("confirm_new"):
        return jsonify(duplicates=dupes, action="confirm"), 200
    patient = register_patient(session, ...)
    session.commit()
    return jsonify(patient=PatientOut(...).model_dump()), 201
```

- [ ] **Step 4: Register blueprint**

Add to `backend/app/api/__init__.py`:
```python
from app.api.patients import bp as patients_bp
app.register_blueprint(patients_bp)
```

- [ ] **Step 5: Run tests**

Expected: PASS.

- [ ] **Step 6: Commit**

``git commit -m "feat(api): add POST /api/patients register endpoint with dedup"``

---

### Task S1-9: Patient Register Frontend

**Files:**
- Create: `frontend/src/features/patient/schemas.ts`
- Create: `frontend/src/features/patient/api.ts`
- Create: `frontend/src/features/patient/hooks.ts`
- Create: `frontend/src/features/patient/RegisterForm.tsx`
- Create: `frontend/src/features/patient/RegisterForm.test.tsx`
- Create: `frontend/src/routes/PatientRegisterRoute.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create zod schema (mirror backend Pydantic)**

```typescript
export const PatientCreateSchema = z.object({
  name: z.string().min(2).max(100),
  dob: z.date().max(new Date(), "DOB tidak boleh di masa depan"),
  gender: z.enum(["male", "female"]),
  nik: z.string().regex(/^\d{16}$/, "NIK harus 16 digit").optional().or(z.literal("")),
  phone: z.string().optional(),
  address: z.string().optional(),
  consent_data_use: z.literal(true, { errorMap: () => ({ message: "Persetujuan wajib" }) }),
});
```

- [ ] **Step 2: Create api.ts with useRegisterPatient mutation**

TanStack Query mutation with `onSuccess` invalidating patient list query.

- [ ] **Step 3: Create hooks.ts with usePatients query**

```typescript
export const patientKeys = {
  all: ["patients"] as const,
  list: (params: SearchParams) => [...patientKeys.all, "list", params] as const,
  detail: (id: string) => [...patientKeys.all, "detail", id] as const,
};
```

- [ ] **Step 4: Create RegisterForm.tsx**

shadcn Form + react-hook-form + zod. Fields: name (Input), dob (Calendar/DatePicker), gender (Select), nik (Input, optional), phone (Input, optional), address (Input, optional), consent_data_use (Checkbox). Submit button disabled while submitting. Server error displayed via toast (sonner).

Handle duplicate response: if server returns `duplicates` array, show shadcn Dialog with list and buttons "Pilih pasien ini" / "Daftarkan baru".

- [ ] **Step 5: Write frontend tests**

Test cases:
- Form renders all required fields
- NIK regex validation (reject 15 digit)
- Submit with consent unchecked blocked
- Duplicate dialog renders when server returns duplicates

- [ ] **Step 6: Add route and wire in App.tsx**

```tsx
<Route path="/patients/new" element={<PatientRegisterRoute />} />
```

- [ ] **Step 7: Run all tests**

Run: ``cd frontend && npm run test -- --run``
Expected: All tests pass.

- [ ] **Step 8: Commit**

``git commit -m "feat(ui): add Patient register form with zod validation and dedup dialog"``

---

### Task S1-10: End-to-End Acceptance - Encryption Invariant

**Files:**
- Modify: `backend/tests/integration/test_patient_register.py` (add acceptance test)

- [ ] **Step 1: Write acceptance test**

```python
def test_register_patient_encryption_invariant(client, seeded_admin):
    """AC-2: T1 fields encrypted in DB, no plaintext in raw bytes."""
    # Login as clinician (seeded_admin has admin role, but we need clinician)
    # For now, use admin which has Patient RUD access
    login = client.post("/api/auth/login", json={"email": "admin@x.id", "password": "StrongPass1"})
    headers = {"Authorization": f"Bearer {login.get_json()['access_token']}"}

    resp = client.post("/api/patients", json={
        "name": "Budi Santoso",
        "dob": "1965-03-12",
        "gender": "male",
        "nik": "3201123456780001",
        "phone": "0812345678",
        "address": "Jl. Mawar 5",
        "consent_data_use": True,
    }, headers=headers)
    assert resp.status_code == 201

    # Verify no plaintext in raw DB
    import sqlite3
    from app.extensions import db
    engine = db.engine
    with engine.connect() as con:
        row = con.execute(sa.text("SELECT name_encrypted, phone_encrypted, address_encrypted FROM patient LIMIT 1")).fetchone()
    assert b"Budi Santoso" not in row[0]
    assert b"0812345678" not in row[1]
    assert b"Jl. Mawar 5" not in row[2]
```

- [ ] **Step 2: Run acceptance test**

Run: ``cd backend && pytest tests/integration/test_patient_register.py -v``
Expected: PASS.

- [ ] **Step 3: Run full backend gate**

Run: ``cd backend && ruff check . && mypy . && pytest tests``
Expected: All pass.

- [ ] **Step 4: Commit**

``git commit -m "test(patient): add encryption invariant acceptance test for AC-2"``

---

## Phase S2 - Patient Search + Detail + Soft-Delete

### Task S2-1: Patient Search Service

**Files:**
- Create: `backend/app/services/patient/search.py`
- Create: `backend/tests/unit/services/patient/test_search.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- Search by MRN returns exact match (masked)
- Search by nik_last4 returns matches (masked)
- Search by name+dob returns matches (masked)
- Search returns empty list when no match
- Deleted patients excluded (deleted_at IS NOT NULL)
- Results are masked (name_masked, phone_masked present, no plaintext)

- [ ] **Step 2: Run tests to verify they fail**

Run: ``cd backend && pytest tests/unit/services/patient/test_search.py -v``
Expected: FAIL

- [ ] **Step 3: Implement search service**

`search_patients(session, facility_id, *, q=None, mrn=None, nik_last4=None, dob=None, gender=None, page=1, page_size=20) -> dict`: Build query with filters, apply masking to results, return `{items: [...], total, page, page_size}`.

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add search service with masking"``

---

### Task S2-2: Patient Detail + PHIAccessLog Wiring

**Files:**
- Create: `backend/app/services/patient/reveal.py`
- Create: `backend/tests/unit/services/patient/test_reveal.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `get_patient_detail(session, patient_id, user_id, ip_address)` returns plaintext PatientOut
- PHIAccessLog row written for each non-null T1 field (name, phone, address)
- If phone is None, no log row for phone (only name + address = 2 rows)
- Deleted patient raises NotFoundError

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement reveal service**

Fetch patient by ID (filter deleted_at IS NULL). Decrypt T1 via ORM (automatic). For each non-null T1 field, call `log_phi_access`. Return PatientOut with plaintext.

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add detail service with PHIAccessLog per T1 field"``

---

### Task S2-3: Patient Soft-Delete Service

**Files:**
- Create: `backend/app/services/patient/delete.py`
- Create: `backend/tests/unit/services/patient/test_delete.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `soft_delete_patient(session, patient_id, user_id, reason)` sets deleted_at
- Raises NotFoundError if patient already deleted
- Raises ValidationError if reason is empty
- Writes audit log with action="patient_soft_delete"

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement delete service**

Set `deleted_at = datetime.now(UTC)`, write audit with reason in description.

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add soft-delete service with audit"``

---

### Task S2-4: Patient List + Detail + Delete API Endpoints

**Files:**
- Modify: `backend/app/api/patients.py`
- Create: `backend/tests/integration/test_patient_api.py`

- [ ] **Step 1: Write failing integration tests**

Test cases:
- GET /api/patients returns masked list (no PHIAccessLog written)
- GET /api/patients?q=... filters correctly
- GET /api/patients/{id} returns plaintext + 3 PHIAccessLog rows
- GET /api/patients/{id} by researcher returns anonymized (is_pseudonymized=true, no T1)
- PATCH /api/patients/{id} updates fields
- DELETE /api/patients/{id} by admin -> 200, sets deleted_at
- DELETE /api/patients/{id} by clinician -> 403
- DELETE /api/patients/{id} without reason -> 422
- GET /api/patients excludes deleted by default
- GET /api/patients?include_deleted=true returns deleted (admin only)

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement endpoints**

```python
@bp.get("/")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.EXPERT_REVIEWER)
def list_patients():
    # ... search with masking, no PHIAccessLog

@bp.get("/<patient_id>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.EXPERT_REVIEWER)
def get_patient(patient_id):
    # ... reveal with PHIAccessLog

@bp.patch("/<patient_id>")
@require_role(Role.CLINICIAN, Role.NURSE)
def update_patient(patient_id):
    # ... update T1 fields (re-encrypt)

@bp.delete("/<patient_id>")
@require_role(Role.ADMIN)
def delete_patient(patient_id):
    # ... soft-delete with reason
```

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(api): add patient list, detail, update, delete endpoints"``

---

### Task S2-5: Patient List + Detail Frontend

**Files:**
- Create: `frontend/src/features/patient/PatientList.tsx`
- Create: `frontend/src/features/patient/PatientDetail.tsx`
- Create: `frontend/src/features/patient/DeleteDialog.tsx`
- Create: `frontend/src/routes/PatientsRoute.tsx`
- Create: `frontend/src/routes/PatientDetailRoute.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create PatientList.tsx**

shadcn Table with columns: MRN, Name (masked), DOB, Gender, NIK last4, Actions (View Detail link). Search bar with debounced input. Pagination controls. Uses `usePatientList` hook.

- [ ] **Step 2: Create PatientDetail.tsx**

shadcn Card sections: Identitas (plaintext name, NIK full, DOB, gender, MRN), Kontak (phone, address), Riwayat Medis (placeholder for S3), Consent (placeholder for S3), Encounter (placeholder for S4). Uses `usePatient` hook. RoleGate for admin-only DeleteDialog.

- [ ] **Step 3: Create DeleteDialog.tsx**

shadcn Dialog with textarea for reason (required). Submit calls DELETE endpoint. Only renders for admin role.

- [ ] **Step 4: Add routes in App.tsx**

```tsx
<Route path="/patients" element={<PatientsRoute />} />
<Route path="/patients/:id" element={<PatientDetailRoute />} />
```

- [ ] **Step 5: Write frontend tests**

Test cases:
- PatientList renders masked names
- PatientDetail renders plaintext after fetch
- DeleteDialog hidden for non-admin roles

- [ ] **Step 6: Run all frontend tests**

Run: ``cd frontend && npm run test -- --run``
Expected: PASS.

- [ ] **Step 7: Commit**

``git commit -m "feat(ui): add patient list, detail, and delete dialog"``

---

### Task S2-6: RBAC + Policy Enforcement

**Files:**
- Create: `backend/app/core/rbac/patient_policy.py`
- Modify: `backend/app/api/patients.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- Researcher GET /api/patients/{id} gets anonymized response (no T1, is_pseudonymized=True)
- Expert_reviewer same as researcher
- Admin GET /api/patients/{id} gets full plaintext

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement patient_policy.py**

```python
def filter_patient_for_role(patient: Patient, role: str) -> dict:
    if role in ("researcher", "expert_reviewer"):
        return {"id": str(patient.id), "dob": patient.dob,
                "gender": patient.gender, "is_pseudonymized": True}
    # full plaintext for treatment roles
    return {...}
```

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(patient): add role-based patient data filtering policy"``

---

## Phase S3 - PatientHistory + Consent

### Task S3-1: PatientHistory Model + Migration 003

**Files:**
- Create: `backend/app/db/models/patient_history.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/003_patient_history.py`

- [ ] **Step 1: Write failing model tests**

Test cases:
- PatientHistory with valid condition_code persists
- Invalid condition_code rejected (enum constraint)
- Append-only (no update/delete from API)

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Create PatientHistory model**

Fields: id (PK), patient_id (FK patient.id), condition_code (enum: MI/DM/HT/CKD/dyslipidemia/smoker/other), onset_date_approx (date, nullable), note_encrypted (EncryptedString, nullable), recorded_by_user_id (FK user.id), recorded_at (datetime).

- [ ] **Step 4: Generate migration**

Run: ``alembic revision --autogenerate -m "add patient_history table"``

- [ ] **Step 5: Run tests + migration roundtrip**

Expected: PASS.

- [ ] **Step 6: Commit**

``git commit -m "feat(db): add PatientHistory model and migration 003"``

---

### Task S3-2: Consent Model + Migration 004

**Files:**
- Create: `backend/app/db/models/consent.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/004_consent.py`

- [ ] **Step 1: Write failing model tests**

Test cases:
- Consent with valid type/status persists
- Multiple consent rows per patient (different types)
- Index on (patient_id, consent_type, status) works

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Create Consent model**

Fields: id (PK), patient_id (FK patient.id), consent_type (enum: data_use/research/ai_analysis), status (enum: given/revoked/pending, default pending), given_at (nullable), revoked_at (nullable), evidence_path (nullable), recorded_by_user_id (FK user.id).

- [ ] **Step 4: Generate migration + tests + roundtrip**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(db): add Consent model and migration 004"``

---

### Task S3-3: Consent + PatientHistory Services

**Files:**
- Create: `backend/app/services/consent/capture.py`
- Create: `backend/app/services/consent/revoke.py`
- Create: `backend/app/services/consent/query.py`
- Create: `backend/app/services/patient_history/writer.py`
- Create: `backend/tests/unit/services/consent/test_capture.py`
- Create: `backend/tests/unit/services/consent/test_query.py`
- Create: `backend/tests/unit/services/patient_history/test_writer.py`

- [ ] **Step 1: Write failing tests**

Test cases for consent:
- `capture_consent(session, patient_id, consent_type, user_id)` creates row with status="given", given_at=now
- `revoke_consent(session, patient_id, consent_type, user_id)` creates new row with status="revoked", revoked_at=now
- `has_consent(session, patient_id, consent_type)` returns True if latest row for type is "given"
- `has_consent` returns False if latest row is "revoked"

Test cases for patient_history:
- `add_history(session, patient_id, condition_code, user_id, ...)` creates row
- Invalid condition_code raises error

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement services**

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(consent): add capture, revoke, query services"``

---

### Task S3-4: Consent + PatientHistory API + Frontend

**Files:**
- Create: `backend/app/api/consent.py`
- Create: `backend/app/api/patient_history.py`
- Modify: `backend/app/api/__init__.py`
- Create: `frontend/src/features/consent/` (api, hooks, schemas, ConsentForm)
- Create: `frontend/src/features/patient_history/` (api, hooks, schemas, HistoryForm, HistoryList)

- [ ] **Step 1: Write failing API tests**

Test cases:
- POST /api/patients/{id}/consent captures consent
- GET /api/patients/{id}/consent lists consent rows
- POST /api/patients/{id}/history appends history
- GET /api/patients/{id}/history lists history

- [ ] **Step 2: Implement API endpoints**

- [ ] **Step 3: Create frontend components**

ConsentForm: select consent_type, button "Berikan Persetujuan". HistoryForm: select condition_code, optional onset_date, optional note. HistoryList: table of history entries.

- [ ] **Step 4: Wire into PatientDetail.tsx**

Replace placeholders in PatientDetail with actual ConsentForm and HistoryList.

- [ ] **Step 5: Run all tests**

Expected: PASS.

- [ ] **Step 6: Commit**

``git commit -m "feat(api): add consent and patient history endpoints + UI"``

---

## Phase S4 - Encounter

### Task S4-1: Encounter Model + Migration 005

**Files:**
- Create: `backend/app/db/models/encounter.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/005_encounter.py`

- [ ] **Step 1: Write failing model tests**

Test cases:
- Encounter with valid data persists
- Default status is "open"
- encounter_type enum constraint works

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Create Encounter model**

Fields: id (PK), patient_id (FK patient.id, index), facility_id (FK healthcare_facility.id, index), attending_user_id (FK user.id, index), encounter_type (enum: rawat_jalan/igd, default rawat_jalan), status (enum: open/closed, default open), chief_complaint (Text, nullable), started_at (datetime, default now), ended_at (datetime, nullable). Index on (patient_id, status).

- [ ] **Step 4: Generate migration + tests + roundtrip**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(db): add Encounter model and migration 005"``

---

### Task S4-2: Encounter Services

**Files:**
- Create: `backend/app/services/encounter/create.py`
- Create: `backend/app/services/encounter/close.py`
- Create: `backend/app/services/encounter/query.py`
- Create: `backend/tests/unit/services/encounter/test_create.py`
- Create: `backend/tests/unit/services/encounter/test_close.py`

- [ ] **Step 1: Write failing tests**

Test cases for create:
- `create_encounter(session, patient_id, facility_id, user_id, encounter_type, chief_complaint)` creates encounter
- Raises NotFoundError if patient deleted
- Raises AuthError/ForbiddenError if consent.data_use not given (CONSENT_REQUIRED)
- Writes audit log

Test cases for close:
- `close_encounter(session, encounter_id, user_id)` sets ended_at, status="closed"
- Idempotent: closing already-closed encounter returns success (no-op)
- Raises NotFoundError if encounter not found

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement services**

- [ ] **Step 4: Run tests**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(encounter): add create and close services with consent gate"``

---

### Task S4-3: Encounter API + Frontend

**Files:**
- Create: `backend/app/api/encounters.py`
- Modify: `backend/app/api/__init__.py`
- Create: `frontend/src/features/encounter/` (api, hooks, schemas, CreateForm, Detail, CloseDialog)
- Create: `frontend/src/routes/EncounterCreateRoute.tsx`
- Create: `frontend/src/routes/EncounterDetailRoute.tsx`
- Modify: `frontend/src/App.tsx`
- Create: `backend/tests/integration/test_encounter_api.py`

- [ ] **Step 1: Write failing API tests**

Test cases:
- POST /api/encounters with valid data -> 201
- POST /api/encounters without data_use consent -> 403 CONSENT_REQUIRED
- GET /api/encounters/{id} returns detail
- PATCH /api/encounters/{id}/close -> 200 (idempotent)
- POST /api/encounters by researcher -> 403

- [ ] **Step 2: Implement API endpoints**

```python
@bp.post("/")
@require_role(Role.CLINICIAN, Role.NURSE)
def create_encounter(): ...

@bp.get("/<encounter_id>")
@require_role(Role.CLINICIAN, Role.NURSE, Role.ADMIN)
def get_encounter(encounter_id): ...

@bp.patch("/<encounter_id>/close")
@require_role(Role.CLINICIAN, Role.NURSE)
def close_encounter(encounter_id): ...
```

- [ ] **Step 3: Create frontend components**

EncounterCreateForm: patient_id (from URL), encounter_type (Select), chief_complaint (textarea). EncounterDetail: header with patient link, type, status badge, started_at, "Tutup Encounter" button. CloseDialog: confirmation dialog.

- [ ] **Step 4: Add routes**

```tsx
<Route path="/patients/:id/encounters/new" element={<EncounterCreateRoute />} />
<Route path="/encounters/:id" element={<EncounterDetailRoute />} />
```

- [ ] **Step 5: Run all tests**

Expected: PASS.

- [ ] **Step 6: Commit**

``git commit -m "feat(api): add encounter create, detail, close endpoints + UI"``

---

### Task S4-4: Encounter Consent Gate Test (AC-8)

**Files:**
- Modify: `backend/tests/integration/test_encounter_api.py`

- [ ] **Step 1: Write acceptance test for AC-8**

```python
def test_encounter_blocks_without_data_use_consent(client, seeded_admin):
    """AC-8: Encounter creation requires data_use consent."""
    login = client.post("/api/auth/login", json={"email": "admin@x.id", "password": "StrongPass1"})
    headers = {"Authorization": f"Bearer {login.get_json()['access_token']}"}

    # Register patient (auto-captures data_use consent)
    patient = client.post("/api/patients", json={
        "name": "Test", "dob": "1990-01-01", "gender": "male",
        "consent_data_use": True,
    }, headers=headers).get_json()["patient"]

    # Revoke data_use consent
    client.post(f"/api/patients/{patient['id']}/consent", json={
        "consent_type": "data_use", "status": "revoked",
    }, headers=headers)

    # Try to create encounter -> should fail
    resp = client.post("/api/encounters", json={
        "patient_id": patient["id"], "encounter_type": "rawat_jalan",
    }, headers=headers)
    assert resp.status_code == 403
    assert resp.get_json()["error"]["code"] == "CONSENT_REQUIRED"
```

- [ ] **Step 2: Run test**

Expected: PASS.

- [ ] **Step 3: Commit**

``git commit -m "test(encounter): add consent gate acceptance test for AC-8"``

---

## Phase S5 - ClinicalContext

### Task S5-1: ClinicalContext Model + Migration 006

**Files:**
- Create: `backend/app/db/models/clinical_context.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/006_clinical_context.py`

- [ ] **Step 1: Write failing model tests**

Test cases:
- ClinicalContext with valid data persists
- unique=True on encounter_id enforces 1:1 (second insert raises IntegrityError)

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Create ClinicalContext model**

Fields: id (PK), encounter_id (FK encounter.id, unique=True), symptom_chest_pain (bool, default False), symptom_dyspnea (bool, default False), symptom_palpitation (bool, default False), symptom_syncope (bool, default False), symptom_other (Text, nullable), pain_onset_minutes (int, nullable), pain_duration_minutes (int, nullable), recorded_by_user_id (FK user.id), recorded_at (datetime, default now).

- [ ] **Step 4: Generate migration + tests + roundtrip**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(db): add ClinicalContext model (1:1 with Encounter) and migration 006"``

---

### Task S5-2: ClinicalContext Service + API + Frontend

**Files:**
- Create: `backend/app/services/clinical_context/writer.py`
- Create: `backend/app/api/clinical_context.py`
- Modify: `backend/app/api/__init__.py`
- Create: `frontend/src/features/clinical_context/` (api, hooks, schemas, ContextForm)
- Create: `backend/tests/unit/services/clinical_context/test_writer.py`
- Create: `backend/tests/integration/test_clinical_context_api.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `write_context(session, encounter_id, user_id, symptom_chest_pain, ...)` creates context
- Second write to same encounter raises ConflictError CLINICAL_CONTEXT_EXISTS
- POST /api/encounters/{id}/clinical-context -> 201
- GET /api/encounters/{id}/clinical-context -> 200 with data
- POST duplicate -> 409

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement service, API, frontend**

ContextForm: checkboxes for each symptom (chest_pain, dyspnea, palpitation, syncope), optional text for symptom_other, optional number inputs for pain_onset_minutes and pain_duration_minutes. Save button.

- [ ] **Step 4: Wire into EncounterDetail.tsx**

Replace ClinicalContext placeholder in EncounterDetail with ContextForm.

- [ ] **Step 5: Run all tests**

Expected: PASS.

- [ ] **Step 6: Commit**

``git commit -m "feat(context): add ClinicalContext service, API, and form"``

---

## Phase S6 - VitalSigns

### Task S6-1: VitalSigns Model + Migration 007

**Files:**
- Create: `backend/app/db/models/vital_signs.py`
- Modify: `backend/app/db/models/__init__.py`
- Create: `backend/migrations/versions/007_vital_signs.py`

- [ ] **Step 1: Write failing model tests**

Test cases:
- VitalSigns with valid data persists
- Multiple rows per encounter allowed (M:1)
- Composite index on (encounter_id, measured_at) exists

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Create VitalSigns model**

Fields: id (PK), encounter_id (FK encounter.id, index), measured_at (datetime, default now, index), bp_systolic (int, nullable), bp_diastolic (int, nullable), heart_rate (int, nullable), respiratory_rate (int, nullable), spo2 (int, nullable), temperature (float, nullable), weight (float, nullable), height (float, nullable), recorded_by_user_id (FK user.id). Index on (encounter_id, measured_at).

- [ ] **Step 4: Generate migration + tests + roundtrip**

Expected: PASS.

- [ ] **Step 5: Commit**

``git commit -m "feat(db): add VitalSigns model (M:1 with Encounter) and migration 007"``

---

### Task S6-2: VitalSigns Service + API + Frontend

**Files:**
- Create: `backend/app/services/vital_signs/capture.py`
- Create: `backend/app/services/vital_signs/query.py`
- Create: `backend/app/api/vital_signs.py`
- Modify: `backend/app/api/__init__.py`
- Create: `frontend/src/features/vital_signs/` (api, hooks, schemas, VitalsForm, VitalsList)
- Create: `backend/tests/unit/services/vital_signs/test_capture.py`
- Create: `backend/tests/unit/services/vital_signs/test_query.py`
- Create: `backend/tests/integration/test_vital_signs_api.py`

- [ ] **Step 1: Write failing tests**

Test cases:
- `capture_vitals(session, encounter_id, user_id, bp_systolic, ...)` creates row
- At least one vital field must be non-null (ValidationError)
- `get_vitals(session, encounter_id)` returns list sorted by measured_at DESC
- `get_latest_vital(session, encounter_id)` returns most recent
- POST /api/encounters/{id}/vital-signs -> 201
- GET /api/encounters/{id}/vital-signs -> 200 list DESC

- [ ] **Step 2: Run tests to verify they fail**

Expected: FAIL

- [ ] **Step 3: Implement services, API, frontend**

VitalsForm: number inputs for bp_systolic, bp_diastolic, heart_rate, respiratory_rate, spo2, temperature, weight, height. At least one required. VitalsList: table showing all vitals for encounter, sorted DESC by measured_at, with "Tambah Pengukuran" button.

- [ ] **Step 4: Wire into EncounterDetail.tsx**

Replace VitalSigns placeholder in EncounterDetail with VitalsList + VitalsForm.

- [ ] **Step 5: Run all tests**

Expected: PASS.

- [ ] **Step 6: Commit**

``git commit -m "feat(vitals): add VitalSigns service, API, and form with M:1 support"``

---

## Phase S7 - E2E Acceptance + Cleanup

### Task S7-1: Playwright Setup

**Files:**
- Create: `tests/e2e/playwright.config.ts`
- Create: `tests/e2e/fixtures/seed.ts`
- Create: `tests/e2e/package.json`
- Modify: `.github/workflows/ci.yml`
- Modify: `.gitignore`

- [ ] **Step 1: Install Playwright**

Run from repo root:
```bash
cd tests/e2e && npm init -y && npm install -D @playwright/test
npx playwright install chromium
```

- [ ] **Step 2: Create playwright.config.ts**

```typescript
import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./specs",
  timeout: 30000,
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
  },
  webServer: [
    { command: "cd ../../backend && python -m flask --app wsgi run --port 5000", port: 5000 },
    { command: "cd ../../frontend && npm run dev", port: 5173 },
  ],
});
```

- [ ] **Step 3: Create seed fixture**

`fixtures/seed.ts`: Before each test, call backend seed scripts via API to provision facility + admin + clinician user.

- [ ] **Step 4: Add Playwright job to CI**

Add new job `e2e` in `.github/workflows/ci.yml` that runs after backend + frontend jobs pass. Use `continue-on-error: true` initially.

- [ ] **Step 5: Add to .gitignore**

```
tests/e2e/playwright-report/
tests/e2e/test-results/
```

- [ ] **Step 6: Commit**

``git commit -m "ci: add Playwright e2e test infrastructure"``

---

### Task S7-2: E2E Happy Path Spec

**Files:**
- Create: `tests/e2e/specs/happy_path.spec.ts`

- [ ] **Step 1: Write happy path spec**

```typescript
test("full clinical context flow", async ({ page }) => {
  // Login as clinician
  await page.goto("/login");
  await page.fill('input[name="email"]', "clinician@demo.id");
  await page.fill('input[name="password"]', "StrongPass1");
  await page.click('button[type="submit"]');
  await page.waitForURL("/dashboard");

  // Register patient
  await page.click('a[href="/patients/new"]');
  await page.fill('input[name="name"]', "Budi Santoso");
  await page.fill('input[name="dob"]', "1965-03-12");
  await page.selectOption('select[name="gender"]', "male");
  await page.check('input[name="consent_data_use"]');
  await page.click('button[type="submit"]');
  // If duplicate dialog appears, click "Daftarkan baru"
  // Verify redirect to patient detail

  // Create encounter
  await page.click('a[href*="encounters/new"]');
  await page.fill('textarea[name="chief_complaint"]', "Nyeri dada 2 jam");
  await page.click('button[type="submit"]');

  // Input clinical context
  await page.check('input[name="symptom_chest_pain"]');
  await page.click('button:has-text("Simpan Konteks")');

  // Input vital signs
  await page.fill('input[name="bp_systolic"]', "140");
  await page.fill('input[name="bp_diastolic"]', "90");
  await page.fill('input[name="heart_rate"]', "110");
  await page.click('button:has-text("Tambah Pengukuran")');

  // Close encounter
  await page.click('button:has-text("Tutup Encounter")');
  await page.click('button:has-text("Ya, Tutup")');
});
```

- [ ] **Step 2: Run spec**

Run: ``cd tests/e2e && npx playwright test specs/happy_path.spec.ts``
Expected: PASS (or mark as `test.fixme()` if infrastructure not ready).

- [ ] **Step 3: Commit**

``git commit -m "test(e2e): add happy path clinical context flow spec"``

---

### Task S7-3: E2E Remaining Specs

**Files:**
- Create: `tests/e2e/specs/dedup.spec.ts`
- Create: `tests/e2e/specs/phi_reveal.spec.ts`
- Create: `tests/e2e/specs/consent_gate.spec.ts`

- [ ] **Step 1: Write dedup spec**

Register patient with same name+dob+gender twice. Verify duplicate dialog appears. Click "Daftarkan baru" with confirm_new. Verify second patient created.

- [ ] **Step 2: Write PHI reveal spec**

Login, open patient detail, verify name is plaintext (not masked). Query DB via API or fixture, verify 3 PHIAccessLog rows per detail visit.

- [ ] **Step 3: Write consent gate spec**

Register patient, revoke data_use consent, try create encounter. Verify 403 CONSENT_REQUIRED.

- [ ] **Step 4: Run all specs**

Run: ``cd tests/e2e && npx playwright test``
Expected: All pass (or fixme for infrastructure).

- [ ] **Step 5: Commit**

``git commit -m "test(e2e): add dedup, PHI reveal, and consent gate specs"``

---

### Task S7-4: ADR-0015 - Dedup Strategy

**Files:**
- Create: `docs/adr/0015-dedup-strategy.md`

- [ ] **Step 1: Write ADR**

Document the dedup limitation: NIK hash cannot be queried for fuzzy match (HMAC is one-way). Name is encrypted with Fernet (random IV, non-deterministic). Dedup strategy: query by dob+gender index, decrypt name in-memory for N candidates (N typically < 10), fuzzy match with Levenshtein distance <= 2. Trade-off: false negatives possible for typos in DOB/gender. Mitigation: manual search by MRN or NIK as alternative.

- [ ] **Step 2: Commit**

``git commit -m "docs(adr): add ADR-0015 dedup strategy (dob+gender index + decrypt-in-memory fuzzy)"``

---

### Task S7-5: Full Gate + Tag + Release

- [ ] **Step 1: Run full backend gate**

Run: ``cd backend && ruff check . && mypy . && pytest tests --cov``
Expected: All pass, coverage >= 85%.

- [ ] **Step 2: Run full frontend gate**

Run: ``cd frontend && npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build``
Expected: All pass.

- [ ] **Step 3: Run e2e (if infrastructure available)**

Run: ``cd tests/e2e && npx playwright test``
Expected: All pass.

- [ ] **Step 4: Update README with Sprint 2A first-run steps**

Add section: "After Sprint 1 setup, run migration + seed + patient register flow."

- [ ] **Step 5: Tag interim release**

```bash
git tag -a v0.2.0-sprint-2a -m "Sprint 2A: Clinical Context"
git push origin main
git push origin v0.2.0-sprint-2a
```

- [ ] **Step 6: Create GitHub Release**

Use `gh release create v0.2.0-sprint-2a --title "Sprint 2A: Clinical Context" --notes "..."` with summary of 10 ACs + security posture.

---

## Self-Review Checklist

After writing this plan, verify:

1. **Spec coverage:** All 10 ACs have corresponding tasks:
   - AC-1 (migration) -> S1-1, S3-1, S3-2, S4-1, S5-1, S6-1
   - AC-2 (encryption invariant) -> S1-10
   - AC-3 (list masked, no log) -> S2-4
   - AC-4 (detail plaintext, PHIAccessLog) -> S2-2, S2-4
   - AC-5 (NIK optional, duplicate 409) -> S1-6, S1-8
   - AC-6 (MRN auto-gen) -> S1-2
   - AC-7 (encounter create/close) -> S4-2, S4-3
   - AC-8 (consent capture + gate) -> S3-3, S3-4, S4-4
   - AC-9 (RBAC) -> S2-4, S2-6
   - AC-10 (soft delete) -> S2-3, S2-4

2. **Placeholder scan:** No TBD/TODO in this document.

3. **Type consistency:** Function names, model field names, schema field names consistent across tasks.

---

## Cross-References

- Sprint 1 design: `docs/superpowers/specs/2026-05-30-sprint-1-foundation-design.md`
- Architecture overview: `docs/superpowers/specs/2026-05-30-architecture-overview-design.md`
- Data model: `docs/superpowers/specs/2026-05-30-data-model-and-phi-design.md`
- ADR-0008 (encounter-driven): `docs/adr/0008-encounter-driven-ai-only-workflow.md`
- ADR-0015 (dedup strategy): `docs/adr/0015-dedup-strategy.md` (NEW)
- Sprint 1 plan: `docs/superpowers/plans/2026-05-30-sprint-1-foundation.md`
