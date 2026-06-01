# Design Spec: Clinical Split-Screen Login

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: 2026-06-01-saas-ui-polish-design.md, ADR-0010 (color), ADR-0012 (bilingual)

## Context

The first SaaS-polish pass kept the login as a single centered card on a soft
gradient. Visually it looked closer to a generic SaaS form than to a clinical
authentication portal — the brand identity (EcgSweep motif, petrol palette)
sits inside a small icon and gets lost on a wide monitor.

We want the login to read as the front door of a clinical instrument while
still feeling premium and modern. The reference is enterprise EMR/CDSS portals
(e.g. Epic / Cerner login screens), which use a large branded panel paired
with a clean form panel. Marketing-style hero pages with neon gradients are
explicitly off-limits per ADR-0010 (data-as-protagonist).

## Decision

Replace the centered-card login with a **Clinical Split-Screen** at `lg+`:

1. **Left panel (≥ lg, 50% width)** — solid `petrol-900` background, white
   foreground. Renders:
   - The `EcgSweep` motif at large scale (~70% panel width) at 5–8% opacity
     as an instrument-grade watermark.
   - A bold wordmark "EKG-Insight" in semibold 2xl.
   - A single bilingual sub-headline ("Sistem Pendukung Keputusan Klinis" /
     "Clinical Decision Support System").
   - One short trust line at the bottom edge ("Akses aman untuk tenaga
     kesehatan" / "Secure access for healthcare professionals") + a small
     clinical disclaimer that mirrors what the dashboard already states.
2. **Right panel** — `bg-paper`. The form lives directly on this canvas
   (no wrapping `Card`, no shadow). Form has its own `max-w-sm` container,
   centered. Submit button is full-width.
3. **Below `lg`** — left panel is hidden; right panel takes the full width.
   On mobile/tablet, the form sits centered on a clean white background
   (no gradient, no motif at full opacity). This matches how clinical EMR
   login pages render on bedside tablets.
4. **Language toggle** — absolute top-right of the right panel on `lg+`,
   absolute top-right of the screen below `lg`.

The right panel keeps the existing `LoginForm` component but drops its
implicit `Card` wrapper and gives the submit button `w-full`.

## Out of Scope

- Marketing visuals (gradients, glassmorphism, animated orbs).
- New copy beyond the trust + disclaimer lines.
- Changing the JWT auth flow or backend.
- Dark mode (declined globally).
- Forgot-password / SSO / 2FA links — none exist on the backend yet.

## Acceptance Criteria

- AC-1: At `lg` (1024px) and wider, the login renders as two equal columns:
  a dark petrol panel on the left and a white form panel on the right.
- AC-2: Below `lg`, the dark panel is hidden and the form fills the screen
  on a clean white background.
- AC-3: The `EcgSweep` motif appears on the left panel at large scale and
  low opacity (5–8%) and is decorative (`aria-hidden`).
- AC-4: The submit button is `w-full` and renders as `bg-primary` with the
  standard hover/active feedback from the SaaS-polish pass.
- AC-5: Headline, sub-headline, trust line, disclaimer, and form labels
  flip between ID and EN via the existing `useI18nStore`.
- AC-6: Language toggle is reachable in both responsive states.
- AC-7: All existing `LoginForm` tests still pass (no regression in the
  form-level behavior).

## Implementation Notes

- Layout uses Tailwind grid: `lg:grid lg:grid-cols-2 min-h-screen`.
- Left panel `bg-petrol-900 text-white relative overflow-hidden`.
- The `EcgSweep` motif uses `text-white/[0.06]` and `pointer-events-none`.
- Right panel `bg-paper relative flex items-center justify-center px-6`.
- Brand wordmark uses the existing `EcgSweep` SVG plus a text label so the
  motif and the wordmark stay coherent (no separate logo file).
- Keep file size well under the 200-line budget; if `login.tsx` grows past
  ~140 lines, split the left panel into `LoginBrandPanel.tsx`.
- The page must not depend on JS to render the petrol panel — it's a pure
  Tailwind layout, no client conditional.
