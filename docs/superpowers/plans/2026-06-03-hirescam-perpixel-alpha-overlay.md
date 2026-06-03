# HiResCAM Per-Pixel Alpha Overlay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement per-pixel alpha overlay blending, CAM cleaning (threshold + gamma correction), and ROI paste-back to ensure the heatmap is focused on the ECG signals and background grid lines remain clean (no solid blue/purple background).

**Architecture:** 
1. Add new config parameters (`cam_threshold`, `cam_gamma`, `max_alpha`) to `HiResCAMConfig`.
2. Add helper functions (`clean_cam`, `make_transparent_cam_overlay`, `paste_roi_overlay_to_full`) to `backend/app/services/hirescam/overlay.py`.
3. Update `generate_artifacts` in `backend/app/services/hirescam/orchestrate.py` to use the new per-pixel alpha overlay pipeline.
4. Update unit tests in `test_config.py`, `test_overlay.py`, and `test_orchestrate.py`.

**Tech Stack:** Python, Pillow, numpy, matplotlib, Pytest.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `backend/app/services/hirescam/config.py` | **Modify** | Add `cam_threshold`, `cam_gamma`, `max_alpha` properties |
| `backend/app/services/hirescam/overlay.py` | **Modify** | Add `clean_cam`, `make_transparent_cam_overlay`, `paste_roi_overlay_to_full` functions |
| `backend/app/services/hirescam/orchestrate.py` | **Modify** | Integrate new clean/overlay/paste pipeline |
| `backend/tests/unit/services/hirescam/test_config.py` | **Modify** | Update Config unit tests with new parameters |
| `backend/tests/unit/services/hirescam/test_overlay.py` | **Modify** | Write unit tests for new overlay helper functions |
| `backend/tests/unit/services/hirescam/test_orchestrate.py` | **Modify** | Verify orchestrate behaves correctly with new functions |

---

## Task 1: Update `HiResCAMConfig` with New Parameters

**Files:**
- Modify: `backend/app/services/hirescam/config.py`
- Modify: `backend/tests/unit/services/hirescam/test_config.py`

- [ ] **Step 1: Edit `config.py`**

Add the three new tuning parameters to `HiResCAMConfig` in `backend/app/services/hirescam/config.py`:

```python
    cam_threshold: float = 0.40
    cam_gamma: float = 2.0
    max_alpha: float = 0.60
```

- [ ] **Step 2: Edit unit tests in `test_config.py`**

Add assertions for the new fields in `test_defaults` and `test_custom_values` inside `backend/tests/unit/services/hirescam/test_config.py`:

```python
    def test_defaults(self):
        # ...
        assert cfg.cam_threshold == 0.40
        assert cfg.cam_gamma == 2.0
        assert cfg.max_alpha == 0.60
```

- [ ] **Step 3: Run config unit tests**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/services/hirescam/test_config.py -v`
Expected: `5 passed`

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/hirescam/config.py backend/tests/unit/services/hirescam/test_config.py
git commit -m "feat(hirescam): add cam_threshold, cam_gamma, and max_alpha to HiResCAMConfig"
```

---

## Task 2: Implement Overlay Helpers in `overlay.py`

**Files:**
- Modify: `backend/app/services/hirescam/overlay.py`
- Modify: `backend/tests/unit/services/hirescam/test_overlay.py`

- [ ] **Step 1: Edit `overlay.py`**

Add the overlay helper functions to `backend/app/services/hirescam/overlay.py`:

```python
import io
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# ... keep existing compose_overlay and compose_side_by_side ...

def clean_cam(
    cam: np.ndarray,
    crop_img: Image.Image,
    *,
    threshold: float = 0.40,
    gamma: float = 2.0,
    use_signal_mask: bool = True,
    signal_mask_blur_radius: int = 5,
) -> np.ndarray:
    """Clean CAM activation map by thresholding, gamma correction, and signal masking."""
    cam = np.nan_to_num(cam).astype(np.float32)
    cam_min, cam_max = cam.min(), cam.max()
    if cam_max - cam_min > 1e-8:
        cam = (cam - cam_min) / (cam_max - cam_min)
    else:
        cam = np.zeros_like(cam)

    # Discard low activations
    cam[cam < threshold] = 0.0

    if cam.max() > 0:
        cam = cam / (cam.max() + 1e-8)

    # Apply gamma correction to emphasize important regions
    cam = np.power(cam, gamma)

    if use_signal_mask:
        from app.services.hirescam.signal_mask import create_signal_mask
        rgb_img = np.array(crop_img.convert("RGB"))
        signal_mask = create_signal_mask(rgb_img, blur_radius=signal_mask_blur_radius)

        if signal_mask.shape != cam.shape:
            # Resize signal mask to match CAM dimensions
            mask_img = Image.fromarray((signal_mask * 255).astype(np.uint8))
            mask_img = mask_img.resize((cam.shape[1], cam.shape[0]), Image.Resampling.BILINEAR)
            signal_mask = np.array(mask_img).astype(np.float32) / 255.0

        cam = cam * signal_mask

        if cam.max() > 0:
            cam = cam / (cam.max() + 1e-8)

    return cam


def make_transparent_cam_overlay(
    crop_img: Image.Image,
    cam: np.ndarray,
    *,
    max_alpha: float = 0.60,
    colormap: str = "jet",
) -> bytes:
    """Generate overlay image with per-pixel alpha maps blending colormapped CAM."""
    crop_rgb = np.array(crop_img.convert("RGB")).astype(np.float32) / 255.0

    if cam.shape[:2] != crop_rgb.shape[:2]:
        cam_img = Image.fromarray((cam * 255).astype(np.uint8))
        cam_img = cam_img.resize((crop_rgb.shape[1], crop_rgb.shape[0]), Image.Resampling.BILINEAR)
        cam = np.array(cam_img).astype(np.float32) / 255.0

    cmap = plt.get_cmap(colormap)
    heatmap = cmap(cam)[..., :3]

    alpha_map = cam[..., None] * max_alpha
    overlay = crop_rgb * (1 - alpha_map) + heatmap * alpha_map
    overlay = np.clip(overlay * 255.0, 0, 255).astype(np.uint8)

    img_out = Image.fromarray(overlay, mode="RGB")
    buf = io.BytesIO()
    img_out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def paste_roi_overlay_to_full(
    full_image_path: str | Path,
    crop_overlay_png: bytes,
    roi_bbox: tuple[int, int, int, int],
) -> bytes:
    """Paste crop overlay PNG bytes back onto full report only within ROI boundaries."""
    full = Image.open(full_image_path).convert("RGB")
    overlay = Image.open(io.BytesIO(crop_overlay_png)).convert("RGB")

    x1, y1, x2, y2 = roi_bbox
    overlay = overlay.resize((x2 - x1, y2 - y1), Image.Resampling.BILINEAR)

    full.paste(overlay, (x1, y1))

    buf = io.BytesIO()
    full.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
```

- [ ] **Step 2: Edit unit tests in `test_overlay.py`**

Add unit tests for the new functions in `backend/tests/unit/services/hirescam/test_overlay.py`:

```python
from app.services.hirescam.overlay import clean_cam, make_transparent_cam_overlay, paste_roi_overlay_to_full

def test_clean_cam_discards_low_activation():
    crop_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    crop_img = Image.fromarray(crop_arr, mode="RGB")
    cam = np.random.rand(10, 10).astype(np.float32)
    cleaned = clean_cam(cam, crop_img, threshold=0.5, use_signal_mask=False)
    assert cleaned.shape == (10, 10)
    assert np.all(cleaned[cam < 0.5] == 0)

def test_make_transparent_cam_overlay_returns_png_bytes():
    crop_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    crop_img = Image.fromarray(crop_arr, mode="RGB")
    cam = np.random.rand(100, 100).astype(np.float32)
    result = make_transparent_cam_overlay(crop_img, cam, max_alpha=0.6)
    assert isinstance(result, bytes)
    assert result[:4] == b"\x89PNG"
```

- [ ] **Step 3: Run overlay unit tests**

Run: `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/services/hirescam/test_overlay.py -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/hirescam/overlay.py backend/tests/unit/services/hirescam/test_overlay.py
git commit -m "feat(hirescam): implement clean_cam, make_transparent_cam_overlay and paste_roi_overlay_to_full"
```

---

## Task 3: Integrate New Overlay Helpers in Orchestrator

**Files:**
- Modify: `backend/app/services/hirescam/orchestrate.py`

- [ ] **Step 1: Edit `orchestrate.py`**

Modify `generate_artifacts` in `backend/app/services/hirescam/orchestrate.py` to use `clean_cam`, `make_transparent_cam_overlay`, and `paste_roi_overlay_to_full` instead of the old constant-alpha `compose_overlay` and `paste_overlay_to_full`:

```python
        # Post-process with tuning params (raw clipping & normalize only)
        processed = postprocess_heatmap(
            heatmap_arr,
            lb_params,
            clip_percentile=config.clip_percentile,
            smooth_sigma=config.smooth_sigma,
            top_percent=config.top_percent,
            colormap=config.colormap,
        )

        from app.services.hirescam.overlay import (
            clean_cam,
            make_transparent_cam_overlay,
            paste_roi_overlay_to_full,
        )

        # We load crop_img directly as Pillow Image
        crop_img = Image.open(cam_source)

        # Clean the heatmap using threshold, gamma, and signal masking
        cam_clean = clean_cam(
            cam=processed["heatmap_norm"],
            crop_img=crop_img,
            threshold=config.cam_threshold,
            gamma=config.cam_gamma,
            use_signal_mask=config.use_signal_mask,
            signal_mask_blur_radius=config.signal_mask_blur_radius,
        )

        # Generate transparent per-pixel alpha overlay on crop
        overlay_png = make_transparent_cam_overlay(
            crop_img=crop_img,
            cam=cam_clean,
            max_alpha=config.max_alpha,
            colormap=config.colormap,
        )

        # Generate standard colored heatmap PNG for DB artifacts
        heatmap_png = array_to_png(cam_clean, colormap=config.colormap)

        # Paste back onto full image if cropped
        if config.use_roi_crop and roi_bbox is not None:
            full_overlay_png = paste_roi_overlay_to_full(
                str(image_path),
                overlay_png,
                roi_bbox,
            )
            # side-by-side: original | heatmap | overlay
            side_by_side_png = compose_side_by_side(
                str(image_path), heatmap_png, full_overlay_png,
            )
        else:
            full_overlay_png = overlay_png
            side_by_side_png = compose_side_by_side(
                str(image_path), heatmap_png, overlay_png,
            )
```

- [ ] **Step 2: Verify syntax**

Run: `backend\.venv\Scripts\python.exe -c "from app.services.hirescam.orchestrate import generate_artifacts; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/orchestrate.py
git commit -m "feat(hirescam): integrate per-pixel alpha overlay pipeline in orchestrator"
```

---

## Task 4: Run Verification Tests

**Files:**
- None (verification only)

- [ ] **Step 1: Reset database configuration**

Run: `backend\.venv\Scripts\python.exe backend/scripts/reset_hirescam_config.py`
Expected: `Successfully reset DB hirescam_config to Kaggle-aligned defaults!`

- [ ] **Step 2: Run all backend tests**

Run: `backend\.venv\Scripts\python.exe -m pytest`
Expected: `364 passed` (all tests green)

- [ ] **Step 3: Commit verification**

```bash
git add -A
git commit -m "test(hirescam): verify all backend tests pass with per-pixel alpha overlay"
```
