# HiResCAM Bug Fix Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix HiResCAM generation bug (`model.args` dict access), regenerate artifacts for existing analyses, and improve frontend UX.

**Architecture:** 4 fixes across backend generator + migration script + frontend query invalidation + empty state UI.

**Tech Stack:** PyTorch, Ultralytics YOLO, Flask, React 18, TypeScript

---

## Root Cause

`backend/app/services/hirescam/generator.py:135` — `model.args` pada YOLO model adalah **dict**, bukan namespace object:

```python
transforms = classify_transforms(model.args.imgsz)  # AttributeError: 'dict' object has no attribute 'imgsz'
```

Error ini di-catch di `generate_artifacts()` try/except yang return None silently → **0 artifacts dari 25 success analyses**.

---

### Task 1: Fix dict access bug in generator

**Files:**
- Modify: `backend/app/services/hirescam/generator.py:130-135`

- [ ] **Step 1: Fix the dict access**

In `backend/app/services/hirescam/generator.py`, replace the `_preprocess_for_model` function's transforms line:

```diff
-     transforms = classify_transforms(model.args.imgsz)
+     imgsz = model.args.get("imgsz", 224) if isinstance(model.args, dict) else getattr(model.args, "imgsz", 224)
+     transforms = classify_transforms(imgsz)
```

This handles both dict and namespace `model.args` formats across YOLO versions.

- [ ] **Step 2: Verify fix works**

Run in `backend/`:
```bash
python -c "from app.services.hirescam.generator import generate_hirescam; from ultralytics import YOLO; m = YOLO('models/yolov8n_cls/best.pt'); h = generate_hirescam(m, 'storage/uploads/ecg/1/1/ECG-P1-20260601101633-2b94.jpg', 3, device='cpu'); print(f'Shape: {h.shape}, min: {h.min():.3f}, max: {h.max():.3f}')"
```
Expected: `Shape: (H, W), min: 0.000, max: 1.000` (no error)

- [ ] **Step 3: Run unit tests**

Run in `backend/`:
```bash
pytest tests/unit/services/hirescam/test_generator.py -v
```
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/hirescam/generator.py
git commit -m "fix(hirescam): fix model.args dict access in generator"
```

---

### Task 2: Create and run migration script for existing analyses

**Files:**
- Create: `backend/scripts/generate_hirescam_existing.py`

- [ ] **Step 1: Create the script**

Create `backend/scripts/generate_hirescam_existing.py`:

```python
"""Generate HiResCAM artifacts for existing AIAnalysis rows missing them.

Run after the generator bug fix to backfill HiResCAM for studies analyzed
before the fix was deployed.
"""
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_analysis import AIAnalysis
from app.db.models.hirescam_artifact import HiResCAMArtifact
from app.services.hirescam.orchestrate import generate_for_study
from app.paths import default_database_url, STORAGE_DIR, MODEL_DIR


def main():
    from app.db.engine import create_db_engine

    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        # Find studies with success analyses
        studies_with_success = list(
            s.scalars(
                select(AIAnalysis.ecg_study_id)
                .where(AIAnalysis.status == "success")
                .distinct()
            ).all()
        )

        print(f"Studies with success analyses: {len(studies_with_success)}")

        total_artifacts = 0
        for study_id in studies_with_success:
            artifacts = generate_for_study(
                s,
                study_id=study_id,
                storage_root=Path(STORAGE_DIR),
                model_dir=Path(MODEL_DIR),
            )
            s.commit()
            total_artifacts += len(artifacts)
            print(f"  Study {study_id}: generated {len(artifacts)} artifacts")

        print(f"\nTotal: {total_artifacts} artifacts generated across {len(studies_with_success)} studies")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

Run in `backend/`:
```bash
python scripts/generate_hirescam_existing.py
```
Expected: Output showing artifacts generated per study, e.g.:
```
Studies with success analyses: 5
  Study 1: generated 5 artifacts
  Study 2: generated 5 artifacts
  ...
Total: 25 artifacts generated across 5 studies
```

- [ ] **Step 3: Verify in database**

Run:
```bash
python -c "import sqlite3; conn=sqlite3.connect('data/cdss.db'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM hirescam_artifact'); print(f'HiResCAM artifacts: {cur.fetchone()[0]}')"
```
Expected: `HiResCAM artifacts: 25` (matching the 25 success analyses)

- [ ] **Step 4: Commit**

```bash
git add backend/scripts/generate_hirescam_existing.py
git commit -m "feat(hirescam): add backfill script for existing analyses"
```

---

### Task 3: Frontend — Invalidate hirescam query after re-run

**Files:**
- Modify: `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx:58-61`

- [ ] **Step 1: Update mutation onSuccess**

In `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`, replace lines 58-61:

```diff
  const mutation = useMutation({
    mutationFn: () => runAnalysis(id, studyId),
-   onSuccess: () => qc.invalidateQueries({ queryKey: analysisKeys.list(id, studyId) }),
+   onSuccess: () => {
+     qc.invalidateQueries({ queryKey: analysisKeys.list(id, studyId) });
+     qc.invalidateQueries({ queryKey: hirescamKeys.study(id, studyId) });
+   },
  });
```

This ensures the HiResCAM section refreshes automatically after re-running analysis.

- [ ] **Step 2: Verify TypeScript compiles**

Run in `frontend/`:
```bash
npm run typecheck
```
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx
git commit -m "fix(hirescam): invalidate hirescam query after re-run analysis"
```

---

### Task 4: Frontend — EmptyState for missing HiResCAM

**Files:**
- Modify: `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx:112-136`

- [ ] **Step 1: Add EmptyState import**

In `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`, ensure `EmptyState` is imported (it should already be from line 7):

```tsx
import { EmptyState } from "@/components/ui/empty-state";
```

- [ ] **Step 2: Replace HiResCAM section with conditional rendering**

Replace lines 112-136:

```diff
-     {/* HiResCAM section */}
-     {hirescam.data && hirescam.data.length > 0 && (
-       <div className="space-y-4">
-         <header className="flex items-center justify-between">
-           <h2 className="text-lg font-semibold tracking-tight">
-             {t("Penjelasan Visual", "Visual Explanation")}
-           </h2>
-           {hirescam.data[0] && (
-             <ExplanationStatusBadge
-               status={hirescam.data[0].explanation_status}
-               focusMetric={hirescam.data[0].focus_metric}
-             />
-           )}
-         </header>
-         <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
-           {hirescam.data.map((hc: HiResCAMRow) => (
-             <HeatmapViewer
-               key={hc.ai_analysis_id}
-               artifact={hc}
-               originalPath={study.data?.image_original_path ?? ""}
-             />
-           ))}
-         </div>
-       </div>
-     )}
+     {/* HiResCAM section */}
+     {hirescam.data && hirescam.data.length > 0 ? (
+       <div className="space-y-4">
+         <header className="flex items-center justify-between">
+           <h2 className="text-lg font-semibold tracking-tight">
+             {t("Penjelasan Visual", "Visual Explanation")}
+           </h2>
+           <ExplanationStatusBadge
+             status={hirescam.data[0].explanation_status}
+             focusMetric={hirescam.data[0].focus_metric}
+           />
+         </header>
+         <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
+           {hirescam.data.map((hc: HiResCAMRow) => (
+             <HeatmapViewer
+               key={hc.ai_analysis_id}
+               artifact={hc}
+               originalPath={study.data?.image_original_path ?? ""}
+             />
+           ))}
+         </div>
+       </div>
+     ) : (
+       <Card>
+         <CardContent className="py-6">
+           <EmptyState
+             title={t("HiResCAM belum tersedia", "HiResCAM not yet available")}
+             description={t(
+               "Klik 'Analisis ulang' untuk generate penjelasan visual.",
+               "Click 'Re-run analysis' to generate visual explanation.",
+             )}
+             hideMotif
+           />
+         </CardContent>
+       </Card>
+     )}
```

This provides clear feedback when HiResCAM data is not available, with guidance on how to generate it.

- [ ] **Step 3: Verify TypeScript compiles**

Run in `frontend/`:
```bash
npm run typecheck
```
Expected: No errors

- [ ] **Step 4: Run frontend tests**

Run in `frontend/`:
```bash
npm run test -- --run
```
Expected: All pass (39 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx
git commit -m "feat(hirescam): add EmptyState for missing HiResCAM data"
```

---

### Task 5: Full gate verification

- [ ] **Step 1: Run full backend gate**

Run in `backend/`:
```bash
pytest tests -v 2>&1 | Select-String -Pattern "passed|failed" | Select-Object -Last 1
ruff check . 2>&1 | Select-Object -Last 1
mypy . 2>&1 | Select-Object -Last 1
```

- [ ] **Step 2: Run full frontend gate**

Run in `frontend/`:
```bash
npm run typecheck && npm run lint && npm run test -- --run && npm run build
```

- [ ] **Step 3: Final commit**

```bash
git commit --allow-empty -m "chore: HiResCAM bug fix complete"
```

---

## Git Flow

| Item | Value |
|------|-------|
| Branch | `fix/sprint-4/hirescam-generation` |
| PR title | `fix(hirescam): fix generator dict access, backfill artifacts, improve UI` |
| Labels | `type/fix`, `area/hirescam`, `sprint-4`, `size/m` |
| Cooldown | 24h (size/m) |

### Execution Sequence

```
1.  git switch main && git pull
2.  git switch -c fix/sprint-4/hirescam-generation
3.  Task 1: Fix generator bug + commit
4.  Task 2: Create backfill script + run + commit
5.  Task 3: Frontend query invalidation + commit
6.  Task 4: Frontend EmptyState + commit
7.  Task 5: Full gate verification
8.  git push -u origin fix/sprint-4/hirescam-generation
9.  Open PR
10. Wait 24h cooldown
11. Squash merge
```

---

## Self-Review

### 1. Spec coverage

| Issue | Task |
|-------|------|
| Dict access bug | Task 1 |
| Missing artifacts for existing analyses | Task 2 |
| Frontend not refreshing after re-run | Task 3 |
| No feedback when HiResCAM missing | Task 4 |
| Full verification | Task 5 |

### 2. No placeholders

All steps contain actual code, commands, and expected output.

### 3. Type consistency

- `hirescamKeys.study(id, studyId)` matches the query key factory defined in Task 9 of the Sprint 4 plan
- `generate_for_study()` signature matches the existing function in `hirescam/orchestrate.py`
- All imports verified against existing code

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-01-hirescam-bug-fix.md`. Two execution options:

**1. Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
