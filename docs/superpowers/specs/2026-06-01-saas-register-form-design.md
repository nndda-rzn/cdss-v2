# Design Spec: SaaS Patient Register Form (Card & Grid)

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: 2026-06-01-saas-ui-polish-design, ADR-0010, ADR-0012

## Context

The patient register form (`/patients/new`) currently renders as a single
`max-w-lg` vertical column of inputs on the bare `bg-sunken` canvas. After the
SaaS-polish pass landed, this page is the most visually behind-the-curve route
in the app: no card chrome, no field grouping, primary action stuck against
the left edge.

Maintainer flagged the page as feeling "too plain". The task is to bring it
in line with the rest of the SaaS-polished surfaces while keeping it readable
and quick to fill in for clinicians (no wizard, no animation).

## Decision

Apply a **Card & Grid** layout:

1. **Wrap the form in a `Card`** with `shadow-elev-sm` and `max-w-3xl`,
   centered horizontally. Page background stays `bg-sunken`.
2. **Two-column grid** for short fields:
   - Row 1: Nama Lengkap (full width).
   - Row 2: Tanggal Lahir (left) · Jenis Kelamin (right).
   - Row 3: NIK (left) · Telepon (right).
   - Row 4: Alamat (full width, kept as `Input` for now — single-line is enough
     for puskesmas RT/RW addresses).
3. **Visual grouping** — a `Separator` between the required-identity block
   (rows 1–3 partial) and the optional-contact block (NIK/phone/address).
   A small `section-label` ("Identitas Pasien" / "Patient Identity" and
   "Kontak Opsional" / "Optional Contact") sits above each block.
4. **Footer aksi** — consent checkbox sits above a `flex justify-end gap-2`
   row containing "Batal" (outline, navigates back) and "Daftar" (primary).
   On mobile both buttons go full-width and stack.
5. **Page title and subheading** — keep "Pasien Baru" as `<h1 className="text-2xl">`
   plus a one-line description ("Daftarkan pasien baru ke fasilitas Anda."
   / "Register a new patient to your facility."). Both bilingual.
6. **Bilingual labels** — every label, helper, button, and section header
   flows through `useI18nStore.t()`.
7. **Native checkbox replaced** with the project's `<Checkbox>` shadcn
   primitive for visual consistency with the rest of the app.

## Out of Scope

- New fields (e.g., emergency contact, pekerjaan).
- Wizard/stepped UI — overkill for a 7-field form.
- Sectioned (Vercel/Stripe-style) split layout — better suited to settings,
  not data-entry.
- Animation beyond what the existing Card/Button hover states provide.
- Backend changes.

## Acceptance Criteria

- AC-1: Form renders inside a `Card` with `shadow-elev-sm` and `max-w-3xl`,
  centered on the page.
- AC-2: Tanggal Lahir and Jenis Kelamin sit in a 2-column grid at `sm+`.
  NIK and Telepon do the same. Nama and Alamat stay full-width.
- AC-3: A `Separator` plus a `section-label` separates required-identity
  fields (Nama, DOB, Gender, NIK) from optional-contact fields (Phone,
  Address). NIK is treated as identity (sits with DOB/Gender block).
- AC-4: Submit row sits at the bottom-right with "Batal" + "Daftar"; on
  mobile (<sm) both are full-width and stacked.
- AC-5: Heading reads "Pasien Baru" / "New Patient" and a sub-headline
  appears below; both flip on language toggle.
- AC-6: Consent uses the shadcn `Checkbox` primitive (not raw `<input>`).
- AC-7: All 4 existing `RegisterForm` tests still pass without modification.
- AC-8: Frontend gate green (typecheck + lint + prettier + test + build);
  file-size guard exits 0.

## Implementation Notes

- The form file is currently 192 source lines. The Card/grid restructure
  will push it close to the 200-line budget. If we cross 200 code lines
  we extract `IdentitySection.tsx` and `ContactSection.tsx` into the
  feature's `components/` subfolder. The existing `DedupDialog` integration
  stays exactly as-is.
- Field validation messages are still owned by the Zod schema in
  `schemas.ts`. No schema change needed.
- Language toggle is already in the header; no per-page toggle.
- Tests use `getByLabelText(/nama lengkap/i)` etc., so label text must keep
  Indonesian as the default language string (we render via `t()` but the
  default ID string still matches the regex).
