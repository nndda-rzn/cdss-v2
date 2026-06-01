# Encounter Detail Clinical Workspace Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task.

**Goal:** Rebuild `/encounters/:id` into a 3-zone clinical workspace (sticky
patient banner + clinical content + sticky meta rail) that fills the right-side
space and cuts vertical scroll, keeping the shipped SaaS polish.

**Architecture:** `Detail.tsx` becomes an orchestrator that fetches the
encounter + patient and lays out three zones. Four new presentational
components live in `features/encounter/components/`. The clinical panels
(VitalsPanel, ContextForm, ECG components) are reused unchanged.

**Tech Stack:** React, React Query, React Router, Tailwind, Zustand i18n,
existing patient/encounter query layer, date-fns for age.

---

## Task 1: EncounterPatientBanner

**Files:** `frontend/src/features/encounter/components/EncounterPatientBanner.tsx` (new)

- Props: `patient: PatientDetail | undefined`, `encounterId: number`, `status: string`.
- Sticky `top-0 z-20`, `h-14`, `bg-paper`, `border-b border-border-strong`.
- Left: avatar mini (initials) + masked name + MRN + DOB + age + gender.
- Right (`ml-auto`): "Kunjungan #<id>" + status Badge (Aktif/Tertutup).
- Pseudonymised / no name -> "Pasien Anonim".
- Bilingual via `useI18nStore`.
- Verify: typecheck.
- Commit: `feat(encounter): add sticky patient banner`.

## Task 2: EncounterInfoCard (rail)

**Files:** `frontend/src/features/encounter/components/EncounterInfoCard.tsx` (new)

- Props: `encounterType: string`, `startedAt: string`, `chiefComplaint: string | null`.
- Compact Card (`p-4`): rows for Tipe, Mulai, Keluhan Utama.
- Bilingual labels; "IGD" / "Rawat Jalan" -> "ER" / "Outpatient".
- Verify: typecheck.
- Commit: `feat(encounter): add rail info card`.

## Task 3: EncounterActionsCard (rail)

**Files:** `frontend/src/features/encounter/components/EncounterActionsCard.tsx` (new)

- Props: `status: string`, `closing: boolean`, `onClose: () => void`.
- Card (`p-4`): when status open, short hint + full-width outline
  "Tutup Kunjungan" button (disabled while closing).
- When closed: show a muted "Kunjungan telah ditutup" note instead.
- Bilingual.
- Verify: typecheck.
- Commit: `feat(encounter): add rail actions card`.

## Task 4: EncounterPatientCard (rail)

**Files:** `frontend/src/features/encounter/components/EncounterPatientCard.tsx` (new)

- Props: `patient: PatientDetail`.
- Card (`p-4`): section-label "Pasien", rows DOB / phone / address (mask-aware,
  hide rows that are null), link "→ Profil Pasien" to `/patients/:id`.
- Anonymised handling for pseudonymised reads.
- Bilingual.
- Verify: typecheck.
- Commit: `feat(encounter): add rail patient summary card`.

## Task 5: Rebuild Detail.tsx into 3 zones

**Files:** `frontend/src/features/encounter/pages/Detail.tsx` (modify)

- Add patient query: `patientKeys.detail(data.patient_id)` -> `fetchPatient`,
  `enabled` once encounter resolves.
- Layout:
  ```tsx
  <div className="space-y-4">
    <EncounterPatientBanner patient={patient.data} encounterId={data.id} status={data.status} />
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_320px]">
      <div className="space-y-4">
        <Card>Tanda Vital -> VitalsPanel</Card>
        <Card>Konteks Klinis -> ContextForm</Card>
        <Card>Studi EKG -> EcgUploadForm + EcgStudyList</Card>
      </div>
      <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
        <EncounterInfoCard ... />
        <EncounterActionsCard ... onClose={closeMutation.mutate} />
        {patient.data && <EncounterPatientCard patient={patient.data} />}
      </aside>
    </div>
  </div>
  ```
- Remove the old encounter info Card and the header close button.
- Keep loading/error states.
- Verify: typecheck + lint + `npm run test -- --run src/features/encounter`.
- Commit: `feat(encounter): rebuild detail into clinical workspace layout`.

## Task 6: Full gate

```bash
cd frontend
npm run typecheck && npm run lint && npm run test -- --run && npm run build
cd ..
backend/.venv/Scripts/python.exe scripts/check_file_size.py
```

Expected: all green, EXIT 0.

## Task 7: Manual verification

- clinician -> open encounter -> banner sticky with patient identity, 2-column
  body at lg+, rail sticky on scroll, right half filled.
- "Tutup Kunjungan" in rail closes the encounter; status flips to Tertutup.
- Patient card link navigates to `/patients/:id`.
- mobile: single column stack.
- toggle ID/EN.

## Task 8: Push + PR

- Push `feat/encounter-detail-workspace`.
- `gh pr create` with before/after note, AC checklist, spec link.
- Wait for CI, squash-merge.

---

## Acceptance Criteria

Mirrors the spec — see `2026-06-01-encounter-detail-workspace-design.md`.
