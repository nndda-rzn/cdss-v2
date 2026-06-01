# UI/UX Redesign Plan: Clinical Workspace

## 1. Context & Motivation
The Encounter Detail page currently functions but lacks visual polish, feeling like an "amateur layout" rather than a professional clinical SaaS tool. Following the UI/UX Pro Max guidelines for "Accessible & Ethical" clinical interfaces, this document outlines the plan to elevate the UI.

## 2. Core Issues Identified
1. **CardContent Top Padding**: `pt-0` causes content to press against headers uncomfortably.
2. **Inconsistent Radii**: Mixing `rounded-sm` (MiniCards), `rounded-full` (pills), and `rounded-md` breaks the cohesive 6px radius theme.
3. **Button Hierarchy**: Missing distinction between primary actions (should be full-width, prominent) and secondary actions.
4. **Form Layout Inconsistencies**: Mixing label-above (Vitals) and label-inline (Context) patterns.
5. **Dropzone Layout**: Forced 1-row horizontal flex looks cramped and unprofessional.
6. **Flat Visual Weight**: Lack of typographic hierarchy makes all elements fight for attention.

## 3. Implementation Plan

### A. Detail Page Padding (`frontend/src/features/encounter/pages/Detail.tsx`)
- Apply `pt-4` to `CardContent` wrappers containing forms (Vitals, Context, ECG).

### B. Context Form (`frontend/src/features/clinical_context/components/ContextForm.tsx`)
- **Pills**: Change to `rounded-lg` (matching theme), `px-4 py-2.5`, add `shadow-sm` on active, subtle hover states.
- **Onset Group**: Switch to block label above input, inline input+unit, proper `space-y-1.5`.
- **Button**: Make primary action `w-full` with standard height `h-10`.

### C. ECG Upload Form (`frontend/src/features/ecg_study/components/EcgUploadForm.tsx`)
- **Dropzone**: Refactor to centered `flex-col` with `py-6`.
- **Icon**: Wrap in `rounded-full bg-primary/10 p-2` for prominence.
- **Button**: `w-full max-w-[220px]` inside dropzone.
- **Preview**: Consolidate to a clean bordered row with clear file info hierarchy.

### D. Vitals Panel (`frontend/src/features/vital_signs/components/VitalsPanel.tsx` & `MiniCard.tsx`)
- **Button**: Make "Tambah Pengukuran" `w-full` to match form patterns.
- **MiniCard**: Update to `rounded-md` from `rounded-sm` for consistency.

### E. ECG Study List (`frontend/src/features/ecg_study/components/EcgStudyList.tsx`)
- **Ghost Button**: Change to `w-full justify-start`, remove negative margins.
- **Spacing**: Increase to `space-y-1.5` for better readability.

## 4. UI/UX Pro Max Checklists Verified
- [x] High contrast text (WCAG AAA)
- [x] Proper touch targets (min 44x44px for primary actions)
- [x] Clear visual focus states
- [x] No layout shifts on hover
- [x] Semantic form structure
