# HiResCAM Path Fix Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix double `heatmaps/heatmaps/` path in heatmap URLs, plus fix clinical-context 404 and analyze 500 errors.

**Architecture:** Backend path storage fix + frontend URL safe guard + re-run backfill script + diagnose other endpoint errors.

**Tech Stack:** Flask, React 18, TypeScript, SQLite

---

## Issues Found

| # | Error | URL | Root Cause |
|---|-------|-----|------------|
| 1 | 404 | `/api/heatmaps/heatmaps/21/overlay.png` | Double path prefix — backend stores `heatmaps/21/...`, frontend adds `/api/heatmaps/` → double `heatmaps/` |
| 2 | 404/401 | `/api/encounters/4/clinical-context` | Endpoint may not exist or auth issue |
| 3 | 500 | `/api/encounters/4/ecg-studies/5/analyze` | Analysis endpoint failing (likely model loading or HiResCAM generation error) |

---

## Root Cause: Double Path

Backend `orchestrate.py` stores paths relative to `STORAGE_DIR`:
```python
heatmap_path=str(heatmap_path.relative_to(storage_root))
# → "heatmaps/21/heatmap.png"
```

Frontend `api.ts` adds `/api/heatmaps/` prefix:
```typescript
export function heatmapUrl(path: string): string {
  return `/api/heatmaps/${path}`;  // → "/api/heatmaps/heatmaps/21/heatmap.png" ❌
}
```

Backend API endpoint serves from `STORAGE_DIR`:
```python
full_path = storage_root / filepath  # → storage/heatmaps/heatmaps/21/heatmap.png ❌
```

---

### Task 1: Backend — Fix path storage

**Files:**
- Modify: `backend/app/services/hirescam/orchestrate.py:70-87`

- [ ] **Step 1: Change artifact path storage**

In `backend/app/services/hirescam/orchestrate.py`, modify `generate_artifacts()`:

```python
# BEFORE (lines ~70-87):
        artifact_dir = _artifact_dir(storage_root, analysis.id)
        heatmap_path = artifact_dir / "heatmap.png"
        overlay_path = artifact_dir / "overlay.png"
        side_by_side_path = artifact_dir / "side_by_side.png"

        heatmap_path.parent.mkdir(parents=True, exist_ok=True)
        heatmap_path.write_bytes(heatmap_png)
        overlay_path.write_bytes(overlay_png)
        side_by_side_path.write_bytes(side_by_side_png)

        artifact = HiResCAMArtifact(
            ai_analysis_id=analysis.id,
            heatmap_path=str(heatmap_path.relative_to(storage_root)),
            overlay_path=str(overlay_path.relative_to(storage_root)),
            side_by_side_path=str(side_by_side_path.relative_to(storage_root)),
            ...
        )

# AFTER:
        # Store paths relative to STORAGE_DIR/heatmaps (not STORAGE_DIR)
        # So paths are "21/heatmap.png" not "heatmaps/21/heatmap.png"
        heatmap_dir = storage_root / "heatmaps" / str(analysis.id)
        heatmap_dir.mkdir(parents=True, exist_ok=True)

        heatmap_path = heatmap_dir / "heatmap.png"
        overlay_path = heatmap_dir / "overlay.png"
        side_by_side_path = heatmap_dir / "side_by_side.png"

        heatmap_path.write_bytes(heatmap_png)
        overlay_path.write_bytes(overlay_png)
        side_by_side_path.write_bytes(side_by_side_png)

        artifact = HiResCAMArtifact(
            ai_analysis_id=analysis.id,
            heatmap_path=str(heatmap_path.relative_to(heatmap_dir.parent)),
            overlay_path=str(overlay_path.relative_to(heatmap_dir.parent)),
            side_by_side_path=str(side_by_side_path.relative_to(heatmap_dir.parent)),
            explanation_status=status,
            focus_metric=focus_metric,
            colormap_used="inferno",
        )
```

Also update `_artifact_dir` function:

```python
# BEFORE:
def _artifact_dir(storage_root: Path, analysis_id: int) -> Path:
    return storage_root / "heatmaps" / str(analysis_id)

# AFTER (or delete if no longer needed):
def _artifact_dir(storage_root: Path, analysis_id: int) -> Path:
    """Returns directory relative to STORAGE_DIR/heatmaps."""
    return Path(str(analysis_id))
```

- [ ] **Step 2: Verify paths are correct**

Check that the new stored paths are `21/heatmap.png` format:
```bash
python -c "import sqlite3; conn=sqlite3.connect('data/cdss.db'); cur=conn.cursor(); cur.execute('SELECT heatmap_path FROM hirescam_artifact LIMIT 3'); [print(f'  {r[0]}') for r in cur.fetchall()]"
```
Expected: `21/heatmap.png` (not `heatmaps/21/heatmap.png`)

- [ ] **Step 3: Run linting**

```bash
cd backend
ruff check app/services/hirescam/orchestrate.py
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/hirescam/orchestrate.py
git commit -m "fix(hirescam): store artifact paths relative to heatmaps dir, not storage root"
```

---

### Task 2: Backend — Re-run backfill script

**Files:**
- Modify: `backend/scripts/generate_hirescam_existing.py` (minor)

- [ ] **Step 1: Delete existing artifacts**

Since we're re-generating with correct paths, first delete the old ones:

```bash
python -c "import sqlite3; conn=sqlite3.connect('data/cdss.db'); cur=conn.cursor(); cur.execute('DELETE FROM hirescam_artifact'); conn.commit(); print(f'Deleted {cur.rowcount} artifacts')"
```
Expected: `Deleted 25 artifacts`

- [ ] **Step 2: Re-run backfill script**

```bash
cd backend
python scripts/generate_hirescam_existing.py
```
Expected: 25 artifacts regenerated with correct paths

- [ ] **Step 3: Verify correct paths**

```bash
python -c "import sqlite3; conn=sqlite3.connect('data/cdss.db'); cur=conn.cursor(); cur.execute('SELECT heatmap_path FROM hirescam_artifact LIMIT 5'); [print(f'  {r[0]}') for r in cur.fetchall()]"
```
Expected: `21/heatmap.png`, `22/heatmap.png`, etc. (no `heatmaps/` prefix)

- [ ] **Step 4: Verify heatmap files exist**

```bash
Test-Path "storage/heatmaps/21/overlay.png"
```
Expected: `True`

- [ ] **Step 5: Commit**

No code change needed — this is data migration. Document in PR body.

---

### Task 3: Frontend — Add URL safe guard

**Files:**
- Modify: `frontend/src/features/ai_analysis/api.ts`

- [ ] **Step 1: Fix heatmapUrl function**

In `frontend/src/features/ai_analysis/api.ts`:

```diff
export function heatmapUrl(path: string): string {
-   return `/api/heatmaps/${path}`;
+   // Backend stores paths relative to STORAGE_DIR/heatmaps (e.g. "21/overlay.png")
+   // Strip any leading "heatmaps/" for backwards compatibility with old data
+   const cleanPath = path.replace(/^heatmaps\//, "");
+   return `/api/heatmaps/${cleanPath}`;
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd frontend
npm run typecheck
```

- [ ] **Step 3: Run frontend tests**

```bash
cd frontend
npm run test -- --run
```
Expected: 39 tests pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/ai_analysis/api.ts
git commit -m "fix(hirescam): strip leading heatmaps/ prefix in heatmapUrl for safety"
```

---

### Task 4: Diagnose clinical-context 404/401

**Files:**
- Investigate: `backend/app/api/clinical_context.py`
- Investigate: `frontend/src/features/clinical_context/`

- [ ] **Step 1: Check if clinical context endpoint exists**

```bash
grep -r "clinical-context" backend/app/api/ | head -5
```

- [ ] **Step 2: Check if auth is the issue**

The 401 might be because the user session expired. Check if other authenticated endpoints work.

- [ ] **Step 3: If endpoint missing, document as known issue**

This is likely a pre-existing issue, not related to HiResCAM fix.

---

### Task 5: Diagnose analyze 500 error

**Files:**
- Investigate: `backend/app/api/ai_analysis.py`
- Investigate: `backend/app/services/inference/orchestrate.py`

- [ ] **Step 1: Check backend logs**

```bash
# Check if there's a Flask log file
Get-Content "$env:TEMP\*.log" -Tail 50 2>$null | Select-String -Pattern "error|exception|traceback" -CaseSensitive:$false | Select-Object -Last 10
```

- [ ] **Step 2: Test analyze endpoint manually**

```bash
# Login first
$resp = curl -s -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"email":"dokter@demo.id","password":"StrongPass1"}'
$token = ($resp | ConvertFrom-Json).access_token

# Try analyze
curl -s -X POST http://localhost:5000/api/encounters/4/ecg-studies/5/analyze -H "Authorization: Bearer $token" -H "Content-Type: application/json"
```

- [ ] **Step 3: If HiResCAM generation is causing the 500, wrap it better**

The try/except in `orchestrate.py` should catch HiResCAM errors. If it's still throwing 500, the error is elsewhere (likely inference itself).

---

### Task 6: Full gate verification + PR update

- [ ] **Step 1: Run full backend gate**

```bash
cd backend
pytest tests -v 2>&1 | Select-String -Pattern "passed|failed" | Select-Object -Last 1
ruff check . 2>&1 | Select-Object -Last 1
mypy . 2>&1 | Select-Object -Last 1
```

- [ ] **Step 2: Run full frontend gate**

```bash
cd frontend
npm run typecheck && npm run lint && npm run test -- --run && npm run build
```

- [ ] **Step 3: Push to existing PR**

```bash
git push origin fix/sprint-4/hirescam-generation
```

- [ ] **Step 4: Update PR body with new changes**

Add to PR #27 description:
```
### Additional fixes:
- Fix double `heatmaps/heatmaps/` path in heatmap URLs
- Store artifact paths relative to `STORAGE_DIR/heatmaps` (not `STORAGE_DIR`)
- Re-generated 25 HiResCAM artifacts with correct paths
- Added safe guard in `heatmapUrl()` for backwards compatibility
```

---

## Git Flow

| Item | Value |
|------|-------|
| Branch | `fix/sprint-4/hirescam-generation` (existing) |
| New commits | 3-4 more on same branch |
| PR | #27 (update existing) |
| Cooldown | Still 24h from original PR creation |

---

## Self-Review

### 1. Issue coverage

| Error | Task |
|-------|------|
| Double heatmap path | Task 1 + 2 + 3 |
| Clinical context 404/401 | Task 4 |
| Analyze 500 | Task 5 |
| Full verification | Task 6 |

### 2. No placeholders

All steps contain actual code, commands, and expected output.

### 3. Backwards compatibility

The frontend safe guard (`path.replace(/^heatmaps\//, "")`) ensures old data with `heatmaps/` prefix still works while new data uses clean paths.

---

## Execution Handoff

Plan complete. Two execution options:

**1. Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
