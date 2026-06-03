# Align HiResCAM Parameters with Kaggle Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align default parameters in CDSS HiResCAMConfig with Kaggle training configuration (use input size 640, jet colormap, tighter ROI coordinates, and updated percentile clipping) to achieve focused heatmaps matching the Kaggle model output.

**Architecture:** Update `HiResCAMConfig` class defaults in `config.py`, update unit tests in `test_config.py`, and reset the database configuration cache in the `system_config` table so changes take effect immediately.

**Tech Stack:** Python, SQLAlchemy, Flask, pytest.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `backend/app/services/hirescam/config.py` | **Modify** | Update default field values in `HiResCAMConfig` |
| `backend/tests/unit/services/hirescam/test_config.py` | **Modify** | Align assertions with new configuration defaults |
| `backend/scripts/reset_hirescam_config.py` | **Create** | DB script to delete or update `hirescam_config` row |

---

## Task 1: Update Default Parameters in `HiResCAMConfig`

**Files:**
- Modify: `backend/app/services/hirescam/config.py`

- [ ] **Step 1: Align configuration defaults in `config.py`**

Replace default parameters in `backend/app/services/hirescam/config.py` lines 14-30:

```python
    target_layer_name: str = "last_conv"
    input_size: int = 640
    device: str = "cpu"
    clip_percentile: float = 98.0
    smooth_sigma: float = 1.0
    top_percent: float = 20.0
    colormap: str = "jet"
    overlay_alpha: float = 0.45
    clip_percentile_low: float = 2.0
    use_signal_mask: bool = True
    signal_mask_strength: float = 0.65
    signal_mask_blur_radius: int = 5
    roi_x1: float = 0.03
    roi_y1: float = 0.18
    roi_x2: float = 0.98
    roi_y2: float = 0.96
    use_roi_crop: bool = True
```

- [ ] **Step 2: Verify Python syntax is valid**

Run: `backend\.venv\Scripts\python.exe -c "from app.services.hirescam.config import HiResCAMConfig; c = HiResCAMConfig(); assert c.input_size == 640 and c.colormap == 'jet'; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/config.py
git commit -m "feat(hirescam): align HiResCAMConfig defaults with Kaggle training parameters"
```

---

## Task 2: Align assertions in Config unit tests

**Files:**
- Modify: `backend/tests/unit/services/hirescam/test_config.py`

- [ ] **Step 1: Update assertions to match new defaults**

Modify `test_defaults` in `backend/tests/unit/services/hirescam/test_config.py`:

```python
    def test_defaults(self):
        cfg = HiResCAMConfig()
        assert cfg.target_layer_name == "last_conv"
        assert cfg.input_size == 640
        assert cfg.device == "cpu"
        assert cfg.clip_percentile == 98.0
        assert cfg.smooth_sigma == 1.0
        assert cfg.top_percent == 20.0
        assert cfg.colormap == "jet"
        assert cfg.overlay_alpha == 0.45
        assert cfg.roi_x1 == 0.03
        assert cfg.roi_y1 == 0.18
        assert cfg.roi_x2 == 0.98
        assert cfg.roi_y2 == 0.96
        assert cfg.use_roi_crop is True
```

- [ ] **Step 2: Run pytest to verify tests pass**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/services/hirescam/test_config.py -v`
Expected: `5 passed`

- [ ] **Step 3: Commit**

```bash
git add backend/tests/unit/services/hirescam/test_config.py
git commit -m "test(hirescam): update Config unit tests for new defaults"
```

---

## Task 3: Create Database Config Reset Script

**Files:**
- Create: `backend/scripts/reset_hirescam_config.py`

- [ ] **Step 1: Write database config reset script**

Write the python script `backend/scripts/reset_hirescam_config.py`:

```python
"""Script to reset active HiResCAM configuration in database to match defaults."""
import os
import sys
from pathlib import Path

# Add backend directory to python path
sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db
from app.db.models.system_config import SystemConfig
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import CONFIG_KEY, save_config

def main():
    app = create_app()
    with app.app_context():
        # Retrieve active config row
        row = db.session.query(SystemConfig).filter(SystemConfig.key == CONFIG_KEY).first()
        if row is not None:
            print("Found active hirescam_config in DB. Deleting to reset to defaults...")
            db.session.delete(row)
        
        # Save default configuration explicitly
        default_config = HiResCAMConfig()
        save_config(db.session, default_config, user_id=None)
        db.session.commit()
        print("Successfully reset DB hirescam_config to Kaggle-aligned defaults!")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run script to reset DB config**

Run: `backend\.venv\Scripts\python.exe backend/scripts/reset_hirescam_config.py`
Expected: `Successfully reset DB hirescam_config to Kaggle-aligned defaults!`

- [ ] **Step 3: Run integration test suite to verify everything passes**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/integration/test_tuning_api.py -v`
Expected: `16 passed`

- [ ] **Step 4: Commit**

```bash
git add backend/scripts/reset_hirescam_config.py
git commit -m "feat(db): add script to reset DB configuration to defaults"
```

---

## Self-Review Checklist

- [ ] **Spec coverage:** All parameters aligned with Kaggle notebook defaults.
- [ ] **Placeholder scan:** No TBD/TODO/placeholder steps.
- [ ] **Type consistency:** All assertions aligned with config default parameters.
