# Design Spec: Encounter Detail Clinical Workspace

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: ADR-0008 (encounter-driven workflow), 2026-06-01-saas-ui-polish-design, 2026-06-01-focus-shell-analysis-design

## Context

The encounter detail page (`/encounters/:id`) stacks four full-width Cards in a
`max-w-2xl` (672px) column: encounter info, clinical context, vital signs, and
ECG studies. On any screen wider than ~700px the entire right half is empty,
and the linear stack scrolls to ~2000px. The maintainer wants it to feel like a
clinical workspace (EMR-grade) while keeping the SaaS polish already shipped.

## Decision

Adopt a **3-zone "Clinical Workspace" layout**: clinical EMR *patterns* with
SaaS *visual execution*.

```
┌──────────────────────────────────────────────────────────────────┐
│ ZONE 1: PATIENT BANNER (sticky top-0)                            │
│ avatar · name(masked) · MRN · DOB · age · gender · #123 [Aktif]  │
├────────────────────────────────────┬─────────────────────────────┤
│ ZONE 2: CLINICAL CONTENT (flex-1)  │ ZONE 3: META RAIL (320px,    │
│  - Tanda Vital                     │         sticky)              │
│  - Konteks Klinis                  │  - Info Kunjungan            │
│  - Studi EKG (upload + grid)       │  - Aksi (Tutup + quick)      │
│                                    │  - Pasien (ringkas + link)   │
└────────────────────────────────────┴─────────────────────────────┘
```

### Decisions (per maintainer, default to senior recommendation)

- **Layout**: 3-zone (banner + content + meta rail).
- **Patient banner (a)**: full identity — avatar mini, masked name, MRN, DOB,
  age, gender, encounter number + status badge.
- **Encounter info Card**: removed from the body; its data moves to the banner
  (number + status) and the right rail (type + start + chief complaint).
- **"Tutup Kunjungan" button (a)**: right rail Actions card with a short
  clinical hint, not the page header.

### SaaS vs Clinical balance

| Aspect | Treatment |
|--------|-----------|
| Card radius | 6px (`rounded-lg`) — soft, not bouncy |
| Card shadow | `elev-sm` — lifted but subtle |
| Card padding | body `p-5`, rail `p-4` (denser) |
| Inter-card gap | `gap-4` (tight, clinical density) |
| Typography | 14px base, tabular numerals for MRN/DOB/vitals |
| Sticky | banner `top-0`; rail sticky below banner |
| Empty space | filled with clinical data + meta, not decoration |
| Excluded | glassmorphism, gradients, entrance animation, drama |

## New Components

| File | Responsibility |
|------|----------------|
| `frontend/src/features/encounter/components/EncounterPatientBanner.tsx` | Sticky banner: avatar + identity strip + encounter number + status badge |
| `frontend/src/features/encounter/components/EncounterInfoCard.tsx` | Rail card: type, start time, chief complaint |
| `frontend/src/features/encounter/components/EncounterActionsCard.tsx` | Rail card: close-encounter (with hint) + quick actions |
| `frontend/src/features/encounter/components/EncounterPatientCard.tsx` | Rail card: patient summary (DOB, phone, address) + link to profile |

## Changed

- `frontend/src/features/encounter/pages/Detail.tsx`: rebuilt into the 3-zone
  layout; orchestrates the new components. Stays the only caller-facing entry.

## Reused (unchanged)

- `VitalsPanel`, `ContextForm`, `EcgUploadForm`, `EcgStudyList` — same props.
- `fetchPatient` + `patientKeys.detail` for the patient summary + banner.
- `PatientIdentityStrip` (from focus shell) — reused inside the banner if it
  fits; otherwise a banner-specific compact identity render.

## RBAC / Privacy

- Patient identity comes from `GET /api/patients/:id` (role-masked already).
- For pseudonymised reads the banner shows "Pasien Anonim".
- "Tutup Kunjungan" stays available to the roles that already had it (no RBAC
  change — it was ungated in the header before; keep behaviour, just relocate).

## Out of Scope

- Tabs (rejected — clinicians need vitals + context + ECG visible together).
- Dark mode.
- Backend changes.
- Changing VitalsPanel / ContextForm / ECG components internally.

## Acceptance Criteria

- AC-1: At >= lg (1024px) the page renders banner + 2-column body (content +
  320px rail). The right half is no longer empty.
- AC-2: Below lg, layout collapses to a single column (banner, then content,
  then rail cards).
- AC-3: Patient banner is sticky at the top and shows masked name, MRN, DOB,
  age, gender, encounter number + status; "Pasien Anonim" when pseudonymised.
- AC-4: The encounter info Card is gone from the body; its data appears in the
  banner (number + status) and the rail (type, start, chief complaint).
- AC-5: "Tutup Kunjungan" lives in the rail Actions card with a short hint.
- AC-6: Right rail is sticky on scroll at lg+.
- AC-7: Body shows exactly three cards: Tanda Vital, Konteks Klinis, Studi EKG.
- AC-8: Patient summary card links to `/patients/:id`.
- AC-9: `Detail.tsx` and every new component stay under the 200-line budget.
- AC-10: Bilingual ID/EN for all new copy.
- AC-11: Frontend gate green (typecheck + lint + tests + build); file-size
  guard exits 0; no test regression.

## Implementation Notes

- `Detail.tsx` fetches the encounter (existing) and the patient (new query via
  `encounter.patient_id`). Banner + rail patient card consume the patient data.
- Sticky offsets: AppShell header is 56px; banner 56px. Rail sticky uses
  `lg:sticky lg:top-[136px]` (56 + 56 + 16 gap) — or simpler `lg:top-20` if the
  banner is not itself sticky within the scroll container. Verify visually.
- Keep `Detail.tsx` an orchestrator; push card markup into the four new files
  to stay within budget.
