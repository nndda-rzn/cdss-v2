# HiResCAM Tuning Viewer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a browser-based tuning results viewer with grid gallery, per-config detail modal, and summary table for comparing 48+ HiResCAM experiments.

**Architecture:** New backend API (`/api/tuning/`) serves tuning outputs from `outputs/hirescam_tuning_grid/`. New frontend feature module `features/tuning/` with grid gallery page, detail modal, and summary table. Route at `/tuning` under AppShell.

**Tech Stack:** Python Flask, React, TanStack Query, Tailwind CSS, lucide-react icons

---

## File Structure

```
backend/app/api/
├── tuning.py                    (CREATE — new blueprint)
├── __init__.py                  (MODIFY — register tuning blueprint)

backend/tests/integration/
├── test_tuning_api.py           (CREATE — integration tests)

frontend/src/features/tuning/
├── api.ts                       (CREATE — API calls + query keys)
├── types.ts                     (CREATE — TypeScript types)
├── pages/
│   └── TuningGridPage.tsx       (CREATE — main grid gallery page)
├── components/
│   ├── ConfigCard.tsx           (CREATE — single config card)
│   ├── ConfigDetailModal.tsx    (CREATE — detail view modal)
│   └── SummaryTable.tsx         (CREATE — summary.csv table)

frontend/src/routes/
└── tuning.tsx                   (CREATE — thin route wrapper)

frontend/src/App.tsx             (MODIFY — add /tuning route)
```

---

## Task 1: Backend API — List Configs

**Files:**
- Create: `backend/app/api/tuning.py`
- Modify: `backend/app/api/__init__.py`
- Create: `backend/tests/integration/test_tuning_api.py`

**Endpoint:** `GET /api/tuning/grid`

Returns summary.csv as JSON array. Response:
```json
{
  "items": [
    {
      "config_index": 1,
      "input_size": 1600,
      "target_layer": "last_conv",
      "smooth_sigma": 0.0,
      "top_percent": 15.0,
      "clip_percentile": 99.0,
      "colormap": "turbo",
      "explanation_status": "good",
      "focus_metric": 0.629,
      "confidence": -1.565
    }
  ]
}
```

- [ ] **Step 1: Write failing test**

```python
# backend/tests/integration/test_tuning_api.py
"""Integration tests for tuning API endpoints."""
from app import create_app


def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def client(app):
    return app.test_client()


class TestTuningGrid:
    def test_get_grid_returns_items(self, client):
        resp = client.get("/api/tuning/grid")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_grid_has_required_fields(self, client):
        resp = client.get("/api/tuning/grid")
        data = resp.get_json()
        if data["items"]:
            item = data["items"][0]
            assert "config_index" in item
            assert "input_size" in item
            assert "target_layer" in item
            assert "focus_metric" in item
            assert "explanation_status" in item

    def test_get_grid_empty_when_no_outputs(self, client):
        resp = client.get("/api/tuning/grid")
        assert resp.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/integration/test_tuning_api.py -v`
Expected: FAIL — 404 or import error

- [ ] **Step 3: Implement tuning.py**

```python
# backend/app/api/tuning.py
"""Tuning pipeline results API."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from flask import Blueprint, current_app, jsonify, abort, send_file

from app.api._shared import session
from app.core.security.decorators import require_role
from app.db.models.user import Role

bp = Blueprint("tuning", __name__, url_prefix="/api/tuning")

ALLOWED_IMAGES = {
    "original.png", "heatmap_colored.png", "heatmap_norm.png",
    "overlay.png", "mask_top_area.png",
}


def _repo_root() -> Path:
    """Get project root from STORAGE_DIR config."""
    return Path(current_app.config.get("STORAGE_DIR", "")).parent.parent


def _grid_dir() -> Path:
    return _repo_root() / "outputs" / "hirescam_tuning_grid"


@bp.get("/grid")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_grid():
    """Return summary.csv as JSON array."""
    summary_path = _grid_dir() / "summary.csv"

    if not summary_path.exists():
        return jsonify({"items": []})

    with open(summary_path, newline="") as f:
        reader = csv.DictReader(f)
        items = []
        for row in reader:
            items.append({
                "config_index": int(row["config_index"]),
                "input_size": int(row["input_size"]),
                "target_layer": row["target_layer"],
                "smooth_sigma": float(row["smooth_sigma"]),
                "top_percent": float(row["top_percent"]),
                "clip_percentile": float(row["clip_percentile"]),
                "colormap": row["colormap"],
                "explanation_status": row["explanation_status"],
                "focus_metric": float(row["focus_metric"]),
                "confidence": float(row["confidence"]),
            })

    return jsonify({"items": items})


@bp.get("/grid/<int:config_index>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_config(config_index: int):
    """Return metadata.json for a specific config."""
    config_dir = _grid_dir() / f"config_{config_index:03d}"
    metadata_path = config_dir / "metadata.json"

    if not metadata_path.exists():
        abort(404, description=f"Config {config_index} not found")

    with open(metadata_path) as f:
        metadata = json.load(f)

    return jsonify(metadata)


@bp.get("/grid/<int:config_index>/images/<filename>")
@require_role(Role.ADMIN, Role.CLINICIAN, Role.NURSE, Role.RESEARCHER)
def get_config_image(config_index: int, filename: str):
    """Serve a PNG image from a config directory."""
    if filename not in ALLOWED_IMAGES:
        abort(404, description=f"Unknown image: {filename}")

    image_path = _grid_dir() / f"config_{config_index:03d}" / filename

    if not image_path.exists() or not image_path.is_file():
        abort(404, description=f"Image not found: {filename}")

    # Path traversal guard
    if not image_path.resolve().is_relative_to(_grid_dir().resolve()):
        abort(400, description="Invalid path")

    return send_file(str(image_path), mimetype="image/png")
```

- [ ] **Step 4: Register blueprint**

In `backend/app/api/__init__.py`, add inside `register_blueprints()`:

```python
from app.api.tuning import bp as tuning_bp
app.register_blueprint(tuning_bp)
```

- [ ] **Step 5: Add remaining tests**

Append to `backend/tests/integration/test_tuning_api.py`:

```python
class TestTuningConfig:
    def test_get_config_returns_metadata(self, client):
        resp = client.get("/api/tuning/grid/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "config_index" in data
        assert data["config_index"] == 1

    def test_get_config_not_found(self, client):
        resp = client.get("/api/tuning/grid/99999")
        assert resp.status_code == 404


class TestTuningImage:
    def test_serves_image(self, client):
        resp = client.get("/api/tuning/grid/1/images/overlay.png")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"

    def test_image_not_found(self, client):
        resp = client.get("/api/tuning/grid/1/images/nonexistent.png")
        assert resp.status_code == 404

    def test_config_not_found(self, client):
        resp = client.get("/api/tuning/grid/99999/images/overlay.png")
        assert resp.status_code == 404

    def test_path_traversal_blocked(self, client):
        resp = client.get("/api/tuning/grid/1/images/../../etc/passwd")
        assert resp.status_code in (400, 404)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/integration/test_tuning_api.py -v`
Expected: 9 tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/tuning.py backend/app/api/__init__.py backend/tests/integration/test_tuning_api.py
git commit -m "feat(tuning): add backend API — grid, config metadata, image serving"
```

---

## Task 2: Frontend — Types + API Layer

**Files:**
- Create: `frontend/src/features/tuning/types.ts`
- Create: `frontend/src/features/tuning/api.ts`

- [ ] **Step 1: Create types.ts**

```typescript
// frontend/src/features/tuning/types.ts
export interface TuningConfig {
  config_index: number;
  input_size: number;
  target_layer: string;
  smooth_sigma: number;
  top_percent: number;
  clip_percentile: number;
  colormap: string;
  explanation_status: string;
  focus_metric: number;
  confidence: number;
}

export interface TuningMetadata extends TuningConfig {
  image_path: string;
  original_size: [number, number];
  target_layer_info: string;
  target_class_id: number;
  letterbox_ratio: number;
  letterbox_padding: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  overlay_alpha: number;
}
```

- [ ] **Step 2: Create api.ts**

```typescript
// frontend/src/features/tuning/api.ts
import { apiFetch } from "@/lib/api/client";
import type { TuningConfig, TuningMetadata } from "./types";

export const tuningKeys = {
  all: ["tuning"] as const,
  grid: () => [...tuningKeys.all, "grid"] as const,
  config: (index: number) => [...tuningKeys.all, "config", index] as const,
};

export async function fetchTuningGrid(): Promise<TuningConfig[]> {
  const resp = await apiFetch("/api/tuning/grid");
  if (!resp.ok) throw new Error("Failed to fetch tuning grid");
  const data = await resp.json();
  return data.items;
}

export async function fetchTuningConfig(index: number): Promise<TuningMetadata> {
  const resp = await apiFetch(`/api/tuning/grid/${index}`);
  if (!resp.ok) throw new Error("Failed to fetch config");
  return resp.json();
}

export function tuningImageUrl(configIndex: number, filename: string): string {
  return `/api/tuning/grid/${configIndex}/images/${filename}`;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/tuning/types.ts frontend/src/features/tuning/api.ts
git commit -m "feat(tuning): add frontend types and API layer"
```

---

## Task 3: Frontend — ConfigCard Component

**Files:**
- Create: `frontend/src/features/tuning/components/ConfigCard.tsx`

- [ ] **Step 1: Create ConfigCard.tsx**

```tsx
// frontend/src/features/tuning/components/ConfigCard.tsx
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { tuningImageUrl } from "../api";
import type { TuningConfig } from "../types";

interface ConfigCardProps {
  config: TuningConfig;
  onClick: (config: TuningConfig) => void;
}

const statusColors: Record<string, string> = {
  good: "bg-green-100 text-green-800",
  diffuse: "bg-yellow-100 text-yellow-800",
  "off-target": "bg-red-100 text-red-800",
  "low-confidence": "bg-gray-100 text-gray-800",
};

export function ConfigCard({ config, onClick }: ConfigCardProps) {
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onClick(config)}
    >
      <CardContent className="p-3">
        <div className="aspect-square overflow-hidden rounded-md mb-2 bg-muted">
          <img
            src={tuningImageUrl(config.config_index, "overlay.png")}
            alt={`Config ${config.config_index}`}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
        <div className="space-y-1 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-mono text-muted-foreground">
              #{config.config_index}
            </span>
            <Badge
              variant="secondary"
              className={statusColors[config.explanation_status] ?? ""}
            >
              {config.explanation_status}
            </Badge>
          </div>
          <div className="text-muted-foreground">
            {config.input_size} | {config.target_layer}
          </div>
          <div className="font-medium">
            focus: {config.focus_metric.toFixed(3)}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/tuning/components/ConfigCard.tsx
git commit -m "feat(tuning): add ConfigCard component"
```

---

## Task 4: Frontend — ConfigDetailModal Component

**Files:**
- Create: `frontend/src/features/tuning/components/ConfigDetailModal.tsx`

- [ ] **Step 1: Create ConfigDetailModal.tsx**

```tsx
// frontend/src/features/tuning/components/ConfigDetailModal.tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchTuningConfig, tuningImageUrl, tuningKeys } from "../api";
import type { TuningConfig } from "../types";

interface ConfigDetailModalProps {
  config: TuningConfig | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type ViewMode = "overlay" | "heatmap" | "original";

const imageFiles: Record<ViewMode, string> = {
  overlay: "overlay.png",
  heatmap: "heatmap_colored.png",
  original: "original.png",
};

export function ConfigDetailModal({ config, open, onOpenChange }: ConfigDetailModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>("overlay");

  const { data: metadata, isLoading } = useQuery({
    queryKey: tuningKeys.config(config?.config_index ?? 0),
    queryFn: () => fetchTuningConfig(config!.config_index),
    enabled: open && config !== null,
  });

  if (!config) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Config #{config.config_index}</DialogTitle>
        </DialogHeader>

        {/* View mode toggle */}
        <div className="flex gap-2">
          {(["overlay", "heatmap", "original"] as const).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === mode
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>

        {/* Image */}
        <div className="aspect-[4/3] overflow-hidden rounded-md bg-muted">
          <img
            src={tuningImageUrl(config.config_index, imageFiles[viewMode])}
            alt={`Config ${config.config_index} ${viewMode}`}
            className="w-full h-full object-contain"
          />
        </div>

        {/* Metadata */}
        {isLoading ? (
          <Skeleton className="h-20" />
        ) : metadata && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Input size: {metadata.input_size}</div>
            <div>Layer: {metadata.target_layer}</div>
            <div>Smooth: {metadata.smooth_sigma}</div>
            <div>Top%: {metadata.top_percent}</div>
            <div>Focus: {metadata.focus_metric.toFixed(3)}</div>
            <div>
              <Badge variant="secondary">{metadata.explanation_status}</Badge>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/tuning/components/ConfigDetailModal.tsx
git commit -m "feat(tuning): add ConfigDetailModal component"
```

---

## Task 5: Frontend — SummaryTable Component

**Files:**
- Create: `frontend/src/features/tuning/components/SummaryTable.tsx`

- [ ] **Step 1: Create SummaryTable.tsx**

```tsx
// frontend/src/features/tuning/components/SummaryTable.tsx
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TuningConfig } from "../types";

interface SummaryTableProps {
  configs: TuningConfig[];
  onSelect: (config: TuningConfig) => void;
}

export function SummaryTable({ configs, onSelect }: SummaryTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Summary ({configs.length} experiments)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">#</th>
                <th className="text-left p-2">Input</th>
                <th className="text-left p-2">Layer</th>
                <th className="text-left p-2">Smooth</th>
                <th className="text-left p-2">Top%</th>
                <th className="text-left p-2">Colormap</th>
                <th className="text-left p-2">Focus</th>
                <th className="text-left p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {configs.map((c) => (
                <tr
                  key={c.config_index}
                  className="border-b hover:bg-muted cursor-pointer"
                  onClick={() => onSelect(c)}
                >
                  <td className="p-2 font-mono">{c.config_index}</td>
                  <td className="p-2">{c.input_size}</td>
                  <td className="p-2">{c.target_layer}</td>
                  <td className="p-2">{c.smooth_sigma}</td>
                  <td className="p-2">{c.top_percent}</td>
                  <td className="p-2">{c.colormap}</td>
                  <td className="p-2 font-medium">{c.focus_metric.toFixed(3)}</td>
                  <td className="p-2">
                    <Badge variant="secondary">{c.explanation_status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/tuning/components/SummaryTable.tsx
git commit -m "feat(tuning): add SummaryTable component"
```

---

## Task 6: Frontend — TuningGridPage

**Files:**
- Create: `frontend/src/features/tuning/pages/TuningGridPage.tsx`

- [ ] **Step 1: Create TuningGridPage.tsx**

```tsx
// frontend/src/features/tuning/pages/TuningGridPage.tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ArrowLeft, LayoutGrid, Table } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useI18nStore } from "@/lib/i18n/store";
import { fetchTuningGrid, tuningKeys } from "../api";
import { ConfigCard } from "../components/ConfigCard";
import { ConfigDetailModal } from "../components/ConfigDetailModal";
import { SummaryTable } from "../components/SummaryTable";
import type { TuningConfig } from "../types";

type ViewMode = "grid" | "table";

export function TuningGridPage() {
  const t = useI18nStore((s) => s.t);
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [selected, setSelected] = useState<TuningConfig | null>(null);

  const { data: configs, isLoading, error } = useQuery({
    queryKey: tuningKeys.grid(),
    queryFn: fetchTuningGrid,
  });

  if (isLoading) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton key={i} className="aspect-square" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !configs) {
    return (
      <EmptyState
        title={t("Gagal memuat data", "Failed to load data")}
        description={t("Terjadi kesalahan saat memuat hasil tuning", "An error occurred while loading tuning results")}
      />
    );
  }

  if (configs.length === 0) {
    return (
      <EmptyState
        title={t("Belum ada hasil tuning", "No tuning results yet")}
        description={t("Jalankan tuning pipeline untuk menghasilkan data", "Run the tuning pipeline to generate data")}
      />
    );
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link to="/dashboard">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">
          {t("Hasil Tuning HiResCAM", "HiResCAM Tuning Results")}
        </h1>
        <div className="ml-auto flex gap-2">
          <Button
            variant={viewMode === "grid" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("grid")}
          >
            <LayoutGrid className="h-4 w-4 mr-1" />
            Grid
          </Button>
          <Button
            variant={viewMode === "table" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("table")}
          >
            <Table className="h-4 w-4 mr-1" />
            Table
          </Button>
        </div>
      </div>

      {/* Content */}
      {viewMode === "grid" ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {configs.map((config) => (
            <ConfigCard
              key={config.config_index}
              config={config}
              onClick={setSelected}
            />
          ))}
        </div>
      ) : (
        <SummaryTable configs={configs} onSelect={setSelected} />
      )}

      {/* Detail Modal */}
      <ConfigDetailModal
        config={selected}
        open={selected !== null}
        onOpenChange={(open) => { if (!open) setSelected(null); }}
      />
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/tuning/pages/TuningGridPage.tsx
git commit -m "feat(tuning): add TuningGridPage with grid/table views"
```

---

## Task 7: Frontend — Route + App Integration

**Files:**
- Create: `frontend/src/routes/tuning.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create route wrapper**

```tsx
// frontend/src/routes/tuning.tsx
import { lazy } from "react";

const TuningGridPage = lazy(
  () => import("../features/tuning/pages/TuningGridPage").then((m) => ({ default: m.TuningGridPage }))
);

export function TuningRoute() {
  return <TuningGridPage />;
}
```

- [ ] **Step 2: Add route to App.tsx**

In `frontend/src/App.tsx`, add import and route:

```tsx
import { TuningRoute } from "./routes/tuning";

// Inside <Routes>, before the * catch-all:
<Route path="/tuning" element={<AppShell><TuningRoute /></AppShell>} />
```

- [ ] **Step 3: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 4: Commit**

```bash
git add frontend/src/routes/tuning.tsx frontend/src/App.tsx
git commit -m "feat(tuning): add /tuning route to App.tsx"
```

---

## Task 8: Final Verification

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v --tb=short`
Expected: ALL tests PASS

- [ ] **Step 2: Run frontend tests**

Run: `cd frontend && npx vitest run`
Expected: ALL tests PASS

- [ ] **Step 3: Test API endpoints manually**

```bash
cd backend
# Start the server
flask run

# List grid
curl http://localhost:5000/api/tuning/grid | python -m json.tool

# Get config metadata
curl http://localhost:5000/api/tuning/grid/1 | python -m json.tool

# Get image
curl -o /tmp/test.png http://localhost:5000/api/tuning/grid/1/images/overlay.png
```

- [ ] **Step 4: Test frontend in browser**

Navigate to `http://localhost:5173/tuning` and verify:
- Grid gallery shows 48 config cards with overlay images
- Clicking a card opens detail modal with image + metadata
- Table view shows summary.csv data
- Table row click opens detail modal

---

## Summary

| Task | Files | Tests |
|------|-------|-------|
| 1. Backend API | `tuning.py`, `__init__.py`, `test_tuning_api.py` | 9 |
| 2. Frontend Types + API | `types.ts`, `api.ts` | — |
| 3. ConfigCard | `ConfigCard.tsx` | — |
| 4. ConfigDetailModal | `ConfigDetailModal.tsx` | — |
| 5. SummaryTable | `SummaryTable.tsx` | — |
| 6. TuningGridPage | `TuningGridPage.tsx` | — |
| 7. Route + App | `tuning.tsx`, `App.tsx` | — |
| 8. Final Verification | — | full suite |

**Total new backend tests: 9**
**Total new frontend components: 4**
**New route: `/tuning`**
