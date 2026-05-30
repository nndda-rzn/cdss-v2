# Color System & Tokens Design - EKG-Insight CDSS v2

| Item | Keterangan |
| --- | --- |
| Dokumen | Color System & Design Tokens |
| Versi | 1.0 |
| Tanggal | 2026-05-30 |
| Status | Approved design |
| Mode | Light only |
| Referensi | architecture-overview-design.md |

## 1. Filosofi: Data-as-Protagonist

UI = canvas profesional yang tenang. Brand color (petrol blue) muncul minimal (top bar, logo, primary action). Visual hierarchy paling intens diserahkan ke signal klinis (triage RED/AMBER/GREEN) dan HiResCAM heatmap (inferno). Pendekatan ini meminimalkan visual noise, mengurangi cognitive load nakes shift panjang, dan memenuhi prinsip scientific visualization.

### Visual Hierarchy (intensitas tinggi ke rendah)

| Tier | Elemen | Warna |
| --- | --- | --- |
| 1 | Triage RED (MI High Risk) | Pure signal red |
| 2 | HiResCAM heatmap | Inferno gradient |
| 3 | Triage AMBER, primary action | Amber, petrol |
| 4 | Brand mark, nav active | Petrol blue |
| 5 | Card, body text, table | Charcoal scale |
| 6 | Background, secondary text | Off-white / soft charcoal |

## 2. Decision Matrix

| # | Topik | Keputusan |
| --- | --- | --- |
| P1 | Direction | Hybrid Petrol Blue + Charcoal |
| P2 | Petrol character | Balanced petrol (hue 200, sat 58%) |
| P3 | Heatmap colormap | Inferno (backend Python) |
| P4 | Triage signal | Strict pure clinical |
| P5 | Dark mode | Light only |
| P6 | Accent | No accent (austere) |
| P7 | Font | Inter + JetBrains Mono |
| - | Radius | Clinical-sharp (0/1/2/3/4/6/full) |
| - | Triage badge | Rectangular (2px), bukan pill |

## 3. Color Tokens

### 3.1 Brand (Petrol Blue, hue 195-210)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| brand.primary | hsl(200,58%,32%) | #225873 | Logo, nav active, primary action bg |
| brand.primary.hover | hsl(200,60%,26%) | #194A62 | Hover primary |
| brand.primary.active | hsl(200,62%,22%) | #143C50 | Pressed |
| brand.primary.subtle | hsl(200,40%,94%) | #E1ECF1 | Selected row, focus tint |
| brand.primary.border | hsl(200,45%,75%) | #A6C5D2 | Border subtle bg |

### 3.2 Surface (warm off-white + warm charcoal)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| surface.canvas | hsl(40,20%,98%) | #FAFAF7 | App background |
| surface.raised | hsl(0,0%,100%) | #FFFFFF | Card, modal body |
| surface.sunken | hsl(40,12%,95%) | #F2F1ED | Inset, disabled input |
| surface.input | hsl(0,0%,100%) | #FFFFFF | Input default |
| surface.muted | hsl(40,10%,96%) | #F5F4F1 | Hover row, secondary panel |

### 3.3 Border

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| border.subtle | hsl(40,8%,92%) | #EBEAE6 | Hairline divider |
| border.default | hsl(40,8%,86%) | #DCDAD3 | Card, input |
| border.strong | hsl(40,8%,70%) | #B6B3A8 | Emphasis |
| border.focus | brand.primary | #225873 | Focus ring |

### 3.4 Text (warm near-black)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| text.primary | hsl(40,20%,12%) | #221F1B | Heading, body |
| text.secondary | hsl(40,10%,35%) | #5E5953 | Secondary, label |
| text.tertiary | hsl(40,8%,50%) | #827E76 | Caption, metadata |
| text.disabled | hsl(40,5%,68%) | #AEABA5 | Disabled |
| text.placeholder | hsl(40,5%,60%) | #9B988F | Placeholder |
| text.on-brand | #FFFFFF | #FFFFFF | Text di atas brand |
| text.link | brand.primary | #225873 | Link inline |

### 3.5 Signal Danger (Triage RED, hue 0)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| signal.danger | hsl(0,72%,46%) | #CA2424 | Triage RED, error, High Risk |
| signal.danger.hover | hsl(0,75%,38%) | #A91919 | Destructive hover |
| signal.danger.subtle | hsl(0,80%,96%) | #FCE7E7 | Alert/banner bg |
| signal.danger.border | hsl(0,65%,60%) | #D86060 | Banner border |
| signal.danger.fg | #FFFFFF | #FFFFFF | Text di atas solid |
| signal.danger.fg-on-subtle | hsl(0,65%,28%) | #761818 | Text di atas subtle |

### 3.6 Signal Caution (Triage AMBER + Disclaimer, hue 38)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| signal.caution | hsl(38,92%,50%) | #F59E0B | Triage AMBER, warning |
| signal.caution.hover | hsl(38,92%,42%) | #CC8409 | Hover warning |
| signal.caution.subtle | hsl(38,95%,95%) | #FEF1DC | Disclaimer banner bg |
| signal.caution.border | hsl(38,80%,65%) | #F2C266 | Disclaimer border |
| signal.caution.fg | hsl(38,60%,18%) | #4A330B | Text di atas subtle |
| signal.caution.fg-on-solid | hsl(38,70%,12%) | #3A2706 | Text di atas solid |

### 3.7 Signal Success (Triage GREEN, hue 145 - 55deg gap dari petrol)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| signal.success | hsl(145,55%,36%) | #298551 | Triage GREEN, validated |
| signal.success.hover | hsl(145,58%,30%) | #1F6E42 | Hover success |
| signal.success.subtle | hsl(145,40%,94%) | #E0F0E7 | Success banner bg |
| signal.success.border | hsl(145,40%,65%) | #7EBD96 | Banner border |
| signal.success.fg | #FFFFFF | #FFFFFF | Text di atas solid |
| signal.success.fg-on-subtle | hsl(145,65%,18%) | #0F4A2A | Text di atas subtle |

### 3.8 Signal Info (SLATE low-sat - bukan blue agar tidak blur dengan brand)

| Token | HSL | Hex | Penggunaan |
| --- | --- | --- | --- |
| signal.info | hsl(220,12%,48%) | #6E7886 | Info icon, neutral status |
| signal.info.subtle | hsl(220,15%,95%) | #EEF0F4 | Info banner bg |
| signal.info.border | hsl(220,14%,75%) | #B5BAC5 | Border |
| signal.info.fg | #FFFFFF | #FFFFFF | Text di atas solid |
| signal.info.fg-on-subtle | hsl(220,25%,22%) | #2C3447 | Text di atas subtle |

### 3.9 Visualization

| Token | Nilai | Lokasi | Penggunaan |
| --- | --- | --- | --- |
| viz.heatmap.colormap | "inferno" | Backend Python | matplotlib.cm.inferno (HiResCAM) |
| viz.confidence.high | hsl(200,65%,38%) | Frontend | Bar penuh confidence |
| viz.confidence.low | hsl(200,35%,80%) | Frontend | Bar awal confidence |
| viz.chart.series.1 | hsl(200,58%,38%) | Frontend | Petrol (model 1) |
| viz.chart.series.2 | hsl(220,12%,45%) | Frontend | Slate (model 2) |
| viz.chart.series.3 | hsl(40,25%,55%) | Frontend | Warm grey (model 3) |
| viz.chart.grid | border.subtle | Frontend | Grid line |
| viz.chart.axis | text.tertiary | Frontend | Axis label |

### 3.10 Print (PDF Report)

| Token | Hex | Catatan |
| --- | --- | --- |
| print.text.primary | #1A1A1A | Solid black-ish |
| print.signal.danger | #C62828 | Muted avoid bleed |
| print.signal.caution | #E65100 | |
| print.signal.success | #2E7D32 | |
| print.brand.primary | #1F4F66 | Darker solid mark |

## 4. Spacing Tokens (4-base scale)

| Token | rem | px | Penggunaan |
| --- | --- | --- | --- |
| space.0 | 0 | 0 | - |
| space.px | - | 1 | Hairline |
| space.0.5 | 0.125 | 2 | Tight inline |
| space.1 | 0.25 | 4 | Icon-text gap |
| space.2 | 0.5 | 8 | Tight component |
| space.3 | 0.75 | 12 | Default inline |
| space.4 | 1 | 16 | Default padding |
| space.5 | 1.25 | 20 | Comfortable |
| space.6 | 1.5 | 24 | Card padding default |
| space.8 | 2 | 32 | Section gap |
| space.10 | 2.5 | 40 | Large gap |
| space.12 | 3 | 48 | Page section gap |
| space.16 | 4 | 64 | Hero |
| space.20 | 5 | 80 | Large hero |
| space.24 | 6 | 96 | Mega |

## 5. Typography Tokens

### 5.1 Font Family

| Token | Stack |
| --- | --- |
| font.sans | Inter, ui-sans-serif, system-ui, "Segoe UI", sans-serif |
| font.mono | "JetBrains Mono", ui-monospace, "Roboto Mono", monospace |
| font.print | Georgia, "Times New Roman", serif |

### 5.2 Font Size

| Token | rem | px | Penggunaan |
| --- | --- | --- | --- |
| text.xs | 0.75 | 12 | Metadata, audit timestamp |
| text.sm | 0.875 | 14 | Caption, table dense |
| text.base | 1.0 | 16 | Body default |
| text.md | 1.0625 | 17 | Body emphasized |
| text.lg | 1.125 | 18 | Lead body |
| text.xl | 1.25 | 20 | h5 |
| text.2xl | 1.5 | 24 | h4 |
| text.3xl | 1.875 | 30 | h3 |
| text.4xl | 2.25 | 36 | h2 page title |
| text.5xl | 3.0 | 48 | h1 (rare) |

### 5.3 Font Weight

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| weight.normal | 400 | Body |
| weight.medium | 500 | Emphasized inline |
| weight.semibold | 600 | Label, table header, button |
| weight.bold | 700 | Heading, badge |

### 5.4 Line Height

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| leading.none | 1 | Display |
| leading.tight | 1.25 | Heading |
| leading.snug | 1.375 | Sub-heading |
| leading.normal | 1.5 | Body |
| leading.relaxed | 1.625 | Rationale, recommendation |

### 5.5 Text Roles (semantic composition)

| Role | Komposisi |
| --- | --- |
| role.h1 | sans + 4xl + bold + tight + primary |
| role.h2 | sans + 3xl + bold + tight + primary |
| role.h3 | sans + 2xl + semibold + snug |
| role.body | sans + base + normal + normal + primary |
| role.label | sans + sm + semibold + wide + secondary |
| role.caption | sans + xs + normal + tertiary |
| role.value-numeric | mono + base + medium + primary |
| role.code-uid | mono + xs + tertiary |
| role.disclaimer | sans + sm + medium + relaxed + caution.fg |
| role.rationale | sans + base + normal + relaxed + primary |

## 6. Border Radius (Clinical-Sharp)

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| radius.none | 0 | Tabel, divider, header strip |
| radius.sm | 1px | Hairline tag |
| radius.default | 2px | Input, button, badge, triage badge |
| radius.md | 3px | Card medium, modal |
| radius.lg | 4px | Card large, panel section |
| radius.xl | 6px | Hero card (rare) |
| radius.full | 9999px | Avatar / circular icon only |

Pill shape (full) dilarang untuk badge/triage/status. Triage badge rectangular (radius.default).

## 7. Border Width

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| stroke.0 | 0 | None |
| stroke.1 | 1px | Default |
| stroke.2 | 2px | Focused, selected |
| stroke.4 | 4px | Banner left-accent |

## 8. Elevation / Shadow (subtle)

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| elevation.none | none | Flat default |
| elevation.xs | 0 1px 2px hsl(40 10% 12% / .04) | Subtle card |
| elevation.sm | 0 1px 3px /.06, 0 1px 2px /.04 | Raised card |
| elevation.md | 0 4px 8px /.08, 0 2px 4px /.04 | Popover, dropdown |
| elevation.lg | 0 10px 20px /.10, 0 4px 8px /.06 | Modal |
| elevation.xl | 0 20px 40px /.12, 0 8px 16px /.08 | Mega modal (rare) |
| elevation.focus | 0 0 0 2px brand.subtle, 0 0 0 4px brand | Focus ring |
| elevation.focus-danger | 0 0 0 2px danger.subtle, 0 0 0 4px danger | Focus error input |

## 9. Z-Index

| Token | Nilai | Lapisan |
| --- | --- | --- |
| z.base | 0 | Default |
| z.raised | 1 | Raised content |
| z.dropdown | 100 | Select dropdown |
| z.sticky | 200 | Sticky header |
| z.fixed | 300 | Fixed nav |
| z.modal-backdrop | 400 | Modal backdrop |
| z.modal | 500 | Modal content |
| z.popover | 600 | Popover, hovercard |
| z.tooltip | 700 | Tooltip |
| z.toast | 800 | Toast |
| z.dialog-critical | 900 | Critical dialog (disclaimer accept) |

## 10. Motion / Transition

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| duration.fast | 100ms | Hover, focus |
| duration.default | 150ms | Button, link |
| duration.slow | 250ms | Modal enter, drawer |
| duration.slower | 350ms | Page transition |
| easing.default | cubic-bezier(0.4,0,0.2,1) | Standard |
| easing.in | cubic-bezier(0.4,0,1,1) | Exit |
| easing.out | cubic-bezier(0,0,0.2,1) | Enter |

Tanpa spring/bouncy easing - clinical UI predictable.

## 11. Breakpoints & Density

| Token | Min Width | Penggunaan |
| --- | --- | --- |
| bp.md | 768px | Tablet ER/IGD |
| bp.lg | 1024px | Desktop Puskesmas default |
| bp.xl | 1280px | Layar besar |
| bp.2xl | 1536px | Dual-monitor |

| Density | Modifier | Penggunaan |
| --- | --- | --- |
| density.compact | -25% padding | History table, batch list |
| density.default | 100% | Standard |
| density.comfortable | +25% padding | Detail page |

Mobile-first (<640px) bukan prioritas - workflow CDSS tidak sesuai mobile.

## 12. Component Semantic Tokens

| Token | Komposisi |
| --- | --- |
| button.primary.bg | brand.primary |
| button.primary.fg | text.on-brand |
| button.primary.bg-hover | brand.primary.hover |
| button.secondary.bg | surface.raised |
| button.secondary.fg | text.primary |
| button.secondary.border | border.default |
| button.danger.bg | signal.danger |
| button.danger.fg | signal.danger.fg |
| button.ghost.fg | text.primary |
| button.ghost.bg-hover | surface.muted |
| card.bg | surface.raised |
| card.border | border.subtle |
| card.shadow | elevation.xs |
| card.radius | radius.lg |
| input.bg | surface.input |
| input.border | border.default |
| input.border-focus | brand.primary |
| input.bg-disabled | surface.sunken |
| input.radius | radius.default |
| triage.red.bg / fg / radius | signal.danger / danger.fg / radius.default |
| triage.amber.bg / fg / radius | signal.caution / caution.fg-on-solid / radius.default |
| triage.green.bg / fg / radius | signal.success / success.fg / radius.default |
| disclaimer.bg | signal.caution.subtle |
| disclaimer.border-accent | signal.caution (left 4px) |
| disclaimer.fg | signal.caution.fg |
| risk.low.bg / fg | signal.success.subtle / success.fg-on-subtle |
| risk.moderate.bg / fg | signal.caution.subtle / caution.fg |
| risk.high.bg / fg | signal.danger.subtle / danger.fg-on-subtle |
| risk.need-review.bg / fg | signal.info.subtle / info.fg-on-subtle |
| risk.uncertain.bg / fg | surface.muted / text.secondary |
| badge.radius / chip.radius | radius.default / radius.sm |
| avatar.radius | radius.full |

## 13. Clash-Avoidance Rulebook

| Aturan | Rasional |
| --- | --- |
| Petrol hue locked 195-210, sat 50-65% | Cegah blur dengan green (gap 55deg ke hue 145) |
| Triage RED tidak pernah overlay heatmap | Cegah dua merah kompetisi |
| Heatmap selalu di surface.raised + border + frame | Edge separation dari canvas |
| Signal.info pakai slate (sat 12%), bukan blue | Cegah blur dengan brand (sat 58%) |
| Result Page: signal di atas, heatmap di bawah, gap 32px | Mata baca top-down, signal lebih dulu |
| Saturation hierarchy: signal > brand > viz > surface | Severity konsisten |
| Mono font hanya numeric/technical values | Hindari console feeling |
| Triage badge solid fill + strong border | Tidak ter-mistake sebagai dekorasi |
| Canvas off-white (#FAFAF7), bukan #FFFFFF | Edge separation + eye fatigue |
| brand.* hanya di Brand/Logo/PrimaryAction/ActiveNav | Disiplin where blue belongs |
| Adjacent color pair delta-E >= 30 | Perceptual distinguishability |

### Verifikasi

| Risk | Status |
| --- | --- |
| Petrol 200 vs Success 145 | 55deg gap - aman |
| Petrol sat 58% vs Info sat 12% | Pemisahan saturation - aman |
| Heatmap inferno vs Triage RED | Spatial top/bottom + saturation - aman |
| Disclaimer subtle vs Triage AMBER solid | Subtle bg vs solid + border 4px - aman |
| Charcoal warm vs Amber | Warm shift 3-5%, amber sat 92% dominan - aman |
| Canvas vs heatmap edge | Canvas 98% L vs raised 100% + border - aman |

## 14. Backend Coordination (Heatmap)

Colormap inferno dirender di backend Python (`backend/app/services/hirescam/colormap.py`), bukan token frontend. Frontend hanya menampilkan PNG hasil via img tag. Token `viz.heatmap.colormap = "inferno"` hanya dokumentasi/referensi. Justifikasi: inferno perceptually uniform (Crameri et al. 2020), colorblind-safe, standard publikasi medical imaging.

## 15. Accessibility Constraints (WCAG)

| Komponen | Target | Catatan |
| --- | --- | --- |
| Body text | AA (4.5:1) | text.primary di canvas = lulus |
| Disclaimer banner | AAA (7:1) | Safety-critical, caution.fg di subtle |
| Triage badge | AAA (7:1) | fg di solid bg semua lulus |
| Secondary text | AA (4.5:1) | text.secondary di canvas |
| Caption | AA large (3:1) | text.tertiary minimal |
| Focus ring | 3:1 non-text | brand.primary ring |
| Triage tidak bergantung warna saja | - | Selalu + label text + icon (colorblind-safe) |

Setiap signal state WAJIB punya label text + icon, tidak hanya warna. Deuteranope/protanope tetap bisa bedakan via teks.

## 16. Implementasi Tailwind

```
frontend/src/styles/
  tokens/
    colors.ts          # primitif + semantic
    spacing.ts
    typography.ts
    radius.ts
    elevation.ts
    motion.ts
    z-index.ts
    breakpoints.ts
    index.ts
  globals.css          # CSS variables (density runtime)
  print.css            # PDF preview stylesheet
tailwind.config.ts     # import dari tokens/
```

Token diakses via class: bg-brand-primary, text-signal-danger-fg. Komponen shadcn override cn() binding ke semantic tokens (surface.*, text.*).

## 17. Justifikasi Naratif (Skripsi/Scopus)

Color system EKG-Insight dirancang dengan prinsip data-as-protagonist: brand color (petrol blue) minimal untuk identitas, surface neutral charcoal sebagai canvas non-kompetitif. Visual hierarchy paling intens diserahkan ke signal klinis (triage RED/AMBER/GREEN sesuai standar acute care) dan HiResCAM heatmap (inferno colormap, perceptually uniform per Crameri et al. 2020). Triage badge rectangular meniru triage tag fisik IGD. Sudut clinical-sharp (max 6px) memberi karakter instrument-grade. Pendekatan ini meminimalkan visual noise, mencegah cognitive load tambahan pada nakes shift panjang, mendukung colorblind-safe melalui label+icon, dan memenuhi prinsip scientific visualization dalam publikasi medical imaging.
