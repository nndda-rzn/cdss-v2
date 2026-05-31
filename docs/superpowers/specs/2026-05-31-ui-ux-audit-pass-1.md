# UI/UX Audit — Pass-1 (EKG-Insight CDSS)

| Item | Keterangan |
| --- | --- |
| Dokumen | UI/UX Audit Pass-1 |
| Tanggal | 2026-05-31 |
| Branch | feat/ui-ux-pass-1 |
| Scope | 7 halaman: Login, Dashboard, Patients (list/register/detail), Encounter (create/detail) |
| Tools | uipro `ui-ux-pro-max` (CLI) + manual review |
| Decisions locked | Compact clinical density, ECG-line motif, petrol/amber/wine status palette, medical-chart 2-col untuk Patient Detail |

## 1. Konteks

Sprint 2A + 2B sudah ship dan running. UI saat ini pakai shadcn defaults (neutral gray, soft radius, generic Card pattern). ADR-0010 (petrol+charcoal), ADR-0011 (sharp radius), ADR-0013 (inferno colormap) sudah jadi keputusan tapi belum diterapkan ke `frontend/src/index.css`.

Audit ini bukan untuk find bug, tapi untuk identifikasi **karakter gap** dan accessibility/quality issue yang harus ditutup di pass-1.

## 2. Output uipro skill (relevansi)

uipro merekomendasikan style "Accessible & Ethical" (WCAG AAA target, focus rings 3-4px, ARIA labels, skip links, reduced motion, 44x44px touch targets). Itu align dengan plan kita. Palette teal+green dan font Figtree yang direkomendasikan **kita override** karena ADR-0010 (petrol+charcoal) dan Inter sudah locked.

Yang kita ambil dari uipro:
- Semua effect dan accessibility item (focus rings, ARIA, skip link, reduced motion)
- shadcn stack guidelines: Form/zod/FormMessage/Table semantic structure
- Pre-delivery checklist: contrast ≥4.5:1, hover transitions 150-300ms, cursor-pointer pada clickable, keyboard nav

## 3. Cross-Cutting Findings

### 3.1 Theme tokens (Critical)
- `index.css` masih pakai shadcn neutral gray defaults
- ADR-0010 (petrol+charcoal) dan ADR-0011 (sharp radius) belum di-apply
- Tidak ada status color tokens (good/acceptable/poor pakai shadcn variant generic)
- Impact: UI flat, tidak punya brand voice

### 3.2 Typography (Important)
- Inter di-load dari sistem; tidak self-hosted (rentan FOUT, dependency CDN)
- Tidak ada `font-variant-numeric: tabular-nums` untuk MRN, study_uid, vital signs, dates
- Heading hierarchy lemah: tidak ada weight contrast yang kuat (700/600/500)
- Line-height 1.5 (default) terlalu longgar untuk clinical density

### 3.3 Card pattern (Important)
- Card default: `rounded-lg`, soft shadow, 1px subtle border → SaaS marketing feel
- Untuk medical app harus document-card pattern: 2px radius, prominent border, near-zero shadow

### 3.4 Status badges (Important)
- Quality badge pakai shadcn variant `default`/`secondary`/`destructive`
- `destructive` = bright red (consumer pattern); clinical app reserve red untuk emergency
- Belum ada glyph dot, belum ada tabular score, belum ada tooltip

### 3.5 Layout & navigation (Critical)
- AppShell: sidebar 224px tanpa header, tanpa user menu, tanpa facility name display
- Tidak ada breadcrumb
- Tidak responsive (mobile sidebar fixed, tidak collapsible)
- Active state pakai background fill (consumer pattern); seharusnya left-accent-bar untuk clinical

### 3.6 Empty/loading/error states (Important)
- Skeleton hanya 1 tempat (Encounter Detail)
- Empty state kosong/missing di banyak list (patient list, encounter list, study list)
- Error state generic (cuma `<p role="alert">`)

### 3.7 Accessibility (Important)
- Skip-to-content link: tidak ada
- Focus rings: pakai shadcn defaults (visible tapi tidak konsisten dengan brand)
- `prefers-reduced-motion`: tidak di-handle di CSS
- Print stylesheet: tidak ada (klinisi sering print summary pasien)
- Keyboard shortcuts: tidak ada (Ctrl+K untuk search, Esc, Ctrl+Enter)

### 3.8 Reliability (Important)
- ErrorBoundary tidak ada — satu component crash bisa bikin layar putih
- React Query devtools tidak terpasang (DX gap)

## 4. Per-Page Findings

### 4.1 `/login`
- LoginForm sudah pakai shadcn Form + zod (Sprint 2A H0)
- Page wrapper minimalis: tidak ada brand mark, tidak ada ECG motif aksen
- Tidak ada visible error envelope dari backend (cuma generic `<p role="alert">`)
- Verdict: small polish — tambah brand wordmark + ECG sweep aksen subtle bg

### 4.2 `/dashboard`
- Saat ini placeholder: `<div>Dashboard (Sprint 2+)</div>`
- Tidak ada konten sama sekali
- Verdict: butuh static placeholder yang lebih baik (informative empty state) sampai Sprint 7 (research dashboard real)

### 4.3 `/patients` (list)
- Table dengan masked names; pagination basic
- Tidak ada empty state untuk zero-patient case
- Tidak ada loading skeleton untuk table rows
- Search bar tidak punya keyboard hint (Ctrl+K)
- Verdict: tambah empty state, skeleton table, Ctrl+K hint

### 4.4 `/patients/new` (register)
- Form lengkap dengan zod validation
- Field grouping flat (semua field di satu kolom panjang); tidak ada section header
- Consent checkbox tidak punya helper text yang menjelaskan apa itu data_use consent
- Verdict: section grouping (Identitas / Kontak / Consent), helper text untuk legal field

### 4.5 `/patients/:id` (detail)
- Sekarang: stack vertical Card untuk Identitas, Kontak, Riwayat, Consent
- Tidak ada visual hierarchy untuk identity vs encounters
- Encounter list dan upload trigger tidak terhubung secara natural ke detail flow
- Verdict: medical-chart 2-col (identity sticky kiri, tabbed content kanan) — sudah locked di plan

### 4.6 `/patients/:id/encounters/new` (encounter create)
- Form simple: encounter_type select + chief_complaint textarea
- Verdict: minor polish, tidak prioritas pass-1

### 4.7 `/encounters/:id` (encounter detail)
- Sudah diisi Sprint 2A+2B: Card Encounter info, ContextForm, VitalsPanel, ECG section
- Card density tinggi tapi tidak ada section grouping yang jelas
- ECG upload pakai `<input type="file">` polos dengan client-validation; tidak ada drag-drop visual
- VitalsPanel pakai table 4-col + grid input — readable tapi tidak punya range indicator
- Verdict: ECG upload zone redesign (E2), Vitals mini-cards (E1), section grouping (D2 breadcrumb + header improvement)

## 5. Library Decisions (final)

### Already in repo (zero install)
`lucide-react`, `tailwindcss-animate`, `class-variance-authority`, `tailwind-merge`, `clsx`, `sonner`, `date-fns`, all `@radix-ui/*` via shadcn, `react-hook-form`, `zod`, TanStack Query, react-router-dom

### Add (npm install)
1. `react-error-boundary` — root + per-feature error fallback (clinical reliability)
2. `@fontsource-variable/inter` — self-hosted Inter (deployment realistik di Puskesmas low-bandwidth/offline)
3. `react-hotkeys-hook` — keyboard shortcuts (Ctrl+K, Esc, Ctrl+Enter)
4. `react-dropzone` — real drag-drop zone untuk ECG upload
5. `react-medium-image-zoom` — lightbox EKG preview

### Add (devDependency)
1. `@tanstack/react-query-devtools` — conditional dev-only import
2. `rollup-plugin-visualizer` — bundle audit pre-tag

### Add (shadcn primitives)
- `tabs` (Radix) — Patient Detail medical-chart
- `tooltip` (Radix) — quality badge metric breakdown
- `avatar` (Radix) — identity sidebar
- `dropdown-menu` (Radix) — header user menu
- `separator` (Radix) — header vertical divider

### Skip (defer ke pass-2 atau Sprint 3+)
- `@tanstack/react-table` — pagination simpel cukup
- `@tanstack/react-virtual` — belum perlu (list <100)
- `recharts`/`tremor` — dashboard real defer ke Sprint 7
- `cmdk` — command palette, defer
- `@react-pdf/renderer` — Sprint 6
- `framer-motion` — tailwindcss-animate cukup
- `react-resizable-panels` — defer ke pass-2
- Storybook — overkill untuk solo dev

## 6. Prioritized Improvements (Pass-1 Scope)

Diurutkan dari foundational ke polish. Setiap item = 1-3 commit kecil.

### Foundational (Phase C — must be first)

| ID | Item | Files | Effort | Priority |
|----|------|-------|--------|----------|
| C0 | Install runtime libraries (error-boundary, fontsource-inter, hotkeys, devtools) | package.json, main.tsx | S | High |
| C1 | Theme tokens ADR-0010 + ADR-0011 (petrol/charcoal scale, sharp radius, status palette) | index.css, tailwind.config.js | M | Critical |
| C2 | Typography rhythm (tabular nums, weight contrast, clinical line-height, h-rule accent) | index.css | S | High |
| C3 | Document-card override (radius 2px, border-strong, near-zero shadow, section-label slot) | components/ui/card.tsx | S | High |

### Domain character (Phase D — biggest impact)

| ID | Item | Files | Effort | Priority |
|----|------|-------|--------|----------|
| D1 | EcgSweep brand motif SVG component | components/brand/EcgSweep.tsx | S | High |
| D2 | AppShell upgrade (header + accent-bar nav + breadcrumb + skip-link + mobile sheet) | components/layout/AppShell.tsx, Header.tsx, Breadcrumb.tsx | M | Critical |
| D3 | EmptyState + QualityBadge + ECG-line shimmer skeleton | components/ui/empty-state.tsx, quality-badge.tsx | S | High |
| D4 | Patient Detail medical-chart 2-col (identity sidebar + tabs) | features/patient/PatientDetail.tsx, IdentitySidebar.tsx | M-L | Critical |

### Polish (Phase E)

| ID | Item | Files | Effort | Priority |
|----|------|-------|--------|----------|
| E1 | Vital signs mini-cards with range indicators | features/vital_signs/VitalsPanel.tsx | S | Medium |
| E2 | ECG upload zone redesign (react-dropzone + image-zoom) | features/ecg_study/EcgUploadForm.tsx, EcgStudyList.tsx | M | High |

### Quality pass (Phase G)

| ID | Item | Files | Effort | Priority |
|----|------|-------|--------|----------|
| G1 | Color contrast audit (axe + manual) on all 7 pages | (no code change, doc only) | S | High |
| G2 | Keyboard navigation pass (Ctrl+K, Esc, Ctrl+Enter, ?) | various form/list components | S | Medium |
| G3 | Print stylesheet for Patient Detail | index.css | S | Medium |
| G4 | prefers-reduced-motion + skip-to-content link | index.css, AppShell | S | High |
| G5 | Bundle visualizer dry-run + document size | vite.config.ts, README.md | S | Low |

## 7. Success Criteria (definition of done untuk pass-1)

- [ ] All 7 pages pakai theme petrol+charcoal token (no shadcn neutral gray on visible surfaces)
- [ ] Sharp radius (2px) di semua Card/Button/Input/Badge
- [ ] Tabular numerals di MRN, study_uid, vital signs, dates
- [ ] EcgSweep motif muncul di minimum 4 tempat (login bg, brand mark, empty state, loading)
- [ ] AppShell punya header dengan user menu + facility name + logout
- [ ] AppShell punya breadcrumb di main content area
- [ ] Sidebar pakai left-accent-bar (bukan bg-fill) untuk active state
- [ ] Mobile: sidebar collapsible via Sheet
- [ ] Patient Detail: medical-chart 2-col layout dengan tabs
- [ ] Vital signs: mini-cards dengan range indicator
- [ ] ECG upload: real drag-drop zone dengan preview
- [ ] EmptyState component dipakai di patient list, encounter list, study list (3+ tempat)
- [ ] QualityBadge dengan tooltip metric breakdown
- [ ] ErrorBoundary di root + Patient Detail + ECG section
- [ ] Self-hosted Inter (no Google Fonts CDN dependency)
- [ ] Skip-to-content link
- [ ] prefers-reduced-motion respected
- [ ] Print stylesheet for Patient Detail
- [ ] Color contrast 4.5:1 minimum (axe pass on 7 pages)
- [ ] Keyboard shortcuts: Ctrl+K (search), Esc (dialog close), Ctrl+Enter (form submit)
- [ ] All component tests still pass (existing 22 + minor adjustments OK)
- [ ] Frontend build clean (lint, typecheck, prettier, test, build)

## 8. Out of Scope (defer to pass-2 or later sprint)

- Dark mode (single theme dulu)
- Real dashboard with stats (Sprint 7 atau pass-2)
- Command palette / cmdk
- Storybook
- Patient list virtualization
- PDF report (Sprint 6)
- i18n EN strings (sudah hardcoded ID per ADR-0012; EN datang Sprint 5/6)
- Resizable panels
- Animation library (framer-motion)

## 9. References

- ADR-0010: Petrol+charcoal color system
- ADR-0011: Clinical-sharp border radius
- ADR-0012: Bilingual ID+EN output (defer EN ke sprint berikutnya)
- ADR-0013: Inferno heatmap colormap (untuk Sprint 4 HiResCAM, tidak dipakai pass-1)
- uipro skill: `.opencode/skills/ui-ux-pro-max/`
- Web design guidelines (existing skill at `~/.agents/skills/web-design-guidelines/`)
