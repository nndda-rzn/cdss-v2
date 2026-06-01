# Design Spec: EKG-Insight Polished SaaS UI

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: ADR-0010 (color), ADR-0011 (radius), ADR-0012 (bilingual), 2026-05-31-ui-ux-audit-pass-1

## Context

The first UI pass (`v0.4.0-ui-ux-pass-1`) deliberately picked an instrument-grade,
clinical-sharp look — 2px radius, near-zero shadows, document-card aesthetic.
This served the goal of "data-as-protagonist" and clinical authority. After
using it day-to-day the maintainer found it visually flat compared to modern
SaaS dashboards (handhold.io was given as a reference).

The goal here is to add SaaS-grade polish (refined radius, progressive elevation,
breathable spacing, micro-interactions, dashboard, global search) **without**
losing clinical credibility — no bright gradients, no AI-purple, no consumer-toy
look. Petrol + charcoal palette stays. Light-mode only stays.

ADR-0012 also requires bilingual ID + EN UI with a language toggle, which the
current shipped UI does not yet expose.

## Decision

Apply a "Polished SaaS Clinical" pass on top of the existing palette, scoped to
six areas:

1. **Bilingual UI (ID/EN)** — Zustand i18n store, `t()` helper used in components,
   visible language toggle in the header. Default ID. Backend `*_id`/`*_en`
   columns are unchanged; this is purely UI-side translation of static strings.

2. **Visual polish** — radius `2px → 6px`, progressive shadow scale,
   card padding `p-4 → p-5`, refined hover/focus states, page fade-in
   (`animate-fadeIn`, 150ms).

3. **Layout** — collapsible sidebar (`w-56 ↔ w-16` icon-only with tooltips),
   user-avatar dropdown menu in the header (replaces plain logout button).

4. **Dashboard** — replace the `/dashboard` placeholder with KPI cards
   (Total Patients, Active Encounters, Analyses Today, Pending Tasks),
   recent encounters table, and quick action buttons. Backed by a new
   `GET /api/dashboard/stats` endpoint.

5. **Global search** — `Ctrl+K` command palette in the header. Backend
   `GET /api/search?q=...` returns matching patients (by MRN prefix; bounded)
   and encounters. Decryption of patient name happens in memory after the
   bounded MRN/dob lookup, consistent with ADR-0015.

6. **Auth & utility pages** — login background gets a subtle radial gradient,
   custom 404 page using the EcgSweep motif and "Kembali ke Dashboard"
   ("Back to Dashboard") action. Empty states already use the motif; only
   text strings get the bilingual treatment.

## Out of Scope

- Dark mode (explicitly declined).
- Changing the petrol/charcoal palette or Inter font.
- Marketing-style visuals (gradients, glassmorphism, etc.).
- New backend functionality beyond the two read endpoints (dashboard + search).
- Changing existing route paths or API contracts.

## Acceptance Criteria

- AC-1: A `lang` switch in the header flips visible UI strings between ID and EN
  for the dashboard, sidebar nav, and at least the patient-list and login pages.
- AC-2: All `Card` primitives render with `radius=6px` and a subtle shadow that
  intensifies slightly on hover.
- AC-3: The sidebar can be collapsed to icon-only and re-expanded; collapsed
  state shows tooltips for nav items.
- AC-4: `/dashboard` shows four KPI numbers and a five-row recent-encounters
  table sourced from `GET /api/dashboard/stats`.
- AC-5: `Ctrl+K` opens a global search palette that returns matching patients
  and encounters from `GET /api/search?q=...`.
- AC-6: Login page has the new gradient background; navigating to a
  non-existent path renders the custom 404 page (not a generic React Router
  fallback).
- AC-7: All backend tests pass; ruff + mypy clean; frontend `lint`,
  `typecheck`, `test`, and `build` all pass; `python scripts/check_file_size.py`
  exits 0.

## Implementation Notes

- File-size budget guard (`scripts/check_file_size.py`) is in effect. Each new
  TS/TSX module is capped at ~200 code lines; split when approaching.
- The Dashboard endpoint counts `analyses_today` from `AIAnalysis.created_at`
  in the current UTC day; `pending_tasks` is `Encounter.status == "open"`.
- The search endpoint scopes results by the caller's `facility_id` claim and
  caps results at 10 per category.
- Translation strings live next to the components that use them (no central
  i18n bundle yet); `t("Pasien", "Patients")` is the inline form. A central
  catalogue can be added later if drift becomes a problem.
