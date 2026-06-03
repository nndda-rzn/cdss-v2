# HiResCAM Signal Masking & Postprocess Improvements

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve HiResCAM heatmap accuracy by adding signal masking (from Kaggle reference code), low-percentile clipping, and evaluator improvement.

**Architecture:** New `signal_mask.py` module + config updates + orchestrator integration. Signal mask computed from original RGB image, applied after reverse-letterbox in orchestrate.py.

**Tech Stack:** Python, NumPy, Pillow, SciPy, Flask, SQLAlchemy, pytest.

---

## File Structure

**Create:**
- `backend/app/services/hirescam/signal_mask.py` — signal mask computation
- `backend/tests/unit/services/hirescam/test_signal_mask.py` — tests

**Modify:**
- `backend/app/services/hirescam/config.py` — add 4 new fields
- `backend/app/services/hirescam/postprocess.py` — add low percentile clipping
- `backend/app/services/hirescam/orchestrate.py` — integrate signal mask
- `backend/app/services/hirescam/evaluator.py` — use signal mask for focus metric
- `backend/app/services/hirescam/__init__.py` — export new module

---

### Task 1: Create signal_mask module

**Files:**
- Create: `backend/app/services/hirescam/signal_mask.py`
- Create: `backend/tests/unit/services/hirescam/test_signal_mask.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/unit/services/hirescam/test_signal_mask.py
"""Tests for signal mask computation."""
import numpy as np

from app.services.hirescam.signal_mask import create_signal_mask


def test_returns_2d_float_array():
    rgb = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
    mask = create_signal_mask(rgb)
    assert mask.ndim == 2
    assert mask.shape == (100, 200)
    assert mask.dtype == np.float32


def test_mask_values_between_0_and_1():
    rgb = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
    mask = create_signal_mask(rgb)
    assert mask.min() >= 0.0
    assert mask.max() <= 1.0


def test_dark_pixels_have_high_mask_value():
    # Create image with known dark region (ECG signal)
    rgb = np.full((100, 200, 3), 255, dtype=np.uint8)  # all white
    rgb[40:60, 80:120] = 0  # dark square in center
    mask = create_signal_mask(rgb)
    # Center dark region should have higher mask than white background
    assert mask[50, 100] > mask[10, 10]


def test_custom_threshold():
    rgb = np.full((100, 200, 3), 100, dtype=np.uint8)  # gray
    mask_strict = create_signal_mask(rgb, signal_threshold=80)
    mask_loose = create_signal_mask(rgb, signal_threshold=120)
    # Stricter threshold (lower value) → fewer dark pixels detected
    assert mask_strict.sum() <= mask_loose.sum()


def test_blur_radius_effect():
    rgb = np.zeros((100, 200, 3), dtype=np.uint8)
    rgb[50, 100] = 255  # single bright pixel
    mask_sharp = create_signal_mask(rgb, blur_radius=0)
    mask_blur = create_signal_mask(rgb, blur_radius=10)
    # Blurred mask should be more spread out (higher total)
    assert mask_blur.sum() >= mask_sharp.sum()
```

- [ ] **Step 2: Run test → FAIL**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_signal_mask.py -v`

- [ ] **Step 3: Implement**

```python
# backend/app/services/hirescam/signal_mask.py
"""Signal mask computation for HiResCAM heatmap focusing."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter


def create_signal_mask(
    rgb_image: np.ndarray,
    *,
    signal_threshold: int = 120,
    blur_radius: int = 5,
) -> np.ndarray:
    """Create a mask highlighting ECG signal regions (dark pixels).

    ECG signals are dark lines on light background. This mask detects
    dark pixels and applies Gaussian blur to create a soft mask that
    prevents heatmap from spreading to empty/grid areas.

    Args:
        rgb_image: Input image as (H, W, 3) uint8 RGB array.
        signal_threshold: Gray value below which pixels are considered
            signal (default 120). Lower = stricter.
        blur_radius: Gaussian blur radius for smooth mask (default 5).

    Returns:
        2D float32 array [0..1] of shape (H, W).
    """
    if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
        raise ValueError(f"Expected (H, W, 3) RGB image, got shape {rgb_image.shape}")

    # Convert to grayscale
    gray = (rgb_image.astype(np.float32).mean(axis=2)).astype(np.uint8)

    # Detect dark pixels (ECG signals, lead labels, grid lines)
    mask = (gray < signal_threshold).astype(np.uint8) * 255

    # Apply Gaussian blur for smooth transitions
    if blur_radius > 0:
        mask_img = Image.fromarray(mask)
        mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        mask = np.asarray(mask_img)

    # Normalize to [0, 1]
    mask = mask.astype(np.float32) / 255.0
    max_val = mask.max()
    if max_val > 0:
        mask = mask / max_val

    return mask
```

- [ ] **Step 4: Run test → PASS**

- [ ] **Step 5: Commit**

---

### Task 2: Update HiResCAMConfig

**File:** `backend/app/services/hirescam/config.py`

- [ ] **Step 1: Add 4 new fields**

Add after `overlay_alpha` field:

```python
# Signal masking
clip_percentile_low: float = 5.0
use_signal_mask: bool = True
signal_mask_strength: float = 0.65
signal_mask_blur_radius: int = 5
```

- [ ] **Step 2: Run existing config tests**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_config.py -v`
Expected: All pass (new fields have defaults, from_dict ignores unknown keys)

- [ ] **Step 3: Commit**

---

### Task 3: Update postprocess with low percentile clipping

**File:** `backend/app/services/hirescam/postprocess.py`

- [ ] **Step 1: Add `clip_percentile_low` parameter**

Update function signature:
```python
def postprocess_heatmap(
    heatmap: np.ndarray,
    letterbox_params: LetterboxParams,
    clip_percentile: float = 99.0,
    clip_percentile_low: float = 5.0,  # NEW
    smooth_sigma: float = 1.0,
    top_percent: float = 20.0,
    colormap: str = "inferno",
) -> dict[str, np.ndarray]:
```

Update clipping step (replace lines 45-47):
```python
# 1. Percentile clipping (low + high)
cap_high = np.percentile(heatmap, clip_percentile)
cap_low = np.percentile(heatmap, clip_percentile_low)
clipped = np.clip(heatmap, cap_low, cap_high)
```

- [ ] **Step 2: Update docstring**

Add `clip_percentile_low` to docstring Args section.

- [ ] **Step 3: Run postprocess tests**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_postprocess.py -v`
Expected: All pass (new param has default, existing behavior unchanged)

- [ ] **Step 4: Commit**

---

### Task 4: Integrate signal mask in orchestrate.py

**File:** `backend/app/services/hirescam/orchestrate.py`

- [ ] **Step 1: Import signal mask**

Add at top:
```python
from app.services.hirescam.signal_mask import create_signal_mask
```

- [ ] **Step 2: Apply signal mask after postprocess**

After `postprocess_heatmap()` call and before `array_to_png()`, add:

```python
# Apply signal mask to focus heatmap on ECG signals
if config.use_signal_mask:
    rgb_img = np.array(Image.open(str(image_path)).convert("RGB"))
    sig_mask = create_signal_mask(
        rgb_img,
        blur_radius=config.signal_mask_blur_radius,
    )
    norm_heatmap = processed["heatmap_norm"]
    masked = (1.0 - config.signal_mask_strength) * norm_heatmap + \
             config.signal_mask_strength * (norm_heatmap * sig_mask)
    # Re-normalize
    m_min, m_max = masked.min(), masked.max()
    if m_max - m_min > 1e-8:
        masked = (masked - m_min) / (m_max - m_min)
    else:
        masked = np.zeros_like(masked)
    processed["heatmap_norm"] = masked

heatmap_png = array_to_png(processed["heatmap_norm"], colormap=config.colormap)
```

Add import at top: `from PIL import Image` and `import numpy as np`.

- [ ] **Step 3: Run orchestrate tests (if any)**

Run: `cd backend && python -m pytest tests/ -k "hirescam" -v --tb=short`

- [ ] **Step 4: Commit**

---

### Task 5: Update evaluator to use signal mask

**File:** `backend/app/services/hirescam/evaluator.py`

- [ ] **Step 1: Add signal mask-based evaluation**

Add new function:
```python
def compute_signal_mask_iou(
    heatmap: np.ndarray,
    rgb_image: np.ndarray,
    *,
    signal_threshold: int = 120,
    blur_radius: int = 5,
) -> float:
    """Compute fraction of heatmap activation overlapping with ECG signal regions.

    More accurate than center-crop for ECG images where signals may not
    be centered.
    """
    from app.services.hirescam.signal_mask import create_signal_mask

    mask = create_signal_mask(rgb_image, signal_threshold=signal_threshold, blur_radius=blur_radius)

    # Ensure same size
    if mask.shape != heatmap.shape:
        import cv2
        mask = cv2.resize(mask, (heatmap.shape[1], heatmap.shape[0]), interpolation=cv2.INTER_LINEAR)

    total = float(heatmap.sum())
    if total == 0:
        return 0.0

    masked_activation = float((heatmap * mask).sum())
    return masked_activation / total
```

- [ ] **Step 2: Update `evaluate_explanation` to accept optional rgb_image**

```python
def evaluate_explanation(
    heatmap: np.ndarray,
    *,
    confidence: float | None = None,
    rgb_image: np.ndarray | None = None,
) -> tuple[str, float]:
    if heatmap.ndim != 2:
        raise ValueError(f"Expected 2D heatmap, got {heatmap.ndim}D")

    if rgb_image is not None:
        focus_metric = compute_signal_mask_iou(heatmap, rgb_image)
    else:
        focus_metric = _compute_signal_region_iou(heatmap)

    status = _classify_status(focus_metric, confidence)
    return status, float(focus_metric)
```

- [ ] **Step 3: Update orchestrate.py to pass rgb_image to evaluator**

In `orchestrate.py`, update `evaluate_explanation()` call:
```python
# Before:
status, focus_metric = evaluate_explanation(
    heatmap_arr, confidence=analysis.confidence_score
)

# After:
status, focus_metric = evaluate_explanation(
    heatmap_arr, confidence=analysis.confidence_score, rgb_image=rgb_img,
)
```

(Move `rgb_img` loading before the evaluate call — it's already loaded in Task 4.)

- [ ] **Step 4: Run evaluator tests**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_evaluator.py -v`

- [ ] **Step 5: Commit**

---

### Task 6: Export new module + update __init__

**File:** `backend/app/services/hirescam/__init__.py`

- [ ] **Step 1: Add import and export**

```python
from app.services.hirescam.signal_mask import create_signal_mask
```

Add to `__all__`:
```python
"create_signal_mask",
```

- [ ] **Step 2: Commit**

---

### Task 7: Run all tests

- [ ] **Step 1: Backend** `cd backend && python -m pytest --tb=short -q`
- [ ] **Step 2: Frontend** `cd frontend && npx vitest run`
- [ ] **Step 3: Fix any issues**
