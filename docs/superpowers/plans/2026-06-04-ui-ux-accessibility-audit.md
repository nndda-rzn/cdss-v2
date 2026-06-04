# UI/UX & Accessibility Audit Fix Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address all UI/UX and accessibility findings from the comprehensive audit to ensure a polished, accessible, and consistent clinical dashboard web application.

**Architecture:** Frontend component edits across various domains to address specific findings. Make sure sonner toasts are configured, accessibility attributes are set, language strings are translated, and input types are corrected.

**Tech Stack:** React, react-hook-form, Tailwind CSS, Lucide icons, Sonner toast, Zustand.

---

### Task 1: Fix Email Input Type and Labels in LoginForm

**Files:**
- Modify: `frontend/src/features/auth/components/LoginForm.tsx`

- [ ] **Step 1: Modify email input element and label translation**
  - Change input type from `text` to `email`.
  - Add i18n support to the "Email" FormLabel.
  - Add `aria-live="polite"` and `aria-relevant="all"` to the serverError container.

- [ ] **Step 2: Verify changes**
  - Ensure login screen still loads and email input field has `type="email"`.

- [ ] **Step 3: Commit**
  - Commit changes with message `feat(auth): fix email type and accessibility in login form`.

---

### Task 2: Add aria-label to Icon-only Buttons

**Files:**
- Modify: `frontend/src/features/admin/pages/UserListPage.tsx`
- Modify: `frontend/src/features/admin/pages/FacilityListPage.tsx`
- Modify: `frontend/src/features/tuning/pages/TuningGridPage.tsx`

- [ ] **Step 1: Add aria-labels to buttons in UserListPage.tsx**
  - Add `aria-label={u.is_active ? "Nonaktifkan user" : "Aktifkan user"}` to the status toggle button.
  - Add `aria-label="Edit user"` to the edit button.

- [ ] **Step 2: Add aria-labels to buttons in FacilityListPage.tsx**
  - Add `aria-label="Edit fasilitas"` to the edit button.

- [ ] **Step 3: Add aria-labels to buttons in TuningGridPage.tsx**
  - Add `aria-label="Kembali"` to the back button icon.

- [ ] **Step 4: Commit**
  - Commit changes with message `feat(ui): add aria-labels to icon-only buttons`.

---

### Task 3: Add Table Semantics and Captions

**Files:**
- Modify: `frontend/src/features/patient/pages/PatientList.tsx`
- Modify: `frontend/src/features/admin/pages/UserListPage.tsx`
- Modify: `frontend/src/features/admin/pages/FacilityListPage.tsx`

- [ ] **Step 1: Add caption and accessibility to PatientList table**
  - Add screen-reader-only `<caption>` or `aria-label` to table.

- [ ] **Step 2: Add caption and accessibility to UserListPage table**
  - Add screen-reader-only `<caption>` or `aria-label` to table.

- [ ] **Step 3: Add caption and accessibility to FacilityListPage table**
  - Add screen-reader-only `<caption>` or `aria-label` to table.

- [ ] **Step 4: Commit**
  - Commit changes with message `feat(ui): improve table accessibility with captions`.

---

### Task 4: Add Confirmation Dialog for Destructive Actions

**Files:**
- Modify: `frontend/src/features/encounter/components/EncounterActionsCard.tsx`

- [ ] **Step 1: Use window.confirm for closing encounter**
  - Prompt user to confirm before calling `onClose()`.

- [ ] **Step 2: Commit**
  - Commit changes with message `feat(encounter): add close encounter confirmation`.

---

### Task 5: Mount Toaster and Add Toast Feedback

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/features/admin/pages/UserListPage.tsx`
- Modify: `frontend/src/features/admin/pages/FacilityListPage.tsx`

- [ ] **Step 1: Mount Toaster in App.tsx**
  - Import and render `Toaster` from `@/components/ui/sonner`.

- [ ] **Step 2: Add toast notifications to UserListPage**
  - Use `toast.success` and `toast.error` for user CRUD actions.

- [ ] **Step 3: Add toast notifications to FacilityListPage**
  - Use `toast.success` and `toast.error` for facility CRUD actions.

- [ ] **Step 4: Commit**
  - Commit changes with message `feat(ui): mount toaster and add CRUD toast notifications`.

---

### Task 6: Translate Hardcoded Strings

**Files:**
- Modify: `frontend/src/features/patient/pages/PatientList.tsx`
- Modify: `frontend/src/features/patient/pages/PatientDetail.tsx`

- [ ] **Step 1: Translate search placeholder in PatientList**
  - Use `t("Cari MRN, nama, atau NIK...", "Search MRN, name, or NIK...")`.

- [ ] **Step 2: Translate tabs in PatientDetail**
  - Use `t("Kunjungan", "Encounters")`, `t("Riwayat Medis", "Medical History")`, `t("Persetujuan", "Consent")`.

- [ ] **Step 3: Commit**
  - Commit changes with message `feat(i18n): translate hardcoded search placeholders and tabs`.

---

### Task 7: CreateForm Loading State

**Files:**
- Modify: `frontend/src/features/encounter/pages/CreateForm.tsx`

- [ ] **Step 1: Add loading state to CreateForm submit button**
  - Disable and show spinner or loading text when form is submitting.

- [ ] **Step 2: Commit**
  - Commit with message `feat(encounter): add loading state to encounter creation form`.

---

### Task 8: Warn on Unsaved Changes

**Files:**
- Modify: `frontend/src/features/patient/components/RegisterForm.tsx`
- Modify: `frontend/src/features/encounter/pages/CreateForm.tsx`

- [ ] **Step 1: Add window beforeunload listener in RegisterForm**
  - Warn before leaving if form is dirty.

- [ ] **Step 2: Add window beforeunload listener in CreateForm**
  - Warn before leaving if form is dirty.

- [ ] **Step 3: Commit**
  - Commit with message `feat(ui): add unsaved changes warning before unload`.

---

### Task 9: Theme Color Meta and Consistent Typography

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/src/features/tuning/pages/TuningGridPage.tsx`
- Modify: `frontend/src/features/admin/pages/AdminDashboardPage.tsx`

- [ ] **Step 1: Add theme-color meta tag**
  - Add `<meta name="theme-color" content="#062a33" />` matching petrol-900.

- [ ] **Step 2: Consistent heading weights**
  - Change `font-bold` to `font-semibold` in TuningGridPage.
  - Add `cursor-pointer` to AdminDashboard buttons.

- [ ] **Step 3: Commit**
  - Commit with message `feat(ui): add theme color meta and improve typography consistency`.

---

### Task 10: Fix QuickActions Link Target

**Files:**
- Modify: `frontend/src/features/dashboard/components/QuickActions.tsx`

- [ ] **Step 1: Link "Kunjungan Baru" directly**
  - Direct user to correct flow (e.g., patient list to search first but with proper instructions, or directly register/new flow).
  - Clarify the text to matches target.

- [ ] **Step 2: Commit**
  - Commit with message `feat(dashboard): fix quick actions link targets`.
