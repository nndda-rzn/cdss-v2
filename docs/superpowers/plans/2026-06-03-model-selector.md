# Model Selector + Visual Explanation Layout

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** (1) Single-select model dropdown for AI analysis, (2) simplify visual explanation to left-right: original ECG + HiResCAM overlay.

**Architecture:** Backend: add `GET /api/models`, modify `POST /analyze` to accept `model_ids`. Frontend: Radix Select dropdown + inline left-right image layout (no separate HeatmapViewer/StudyHeaderCard).

**Tech Stack:** Flask + SQLAlchemy (backend), React + TanStack Query + Tailwind + Radix Select (frontend).

---

## File Structure

**Create:**
- `backend/app/api/models.py`
- `backend/tests/unit/api/test_models.py`
- `backend/tests/unit/api/test_analyze_model_ids.py`

**Modify:**
- `backend/app/api/__init__.py` — register models blueprint
- `backend/app/api/ai_analysis.py` — accept `model_ids` from body
- `backend/app/services/inference/orchestrate.py` — accept optional `model_ids`
- `backend/app/services/model_registry/query.py` — add `list_models_by_ids()`
- `frontend/src/features/ai_analysis/types.ts` — add `ModelOption`
- `frontend/src/features/ai_analysis/api.ts` — add `fetchModels()`, update `runAnalysis()`
- `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx` — dropdown + left-right layout

**Delete (unused after refactor):**
- `frontend/src/features/ai_analysis/components/HeatmapViewer.tsx`
- `frontend/src/features/ai_analysis/components/StudyHeaderCard.tsx`
- `frontend/src/features/ai_analysis/components/ExplanationStatusBadge.tsx`

---

### Task 1: Backend — List available models endpoint

**Files:**
- Create: `backend/app/api/models.py`
- Modify: `backend/app/api/__init__.py`
- Create: `backend/tests/unit/api/test_models.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/unit/api/test_models.py
from tests.conftest import _auth_headers


def test_models_list_requires_auth(client):
    resp = client.get("/api/models")
    assert resp.status_code in (401, 403)


def test_models_list_returns_all_models(client, admin_token, seed_models):
    resp = client.get("/api/models", headers=_auth_headers(admin_token))
    assert resp.status_code == 200
    body = resp.get_json()
    assert "items" in body
    assert len(body["items"]) >= 1
    item = body["items"][0]
    assert "id" in item
    assert "model_name" in item
    assert "is_active" in item
```

- [ ] **Step 2: Run test → FAIL (404)**

Run: `cd backend && python -m pytest tests/unit/api/test_models.py -v`

- [ ] **Step 3: Implement endpoint**

```python
# backend/app/api/models.py
"""Model listing endpoint: returns all registered models for selection."""
from flask import Blueprint, Response, jsonify
from sqlalchemy import select

from app.api._shared import session
from app.core.rbac.decorators import require_role
from app.core.rbac.roles import Role
from app.db.models.model_metadata import ModelMetadata

bp = Blueprint("models", __name__, url_prefix="/api/models")


@bp.get("")
@require_role(Role.CLINICIAN, Role.NURSE, Role.ADMIN)
def list_models() -> Response:
    s = session()
    models = list(
        s.scalars(select(ModelMetadata).order_by(ModelMetadata.id)).all()
    )
    items = [
        {
            "id": m.id,
            "model_name": m.model_name,
            "model_version": m.model_version,
            "architecture": m.architecture,
            "is_active": m.is_active,
        }
        for m in models
    ]
    return jsonify(items=items)
```

Register in `__init__.py`: `from app.api.models import bp as models_bp` + `app.register_blueprint(models_bp)`.

- [ ] **Step 4: Run test → PASS**

- [ ] **Step 5: Commit**

---

### Task 2: Backend — Accept `model_ids` in analyze endpoint

**Files:**
- Modify: `backend/app/services/model_registry/query.py`
- Modify: `backend/app/services/inference/orchestrate.py`
- Modify: `backend/app/api/ai_analysis.py`
- Create: `backend/tests/unit/api/test_analyze_model_ids.py`

- [ ] **Step 1: Add `list_models_by_ids` to query.py**

```python
def list_models_by_ids(session: Session, model_ids: list[int]) -> list[ModelMetadata]:
    if not model_ids:
        return list_active_models(session)
    return list(
        session.scalars(
            select(ModelMetadata)
            .where(ModelMetadata.id.in_(model_ids))
            .order_by(ModelMetadata.id)
        ).all()
    )
```

- [ ] **Step 2: Modify `orchestrate.py`**

Add `model_ids: list[int] | None = None` param to `analyze_study()`. Replace `list_active_models(session)` → `list_models_by_ids(session, model_ids or [])`.

- [ ] **Step 3: Modify `ai_analysis.py`**

Parse body: `body = request.get_json(silent=True) or {}`, `model_ids = body.get("model_ids")`, validate list or None, pass to `analyze_study()`. Add `from flask import request`.

- [ ] **Step 4: Write tests + verify**

```python
# backend/tests/unit/api/test_analyze_model_ids.py
from tests.conftest import _auth_headers


def test_analyze_without_model_ids_backward_compat(client, clinician_token, seed_models):
    resp = client.post(
        "/api/encounters/1/ecg-studies/1/analyze",
        headers=_auth_headers(clinician_token),
    )
    assert resp.status_code != 400


def test_analyze_with_single_model_id(client, clinician_token, seed_models):
    resp = client.post(
        "/api/encounters/1/ecg-studies/1/analyze",
        headers=_auth_headers(clinician_token),
        json={"model_ids": [1]},
    )
    assert resp.status_code != 400


def test_analyze_with_invalid_model_ids_fallback(client, clinician_token, seed_models):
    resp = client.post(
        "/api/encounters/1/ecg-studies/1/analyze",
        headers=_auth_headers(clinician_token),
        json={"model_ids": "not-a-list"},
    )
    assert resp.status_code != 400
```

- [ ] **Step 5: Run tests + commit**

---

### Task 3: Frontend — Radix Select dropdown

**Files:**
- Modify: `frontend/src/features/ai_analysis/types.ts`
- Modify: `frontend/src/features/ai_analysis/api.ts`
- Modify: `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`

- [ ] **Step 1: Add `ModelOption` type**

```typescript
// types.ts — add at bottom
export interface ModelOption {
  id: number;
  model_name: string;
  model_version: string;
  architecture: string;
  is_active: boolean;
}
```

- [ ] **Step 2: Update api.ts**

```typescript
export const modelKeys = {
  list: () => ["models"] as const,
};

export async function fetchModels(): Promise<ModelOption[]> {
  const resp = await apiFetch("/api/models");
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error?.message_id ?? "Gagal memuat model");
  return body.items as ModelOption[];
}

export async function runAnalysis(
  encounterId: string,
  studyId: string,
  modelIds?: number[],
): Promise<void> {
  const resp = await apiFetch(`/api/encounters/${encounterId}/ecg-studies/${studyId}/analyze`, {
    method: "POST",
    body: modelIds && modelIds.length > 0
      ? JSON.stringify({ model_ids: modelIds })
      : undefined,
    headers: modelIds && modelIds.length > 0
      ? { "Content-Type": "application/json" }
      : undefined,
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.error?.message_id ?? "Gagal menjalankan analisis AI");
  }
}
```

- [ ] **Step 3: Add dropdown to AnalysisDetailPage.tsx**

Add imports:
```typescript
import { useState, useEffect } from "react";
import { modelKeys, fetchModels } from "../api";
import type { ModelOption } from "../types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
```

Add query + state:
```typescript
const models = useQuery({
  queryKey: modelKeys.list(),
  queryFn: fetchModels,
});

const [selectedModelId, setSelectedModelId] = useState<string>("");

useEffect(() => {
  if (models.data && !selectedModelId) {
    const active = models.data.find((m) => m.is_active);
    if (active) setSelectedModelId(String(active.id));
  }
}, [models.data, selectedModelId]);
```

Update mutation to pass selected model:
```typescript
const mutation = useMutation({
  mutationFn: () => runAnalysis(id, studyId, selectedModelId ? [Number(selectedModelId)] : undefined),
  onSuccess: () => {
    qc.invalidateQueries({ queryKey: analysisKeys.list(id, studyId) });
    qc.invalidateQueries({ queryKey: hirescamKeys.study(id, studyId) });
  },
});
```

Add dropdown before buttons:
```tsx
{models.data && models.data.length > 0 && (
  <div className="no-print rounded-lg border bg-card p-3">
    <Label className="mb-1.5 text-xs font-medium text-muted-foreground">
      {t("Pilih model:", "Select model:")}
    </Label>
    <Select value={selectedModelId} onValueChange={setSelectedModelId}>
      <SelectTrigger className="w-full">
        <SelectValue placeholder={t("Pilih model...", "Select model...")} />
      </SelectTrigger>
      <SelectContent>
        {models.data.map((m) => (
          <SelectItem key={m.id} value={String(m.id)}>
            {m.model_name} v{m.model_version} ({m.architecture})
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
)}
```

Disable button: `disabled={mutation.isPending || !selectedModelId}`

- [ ] **Step 4: Typecheck** `cd frontend && npx tsc --noEmit`

- [ ] **Step 5: Commit**

---

### Task 4: Frontend — Left-right visual explanation layout

**Files:**
- Modify: `frontend/src/features/ai_analysis/pages/AnalysisDetailPage.tsx`
- Delete: `frontend/src/features/ai_analysis/components/HeatmapViewer.tsx`
- Delete: `frontend/src/features/ai_analysis/components/StudyHeaderCard.tsx`
- Delete: `frontend/src/features/ai_analysis/components/ExplanationStatusBadge.tsx`

- [ ] **Step 1: Replace StudyHeaderCard + HiResCAM section in AnalysisDetailPage**

Remove imports: `StudyHeaderCard`, `HeatmapViewer`, `ExplanationStatusBadge`.
Add import: `AuthedImage` from `@/components/ui/authed-image`, `Zoom` from `react-medium-image-zoom`.

**Remove** the old grid section (lines ~106-150):
```tsx
// DELETE this entire block:
<div className="grid grid-cols-1 gap-4 lg:grid-cols-[3fr_1fr]">
  {study.isLoading ? <Skeleton /> : <StudyHeaderCard study={study.data} />}
  <ConsensusCard rows={rows} id={CONSENSUS_ID} />
</div>

// DELETE this entire block:
{hirescam.data && hirescam.data.length > 0 ? ( ... ) : ( ... )}
```

**Replace** with inline left-right layout:
```tsx
{/* Original ECG + HiResCAM side by side */}
{study.data && (
  <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
    {/* Left: Original ECG */}
    <Card className="overflow-hidden">
      <div className="relative bg-charcoal-50">
        <Zoom>
          <AuthedImage
            path={study.data.image_original_path}
            alt={t("Studi EKG", "ECG study")}
            className="max-h-[600px] w-full object-contain"
          />
        </Zoom>
      </div>
      <div className="px-4 py-2 text-xs text-muted-foreground">
        {t("Gambar asli", "Original image")}
      </div>
    </Card>

    {/* Right: HiResCAM overlay */}
    {hirescam.data && hirescam.data.length > 0 ? (
      <Card className="overflow-hidden">
        <div className="relative bg-charcoal-50">
          <Zoom>
            <AuthedImage
              path={`api/encounters/heatmaps/${hirescam.data[0].overlay_path}`}
              alt={t("Overlay HiResCAM", "HiResCAM overlay")}
              className="max-h-[600px] w-full object-contain"
            />
          </Zoom>
        </div>
        <div className="flex items-center justify-between px-4 py-2 text-xs text-muted-foreground">
          <span>{t("HiResCAM overlay", "HiResCAM overlay")}</span>
          <span className="tabular font-medium text-foreground">
            {t("Fokus", "Focus")}: {Math.round(hirescam.data[0].focus_metric * 100)}%
          </span>
        </div>
      </Card>
    ) : (
      <Card className="flex items-center justify-center">
        <CardContent className="py-6">
          <EmptyState
            title={t("HiResCAM belum tersedia", "HiResCAM not yet available")}
            description={t(
              "Jalankan analisis untuk generate penjelasan visual.",
              "Run analysis to generate visual explanation.",
            )}
            hideMotif
          />
        </CardContent>
      </Card>
    )}
  </div>
)}
```

- [ ] **Step 2: Delete unused component files**

- Delete `frontend/src/features/ai_analysis/components/HeatmapViewer.tsx`
- Delete `frontend/src/features/ai_analysis/components/StudyHeaderCard.tsx`
- Delete `frontend/src/features/ai_analysis/components/ExplanationStatusBadge.tsx`

- [ ] **Step 3: Remove unused imports from AnalysisDetailPage**

Remove: `StudyHeaderCard`, `HeatmapViewer`, `ExplanationStatusBadge`, `HiResCAMRow` type import (if only used by deleted components).

- [ ] **Step 4: Typecheck** `cd frontend && npx tsc --noEmit`

- [ ] **Step 5: Commit**

---

### Task 5: Run all tests

- [ ] **Step 1: Backend** `cd backend && python -m pytest --tb=short -q`
- [ ] **Step 2: Frontend** `cd frontend && npx vitest run`
- [ ] **Step 3: Lint** `cd frontend && npx eslint src/`
