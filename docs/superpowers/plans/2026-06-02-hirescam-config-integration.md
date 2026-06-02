# Plan: Integrate HiResCAM Tuning Config into Production Pipeline

**Date:** 2026-06-02
**Branch:** `feat/sprint-4/hirescam-tuning-viewer` (existing) → new branch `feat/sprint-4/hirescam-config-integration`
**Status:** Draft

---

## Problem

HiResCAM production pipeline (`orchestrate.py`) has 6 hardcoded params:
- `target_layer_name="last_conv"`, `input_size=1600`, `device="cpu"`
- `colormap="inferno"` (in artifact persistence)
- **`postprocess_heatmap()` is dead code** — never called in production flow

Tuning pipeline generated 48 configs ranked by `focus_metric`, but results cannot feed back into production.

## Goal

1. Store best HiResCAM config in DB (`system_config` table)
2. Wire config through `orchestrate.py` → `generate_hirescam_v2()` + `postprocess_heatmap()`
3. Add API endpoint to apply/select a tuning config
4. Seed default config from tuning results

---

## Architecture

### Current flow (broken)
```
API → generate_artifacts()
  → generate_hirescam_v2(last_conv, 1600)  # hardcoded
  → array_to_png(heatmap)                    # raw, no postprocess!
  → compose_overlay / compose_side_by_side
  → evaluate_explanation()
  → HiResCAMArtifact(colormap_used="inferno") # hardcoded
```

### Target flow
```
API → generate_artifacts(config=read_config())
  → generate_hirescam_v2(config.target_layer, config.input_size)
  → postprocess_heatmap(config.clip, config.smooth, config.top%, config.colormap)
  → compose_overlay / compose_side_by_side
  → evaluate_explanation()
  → HiResCAMArtifact(colormap_used=config.colormap)
```

---

## Tasks

### Task 1: Create HiResCAMConfig dataclass
**File:** `backend/app/services/hirescam/config.py` (NEW, ~50 lines)

```python
@dataclass
class HiResCAMConfig:
    target_layer_name: str = "last_conv"
    input_size: int = 1600
    device: str = "cpu"
    clip_percentile: float = 99.0
    smooth_sigma: float = 1.0
    top_percent: float = 20.0
    colormap: str = "inferno"
    overlay_alpha: float = 0.45

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, d: dict) -> "HiResCAMConfig": ...
```

- Register exports in `__init__.py`

### Task 2: Add DB config CRUD
**File:** `backend/app/services/hirescam/config_store.py` (NEW, ~40 lines)

```python
CONFIG_KEY = "hirescam_config"

def get_config(session) -> HiResCAMConfig:
    """Read from system_config table, return default if missing."""
    row = session.get(SystemConfig, CONFIG_KEY)
    if row is None:
        return HiResCAMConfig()
    return HiResCAMConfig.from_dict(row.value_json)

def save_config(session, config: HiResCAMConfig, user_id: int | None = None) -> None:
    """Upsert config into system_config table."""
    row = session.get(SystemConfig, CONFIG_KEY)
    if row is None:
        row = SystemConfig(key=CONFIG_KEY, value_json=config.to_dict())
        session.add(row)
    else:
        row.value_json = config.to_dict()
        row.updated_by = user_id
```

Uses existing `system_config` table — **no migration needed**.

### Task 3: Add POST /api/tuning/apply endpoint
**File:** `backend/app/api/tuning.py` (extend, ~85→130 lines)

```python
@bp.post("/apply/<int:config_index>")
@require_role(Role.ADMIN)
def apply_config(config_index: int):
    """Read config_index from summary.csv, save to DB as active config."""
    # 1. Read summary.csv, find row with config_index
    # 2. Extract: input_size, target_layer, smooth_sigma, top_percent, clip_percentile, colormap
    # 3. Build HiResCAMConfig, save_config(session)
    # 4. Return { status: "applied", config: {...} }
```

Also add GET endpoint:
```python
@bp.get("/active")
def get_active_config():
    """Return current active HiResCAM config from DB."""
```

### Task 4: Wire config into orchestrate.py
**File:** `backend/app/services/hirescam/orchestrate.py` (modify, 151→~180 lines)

Changes:
1. `generate_artifacts()` add optional `config: HiResCAMConfig | None = None`
2. If `config is None`, call `get_config(session)` from DB
3. Pass `config.target_layer_name`, `config.input_size` to `generate_hirescam_v2()`
4. **Add `postprocess_heatmap()` call** after generator, before `array_to_png()`
5. Pass `config.clip_percentile`, `config.smooth_sigma`, `config.top_percent`, `config.colormap` to postprocess
6. Use `config.colormap` in artifact persistence (not hardcoded `"inferno"`)
7. Use `config.overlay_alpha` in `compose_overlay()`

### Task 5: Thread config through API callers
**Files:**
- `backend/app/api/hirescam.py` — read config from DB, pass to `generate_artifacts()`
- `backend/app/services/inference/orchestrate.py` — same

### Task 6: Update overlay.py to accept alpha param
**File:** `backend/app/services/hirescam/overlay.py` (modify)

```python
def compose_overlay(image_path, heatmap_png, *, alpha: float = 0.4): ...
```

### Task 7: Seed default config from best tuning result
**File:** `backend/scripts/seed_hirescam_config.py` (NEW, ~30 lines)

```python
# 1. Read summary.csv, find row with highest focus_metric
# 2. Build HiResCAMConfig from that row
# 3. Save to system_config via save_config()
# 4. Print applied config
```

### Task 8: Tests
- `backend/tests/unit/services/hirescam/test_config.py` — dataclass round-trip
- `backend/tests/unit/services/hirescam/test_config_store.py` — DB read/write
- Extend `backend/tests/integration/test_tuning_api.py` — POST /apply + GET /active
- Verify orchestrate uses config (mock test)

### Task 9: File-size check
- `orchestrate.py` currently 151 lines, target ~180 — under 200 budget
- If over: extract `_generate_heatmap_artifacts()` helper

---

## Dependency Order

```
Task 1 (config dataclass)
  → Task 2 (config_store)
    → Task 3 (apply endpoint)
    → Task 4 (wire orchestrate)
      → Task 5 (thread through callers)
        → Task 6 (overlay alpha)
  → Task 7 (seed script)
  → Task 8 (tests)
  → Task 9 (file-size check)
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `app/services/hirescam/orchestrate.py` | Production HiResCAM generation — main target |
| `app/services/hirescam/postprocess.py` | Post-processing pipeline (currently dead code) |
| `app/services/hirescam/generator_v2.py` | Core HiResCAM generator |
| `app/services/hirescam/overlay.py` | Overlay composition |
| `app/db/models/system_config.py` | Key-value config table (reuse) |
| `app/api/tuning.py` | Tuning API (extend with apply) |
| `app/api/hirescam.py` | HiResCAM API endpoint |
| `app/services/inference/orchestrate.py` | Auto-generate on inference |
| `outputs/hirescam_tuning_grid/summary.csv` | Tuning results |

---

## Risk

- **postprocess_heatmap() adds ~15ms per image** — acceptable for CDSS
- **Existing artifacts** not re-generated — only new analyses use config (by design)
- **No DB migration** needed — uses existing `system_config` table
