# AnalysisDetailPage — UI/UX Improvements

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve AnalysisDetailPage UX — move actions to top, remove duplication, add loading states, fix mobile responsiveness.

**Architecture:** Single page component rewrite + minor component tweaks. No backend changes.

**Tech Stack:** React + TanStack Query + Tailwind + Radix Select.

---

## File Structure

**Modify:**
- `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx` — main layout rewrite
- `frontend/src/features/ai_analysis/components/AnalysisDetailTable.tsx` — mobile responsive

---

### Task 1: Move actions to top + remove duplicate Back

**File:** `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`

- [ ] **Step 1: Move action bar to top**

Current layout:
```
[Back link]
[Header]
[ECG + HiResCAM]
[Table]
[Actions: Back, Print, ModelSelector, RunAI]
[Error]
```

New layout:
```
[Back link]
[Header]
[Actions: ModelSelector | RunAI | Print]  ← moved here, no Back button
[ECG + HiResCAM]
[Table]
[Error]
```

Move the action bar div to after `</header>`, before the ECG grid.

Remove the "Kembali" button — already have "Kembali ke Kunjungan" at top.

- [ ] **Step 2: Update button layout**

Action bar should be a horizontal flex row inside a bordered card:
```tsx
<div className="no-print flex flex-col gap-3 rounded-lg border bg-card p-3 sm:flex-row sm:items-center sm:justify-between">
  {/* Left: Model Selector */}
  <RoleGate allow={["clinician", "nurse"]}>
    <ModelSelector value={selectedModelId} onChange={setSelectedModelId} />
  </RoleGate>

  {/* Right: Print + Run AI */}
  <div className="flex items-center gap-2">
    <Button variant="outline" onClick={() => window.print()} className="cursor-pointer">
      <Printer className="mr-1.5 h-4 w-4" aria-hidden="true" />
      {t("Cetak", "Print")}
    </Button>
    <RoleGate allow={["clinician", "nurse"]}>
      <Button
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending || !selectedModelId}
        className="cursor-pointer"
      >
        <Sparkles className="mr-1.5 h-4 w-4" aria-hidden="true" />
        {mutation.isPending
          ? t("Menganalisis...", "Analysing...")
          : rows.length === 0
            ? t("Jalankan Analisis AI", "Run AI Analysis")
            : t("Analisis ulang", "Re-run analysis")}
      </Button>
    </RoleGate>
  </div>
</div>
```

- [ ] **Step 3: Verify no duplicate Back buttons**

Search file for "Kembali" — should only appear once (the top link).

- [ ] **Step 4: Commit**

---

### Task 2: Add loading skeleton + update subtitle

**File:** `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`

- [ ] **Step 1: Add loading skeleton for ECG + HiResCAM**

Replace `{study.data && (...)}` block with skeleton-aware version:
```tsx
<div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
  {study.isLoading ? (
    <Skeleton variant="ecg" className="h-80 w-full" />
  ) : study.data ? (
    <Card className="overflow-hidden">
      {/* ... existing ECG content ... */}
    </Card>
  ) : null}

  {hirescam.isLoading ? (
    <Skeleton variant="ecg" className="h-80 w-full" />
  ) : hirescam.data && hirescam.data.length > 0 ? (
    <Card className="overflow-hidden">
      {/* ... existing HiResCAM content ... */}
    </Card>
  ) : (
    <Card className="flex items-center justify-center">
      <CardContent className="py-6">
        <EmptyState ... />
      </CardContent>
    </Card>
  )}
</div>
```

- [ ] **Step 2: Add loading skeleton for table**

```tsx
<Card>
  <CardContent className="overflow-x-auto py-4">
    {analyses.isLoading ? (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} variant="ecg" className="h-9 w-full" />
        ))}
      </div>
    ) : rows.length === 0 ? (
      <EmptyState ... />
    ) : (
      <AnalysisDetailTable ... />
    )}
  </CardContent>
</Card>
```

- [ ] **Step 3: Update subtitle**

```
OLD: "Perbandingan lima model YOLO untuk studi EKG ini."
NEW: "Jalankan analisis AI untuk studi EKG ini."
```

- [ ] **Step 4: Typecheck** `cd frontend && npx tsc --noEmit`

- [ ] **Step 5: Commit**

---

### Task 3: Mobile-responsive table

**File:** `frontend/src/features/ai_analysis/components/AnalysisDetailTable.tsx`

- [ ] **Step 1: Hide probability columns on mobile**

In `<thead>`, add `hidden md:table-cell` to probability `<th>`:
```tsx
{CLASS_ORDER.map((c) => (
  <th key={c} className="hidden py-2 pr-3 text-right md:table-cell">
    {CLASS_LABEL[c].split(" ")[0]}
  </th>
))}
```

In `<tbody>`, add `hidden md:table-cell` to probability `<td>`:
```tsx
{CLASS_ORDER.map((c) => (
  <td key={c} className="hidden py-2 pr-3 text-right align-middle md:table-cell">
    <ProbCell value={row.probability_json[c]} />
  </td>
))}
```

- [ ] **Step 2: Typecheck** `cd frontend && npx tsc --noEmit`

- [ ] **Step 3: Commit**

---

### Task 4: Run all tests

- [ ] **Step 1: Frontend tests** `cd frontend && npx vitest run`
- [ ] **Step 2: Lint** `cd frontend && npx eslint src/`
- [ ] **Step 3: Fix any issues + commit if needed**
