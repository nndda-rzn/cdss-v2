# HiResCAM Tuning Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tuning pipeline with configurable HiResCAM generation: letterbox reverse mapping, multi-layer targeting, comprehensive post-processing, and a CLI experiment runner.

**Architecture:** Hybrid approach — shared core logic in `backend/app/services/hirescam/` (letterbox, postprocess, generator rewrite, colormap extension) + standalone CLI runner in `backend/scripts/run_hirescam_tuning.py`. Existing `generate_hirescam` stays for backward compatibility; new `generate_hirescam_v2` is the v2 entry with letterbox + multi-layer support.

**Tech Stack:** Python 3.13, NumPy, OpenCV, Pillow, matplotlib, scipy, ultralytics YOLO, pytest

---

## File Structure

```
backend/app/services/hirescam/
├── __init__.py              (MODIFY — export new symbols)
├── letterbox.py             (CREATE — letterbox + reverse mapping)
├── postprocess.py           (CREATE — full post-processing pipeline)
├── generator.py             (MODIFY — add find_conv_layers, select_target_layer, generate_hirescam_v2)
├── colormap.py              (MODIFY — extend to support multiple colormaps)
├── evaluator.py             (no change)
├── overlay.py               (no change)
├── orchestrate.py           (MODIFY — swap to v2 generator in Task 7)

backend/scripts/
├── run_hirescam_tuning.py   (CREATE — CLI experiment runner)

backend/tests/unit/services/hirescam/
├── test_letterbox.py        (CREATE — 8 tests)
├── test_postprocess.py      (CREATE — 6 tests)
├── test_generator_v2.py     (CREATE — 7 tests)
├── test_colormap.py         (MODIFY — add 4 multi-colormap tests)
├── test_evaluator.py        (no change)
├── test_overlay.py          (no change)
```

---

## Task 1: Letterbox Module

**Files:**
- Create: `backend/app/services/hirescam/letterbox.py`
- Create: `backend/tests/unit/services/hirescam/test_letterbox.py`

- [ ] **Step 1: Write failing tests for LetterboxParams, letterbox, reverse_letterbox**

```python
# backend/tests/unit/services/hirescam/test_letterbox.py
import numpy as np
import pytest
from app.services.hirescam.letterbox import LetterboxParams, letterbox, reverse_letterbox


class TestLetterboxParams:
    def test_dataclass_fields(self):
        p = LetterboxParams(
            ratio=0.714, pad_top=123, pad_bottom=123,
            pad_left=0, pad_right=0, orig_h=1572, orig_w=2213, target_size=1600
        )
        assert p.ratio == 0.714
        assert p.pad_top == 123
        assert p.orig_h == 1572


class TestLetterbox:
    def test_output_is_square(self):
        img = np.random.randint(0, 255, (1572, 2213, 3), dtype=np.uint8)
        out, params = letterbox(img, target_size=1600)
        assert out.shape == (1600, 1600, 3)

    def test_params_contain_orig_dims(self):
        img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        out, params = letterbox(img, target_size=416)
        assert params.orig_h == 100
        assert params.orig_w == 200
        assert params.target_size == 416
        assert out.shape == (416, 416, 3)

    def test_fill_color_applied(self):
        img = np.ones((50, 100, 3), dtype=np.uint8) * 128
        out, params = letterbox(img, target_size=200, fill_color=(0, 0, 0))
        # padding region should be 0
        assert out[0, 0, 0] == 0

    def test_grayscale_input_rejected(self):
        img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-channel"):
            letterbox(img, target_size=200)


class TestReverseLetterbox:
    def test_roundtrip_dimensions(self):
        orig = np.random.randint(0, 255, (1572, 2213, 3), dtype=np.uint8)
        padded, params = letterbox(orig, target_size=1600)
        recovered = reverse_letterbox(padded, params)
        assert recovered.shape == (1572, 2213, 3)

    def test_heatmap_roundtrip_2d(self):
        """2D heatmap should survive letterbox → reverse_letterbox roundtrip."""
        from PIL import Image
        orig = np.random.rand(1572, 2213).astype(np.float32)
        orig_pil = Image.fromarray((orig * 255).astype(np.uint8), mode="L")
        resized = orig_pil.resize((1600, 1600), Image.BILINEAR)
        arr = np.array(resized).astype(np.float32) / 255.0
        params = LetterboxParams(
            ratio=1600 / 2213, pad_top=0, pad_bottom=0,
            pad_left=0, pad_right=0, orig_h=1572, orig_w=2213, target_size=1600
        )
        recovered = reverse_letterbox(arr, params)
        assert recovered.shape == (1572, 2213)

    def test_crop_removes_padding(self):
        """reverse_letterbox should crop before resize."""
        arr = np.ones((200, 200), dtype=np.float32)
        params = LetterboxParams(
            ratio=0.5, pad_top=50, pad_bottom=50,
            pad_left=50, pad_right=50, orig_h=100, orig_w=100, target_size=200
        )
        recovered = reverse_letterbox(arr, params)
        assert recovered.shape == (100, 100)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_letterbox.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.hirescam.letterbox'`

- [ ] **Step 3: Implement letterbox.py**

```python
# backend/app/services/hirescam/letterbox.py
"""Custom letterbox preprocessing + reverse mapping for HiResCAM."""
from __future__ import annotations

from dataclasses import dataclass
import cv2
import numpy as np


@dataclass(frozen=True)
class LetterboxParams:
    """Parameters from letterbox preprocessing, needed for reverse mapping."""
    ratio: float
    pad_top: int
    pad_bottom: int
    pad_left: int
    pad_right: int
    orig_h: int
    orig_w: int
    target_size: int


def letterbox(
    img: np.ndarray,
    target_size: int,
    fill_color: tuple[int, int, int] = (114, 114, 114),
) -> tuple[np.ndarray, LetterboxParams]:
    """Resize image with padding to target_size x target_size.

    Preserves aspect ratio by fitting the image within the square and
    centering it with fill_color padding.

    Args:
        img: Input image (H, W, 3) uint8 RGB.
        target_size: Target square size.
        fill_color: Padding fill color (default: YOLO standard 114,114,114).

    Returns:
        (padded_image, letterbox_params)

    Raises:
        ValueError: If input is not a 3-channel image.
    """
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Input image must be a 3-channel RGB image (H, W, 3)")

    orig_h, orig_w = img.shape[:2]
    ratio = min(target_size / orig_w, target_size / orig_h)
    new_w = int(orig_w * ratio)
    new_h = int(orig_h * ratio)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    canvas = np.full((target_size, target_size, 3), fill_color, dtype=np.uint8)
    pad_top = (target_size - new_h) // 2
    pad_left = (target_size - new_w) // 2
    canvas[pad_top: pad_top + new_h, pad_left: pad_left + new_w] = resized

    params = LetterboxParams(
        ratio=ratio,
        pad_top=pad_top,
        pad_bottom=target_size - new_h - pad_top,
        pad_left=pad_left,
        pad_right=target_size - new_w - pad_left,
        orig_h=orig_h,
        orig_w=orig_w,
        target_size=target_size,
    )
    return canvas, params


def reverse_letterbox(heatmap: np.ndarray, params: LetterboxParams) -> np.ndarray:
    """Remove letterbox padding and resize heatmap to original image dimensions.

    This is the critical function that prevents overlay shift — it crops
    the padding that was added during letterbox, then resizes to the
    original image dimensions.

    Args:
        heatmap: 2D (H, W) or 3D (H, W, C) array from the letterboxed space.
        params: LetterboxParams from the forward letterbox call.

    Returns:
        Heatmap resized to (orig_h, orig_w).

    Raises:
        ValueError: If heatmap is not 2D or 3D.
    """
    if heatmap.ndim == 2:
        h, w = heatmap.shape
        crop = heatmap[
            params.pad_top: h - params.pad_bottom,
            params.pad_left: w - params.pad_right,
        ]
    elif heatmap.ndim == 3:
        h, w = heatmap.shape[:2]
        crop = heatmap[
            params.pad_top: h - params.pad_bottom,
            params.pad_left: w - params.pad_right,
        ]
    else:
        raise ValueError(f"Heatmap must be 2D or 3D, got {heatmap.ndim}D")

    return cv2.resize(crop, (params.orig_w, params.orig_h), interpolation=cv2.INTER_LINEAR)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_letterbox.py -v`
Expected: 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/hirescam/letterbox.py backend/tests/unit/services/hirescam/test_letterbox.py
git commit -m "feat(hirescam): add letterbox module with reverse mapping"
```

---

## Task 2: Colormap Extension

**Files:**
- Modify: `backend/app/services/hirescam/colormap.py`
- Modify: `backend/tests/unit/services/hirescam/test_colormap.py`

- [ ] **Step 1: Write failing tests for multi-colormap support**

Append to `backend/tests/unit/services/hirescam/test_colormap.py`:

```python
import pytest
from app.services.hirescam.colormap import array_to_png, SUPPORTED_COLORMAPS


class TestSupportedColormaps:
    def test_list_contains_inferno(self):
        assert "inferno" in SUPPORTED_COLORMAPS

    def test_list_contains_turbo(self):
        assert "turbo" in SUPPORTED_COLORMAPS

    def test_all_colormaps_produce_png(self):
        arr = np.random.rand(32, 32).astype(np.float32)
        for cmap in SUPPORTED_COLORMAPS:
            result = array_to_png(arr, colormap=cmap)
            assert result[:4] == b"\x89PNG", f"Failed for colormap={cmap}"

    def test_unknown_colormap_raises(self):
        arr = np.random.rand(32, 32).astype(np.float32)
        with pytest.raises(ValueError, match="Unsupported colormap"):
            array_to_png(arr, colormap="nonexistent")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_colormap.py::TestSupportedColormaps -v`
Expected: FAIL — `array_to_png() got an unexpected keyword argument 'colormap'`

- [ ] **Step 3: Implement multi-colormap support**

Replace the full content of `backend/app/services/hirescam/colormap.py`:

```python
# backend/app/services/hirescam/colormap.py
"""Apply colormaps to normalized heatmaps."""
from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.cm as cm
import numpy as np
from matplotlib.colors import Normalize
from PIL import Image

SUPPORTED_COLORMAPS = ["inferno", "turbo", "jet", "viridis", "plasma"]

_COLORMAP_REGISTRY = {
    name: cm.get_cmap(name) for name in SUPPORTED_COLORMAPS
}


def array_to_png(arr: np.ndarray, *, colormap: str = "inferno") -> bytes:
    """Convert a 2D float array [0..1] to PNG bytes using the given colormap.

    Args:
        arr: 2D numpy array with values in [0, 1].
        colormap: Name of matplotlib colormap.

    Returns:
        PNG-encoded bytes.

    Raises:
        ValueError: If arr is not 2D or colormap is unsupported.
    """
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D array, got {arr.ndim}D")
    if colormap not in _COLORMAP_REGISTRY:
        raise ValueError(
            f"Unsupported colormap '{colormap}'. "
            f"Choose from: {SUPPORTED_COLORMAPS}"
        )

    cmap = _COLORMAP_REGISTRY[colormap]
    norm = Normalize(0, 1)
    rgba = cmap(norm(arr))
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)

    img = Image.fromarray(rgb, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
```

- [ ] **Step 4: Run all colormap tests**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_colormap.py -v`
Expected: all tests PASS (existing 4 + new 4 = 8)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/hirescam/colormap.py backend/tests/unit/services/hirescam/test_colormap.py
git commit -m "feat(hirescam): extend colormap to support turbo/jet/viridis/plasma"
```

---

## Task 3: Post-processing Module

**Files:**
- Create: `backend/app/services/hirescam/postprocess.py`
- Create: `backend/tests/unit/services/hirescam/test_postprocess.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/unit/services/hirescam/test_postprocess.py
import numpy as np
import pytest
from app.services.hirescam.letterbox import LetterboxParams
from app.services.hirescam.postprocess import postprocess_heatmap


def _fake_params(orig_h=100, orig_w=200, target_size=416):
    return LetterboxParams(
        ratio=target_size / max(orig_w, orig_h),
        pad_top=0, pad_bottom=0, pad_left=0, pad_right=0,
        orig_h=orig_h, orig_w=orig_w, target_size=target_size,
    )


class TestPostprocessHeatmap:
    def test_output_keys(self):
        hm = np.random.rand(416, 416).astype(np.float32)
        params = _fake_params()
        result = postprocess_heatmap(hm, params)
        assert "heatmap_raw" in result
        assert "heatmap_norm" in result
        assert "heatmap_colored" in result
        assert "mask_top_area" in result

    def test_output_matches_original_dims(self):
        hm = np.random.rand(416, 416).astype(np.float32)
        params = _fake_params(orig_h=150, orig_w=300)
        result = postprocess_heatmap(hm, params)
        assert result["heatmap_norm"].shape == (150, 300)
        assert result["heatmap_colored"].shape == (150, 300, 3)

    def test_clip_percentile(self):
        hm = np.random.rand(64, 64).astype(np.float32)
        hm[0, 0] = 100.0  # outlier
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        result = postprocess_heatmap(hm, params, clip_percentile=99.0)
        # After clipping + normalization, outlier should be capped
        assert result["heatmap_norm"].max() <= 1.0

    def test_top_percent_mask(self):
        hm = np.zeros((64, 64), dtype=np.float32)
        hm[30:34, 30:34] = 1.0  # small hot spot
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        result = postprocess_heatmap(hm, params, top_percent=5.0)
        mask = result["mask_top_area"]
        assert mask.sum() > 0
        assert mask.sum() / mask.size <= 0.15  # roughly top 5% ± margin

    def test_smooth_sigma_zero_no_blur(self):
        hm = np.zeros((64, 64), dtype=np.float32)
        hm[32, 32] = 1.0
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        result = postprocess_heatmap(hm, params, smooth_sigma=0)
        # With sigma=0, max should still be at center
        assert result["heatmap_norm"].max() == result["heatmap_norm"][32, 32]

    def test_different_colormaps(self):
        hm = np.random.rand(64, 64).astype(np.float32)
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        r1 = postprocess_heatmap(hm, params, colormap="turbo")
        r2 = postprocess_heatmap(hm, params, colormap="inferno")
        # Different colormaps → different colored output
        assert not np.array_equal(r1["heatmap_colored"], r2["heatmap_colored"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_postprocess.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.hirescam.postprocess'`

- [ ] **Step 3: Implement postprocess.py**

```python
# backend/app/services/hirescam/postprocess.py
"""Heatmap post-processing pipeline for HiResCAM tuning."""
from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from app.services.hirescam.letterbox import LetterboxParams, reverse_letterbox
from app.services.hirescam.colormap import array_to_png


def postprocess_heatmap(
    heatmap: np.ndarray,
    letterbox_params: LetterboxParams,
    clip_percentile: float = 99.0,
    smooth_sigma: float = 1.0,
    top_percent: float = 20.0,
    colormap: str = "inferno",
) -> dict[str, np.ndarray]:
    """Full post-processing pipeline.

    Steps:
        1. Percentile clipping (remove outliers)
        2. Min-max normalization
        3. Reverse letterbox (remove padding + resize to original dims)
        4. Gaussian smoothing
        5. Top percent thresholding
        6. Apply colormap

    Args:
        heatmap: Raw HiResCAM 2D array (letterboxed space).
        letterbox_params: Parameters from letterbox preprocessing.
        clip_percentile: Percentile for outlier clipping (default 99.0).
        smooth_sigma: Gaussian smoothing sigma, 0 = no smoothing (default 1.0).
        top_percent: Top percent of activation to mask (default 20.0).
        colormap: Matplotlib colormap name (default "inferno").

    Returns:
        dict with keys: heatmap_raw, heatmap_norm, heatmap_colored, mask_top_area
    """
    raw = heatmap.copy()

    # 1. Percentile clipping
    cap = np.percentile(heatmap, clip_percentile)
    clipped = np.clip(heatmap, 0, cap)

    # 2. Min-max normalization
    h_min, h_max = clipped.min(), clipped.max()
    if h_max - h_min > 1e-8:
        normalized = (clipped - h_min) / (h_max - h_min)
    else:
        normalized = np.zeros_like(clipped)

    # 3. Reverse letterbox (remove padding + resize to original dims)
    norm_recovered = reverse_letterbox(normalized, letterbox_params)

    # Ensure float32
    norm_recovered = norm_recovered.astype(np.float32)

    # 4. Gaussian smoothing
    if smooth_sigma > 0:
        norm_recovered = gaussian_filter(norm_recovered, sigma=smooth_sigma)
        # Re-normalize after smoothing
        s_min, s_max = norm_recovered.min(), norm_recovered.max()
        if s_max - s_min > 1e-8:
            norm_recovered = (norm_recovered - s_min) / (s_max - s_min)

    # 5. Top percent thresholding
    if 0 < top_percent < 100:
        threshold = np.percentile(norm_recovered, 100 - top_percent)
        mask_top = (norm_recovered >= threshold).astype(np.uint8)
    else:
        mask_top = np.ones_like(norm_recovered, dtype=np.uint8)

    # 6. Apply colormap
    colored_bytes = array_to_png(norm_recovered, colormap=colormap)
    colored_img = Image.open(io.BytesIO(colored_bytes)).convert("RGB")
    colored_rgb = np.array(colored_img)

    return {
        "heatmap_raw": raw,
        "heatmap_norm": norm_recovered,
        "heatmap_colored": colored_rgb,
        "mask_top_area": mask_top,
    }
```

- [ ] **Step 4: Install scipy**

Run: `cd backend && pip install scipy`
Expected: installed or already present

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_postprocess.py -v`
Expected: 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/hirescam/postprocess.py backend/tests/unit/services/hirescam/test_postprocess.py
git commit -m "feat(hirescam): add postprocess module with clip/smooth/top_percent pipeline"
```

---

## Task 4: Generator Rewrite — Multi-Layer + Configurable Input Size

**Files:**
- Modify: `backend/app/services/hirescam/generator.py`
- Create: `backend/tests/unit/services/hirescam/test_generator_v2.py`

- [ ] **Step 1: Write failing tests for new generator functions**

```python
# backend/tests/unit/services/hirescam/test_generator_v2.py
import numpy as np
import pytest
import torch
import torch.nn as nn
from unittest.mock import MagicMock
from app.services.hirescam.generator import (
    find_conv_layers,
    select_target_layer,
)


class _FakeConv(nn.Module):
    def __init__(self, out_channels):
        super().__init__()
        self.conv = nn.Conv2d(3, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class _FakeModel:
    """Mimics ultralytics YOLO wrapper."""
    def __init__(self):
        self._conv1 = _FakeConv(16)
        self._conv2 = _FakeConv(32)
        self._conv3 = _FakeConv(64)
        self._model = nn.Sequential(self._conv1, self._conv2, self._conv3)
        self._model.f = lambda x: x
        self.args = {"imgsz": 224}

    @property
    def model(self):
        return self._model

    def predict(self, *a, **kw):
        return MagicMock()


class TestFindConvLayers:
    def test_returns_all_conv_layers(self):
        fake = _FakeModel()
        layers = find_conv_layers(fake)
        assert len(layers) == 3

    def test_filters_small_output(self):
        """Conv2d with out_channels <= 4 should be excluded."""
        model = MagicMock()
        small_conv = nn.Conv2d(3, 2, kernel_size=1)
        big_conv = nn.Conv2d(3, 64, kernel_size=1)
        model.model.modules.return_value = [small_conv, big_conv]
        layers = find_conv_layers(model)
        assert big_conv in layers
        assert small_conv not in layers

    def test_empty_model_raises(self):
        model = MagicMock()
        model.model.modules.return_value = []
        with pytest.raises(RuntimeError, match="No Conv2d"):
            find_conv_layers(model)


class TestSelectTargetLayer:
    def test_last_conv(self):
        convs = [MagicMock(name="c1"), MagicMock(name="c2"), MagicMock(name="c3")]
        result = select_target_layer(convs, "last_conv")
        assert result is convs[-1]

    def test_second_last_conv(self):
        convs = [MagicMock(name="c1"), MagicMock(name="c2"), MagicMock(name="c3")]
        result = select_target_layer(convs, "second_last_conv")
        assert result is convs[-2]

    def test_third_last_conv(self):
        convs = [MagicMock(name="c1"), MagicMock(name="c2"), MagicMock(name="c3")]
        result = select_target_layer(convs, "third_last_conv")
        assert result is convs[-3]

    def test_unknown_name_raises(self):
        convs = [MagicMock()]
        with pytest.raises(ValueError, match="Unknown target layer"):
            select_target_layer(convs, "nonexistent")

    def test_too_few_layers_raises(self):
        convs = [MagicMock(name="c1")]
        with pytest.raises(ValueError, match="cannot select"):
            select_target_layer(convs, "second_last_conv")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_generator_v2.py -v`
Expected: FAIL — `ImportError: cannot import name 'find_conv_layers'`

- [ ] **Step 3: Add find_conv_layers, select_target_layer, generate_hirescam_v2 to generator.py**

Append the following to `backend/app/services/hirescam/generator.py` (keep ALL existing functions untouched for backward compat):

```python
# --- NEW: Multi-layer + configurable input size (v2) ---


def find_conv_layers(model: Any) -> list:
    """Return ALL Conv2d layers with out_channels > 4, ordered first to last.

    Args:
        model: Ultralytics YOLO model wrapper.

    Returns:
        List of Conv2d modules.

    Raises:
        RuntimeError: If no valid Conv2d layers found.
    """
    layers = list(model.model.modules())
    conv_layers = [
        m for m in layers
        if isinstance(m, torch.nn.Conv2d) and m.out_channels > 4
    ]
    if not conv_layers:
        raise RuntimeError("No Conv2d layer with out_channels > 4 found in model")
    return conv_layers


def select_target_layer(layers: list, name: str) -> Any:
    """Select a target layer by name.

    Args:
        layers: List of Conv2d layers from find_conv_layers().
        name: One of 'last_conv', 'second_last_conv', 'third_last_conv'.

    Returns:
        The selected Conv2d layer.

    Raises:
        ValueError: If name is unknown or layers list is too short.
    """
    index_map = {
        "last_conv": -1,
        "second_last_conv": -2,
        "third_last_conv": -3,
    }
    if name not in index_map:
        raise ValueError(
            f"Unknown target layer '{name}'. Choose from: {list(index_map.keys())}"
        )
    idx = index_map[name]
    if abs(idx) > len(layers):
        raise ValueError(
            f"Model has {len(layers)} conv layers, cannot select '{name}'"
        )
    return layers[idx]


def generate_hirescam_v2(
    model: Any,
    image_path: str,
    target_class_idx: int,
    *,
    target_layer_name: str = "last_conv",
    input_size: int = 1600,
    device: str = "cpu",
) -> tuple[np.ndarray, Any, dict]:
    """Generate HiResCAM heatmap with configurable input size and target layer.

    Uses custom letterbox preprocessing instead of YOLO's classify_transforms,
    enabling proper reverse mapping to prevent overlay shift.

    Args:
        model: Ultralytics YOLO model wrapper.
        image_path: Path to the input ECG image.
        target_class_idx: Index of the target class for gradient computation.
        target_layer_name: Which conv layer to hook (last_conv, second_last_conv, third_last_conv).
        input_size: Square input size for the model (e.g. 1600, 2048).
        device: 'cpu' or 'cuda'.

    Returns:
        (raw_heatmap, letterbox_params, metadata) where raw_heatmap is 2D [0..1] float32.
    """
    from app.services.hirescam.letterbox import letterbox as custom_letterbox
    from app.services.hirescam.letterbox import reverse_letterbox

    conv_layers = find_conv_layers(model)
    target_layer = select_target_layer(conv_layers, target_layer_name)

    # Warm-up predict (ensures model is loaded)
    model.predict(image_path, verbose=False)

    # Register hooks
    activations: dict[str, torch.Tensor] = {}
    gradients: dict[str, torch.Tensor] = {}

    def fwd_hook(module, inp, output):
        activations["target"] = output.detach()

    def bwd_hook(module, grad_in, grad_out):
        if grad_out[0] is not None:
            gradients["target"] = grad_out[0].detach()

    handle_fwd = target_layer.register_forward_hook(fwd_hook)
    handle_bwd = target_layer.register_full_backward_hook(bwd_hook)

    old_states = _disable_inplace(model.model)

    try:
        # Read + custom letterbox preprocess
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        padded, lb_params = custom_letterbox(img_rgb, target_size=input_size)

        # To tensor (ImageNet normalization)
        tensor = padded.astype(np.float32) / 255.0
        tensor = (tensor - np.array([0.485, 0.456, 0.406])) / np.array(
            [0.229, 0.224, 0.225]
        )
        tensor = tensor.transpose(2, 0, 1)  # CHW
        tensor = torch.from_numpy(tensor).unsqueeze(0).to(device)
        tensor.requires_grad_(True)

        # Forward
        model.model.train()
        output = model.model(tensor)

        # Extract logit for target class
        if hasattr(output, "probs") and output.probs is not None:
            target_score = output.probs.data[0, target_class_idx]
        else:
            logits = output if isinstance(output, torch.Tensor) else output[0]
            target_score = logits[0, target_class_idx]

        # Backward
        model.model.zero_grad()
        target_score.backward()

        # HiResCAM computation
        activs = activations["target"].cpu().numpy()[0]  # (C, H, W)
        grads = gradients["target"].cpu().numpy()[0]  # (C, H, W)

        cams = np.multiply(grads, activs)
        cam = np.sum(cams, axis=0)  # sum over channels
        cam = np.maximum(cam, 0)  # ReLU

        # Normalize
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        # Resize to letterbox size then reverse-map to original
        cam_resized = cv2.resize(
            cam, (input_size, input_size), interpolation=cv2.INTER_LINEAR
        )
        heatmap = reverse_letterbox(cam_resized, lb_params)

        # Metadata
        target_layer_info = str(target_layer)
        confidence = float(target_score.detach().cpu())

        metadata = {
            "image_path": image_path,
            "original_size": [lb_params.orig_h, lb_params.orig_w],
            "input_size": input_size,
            "target_layer": target_layer_name,
            "target_layer_info": target_layer_info,
            "target_class_id": target_class_idx,
            "confidence": confidence,
            "letterbox_ratio": lb_params.ratio,
            "letterbox_padding": {
                "top": lb_params.pad_top,
                "bottom": lb_params.pad_bottom,
                "left": lb_params.pad_left,
                "right": lb_params.pad_right,
            },
        }

        return heatmap, lb_params, metadata

    finally:
        handle_fwd.remove()
        handle_bwd.remove()
        _restore_inplace(old_states)
        model.model.eval()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/test_generator_v2.py tests/unit/services/hirescam/test_generator.py -v`
Expected: all tests PASS (existing 4 + new 7 = 11)

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/hirescam/generator.py backend/tests/unit/services/hirescam/test_generator_v2.py
git commit -m "feat(hirescam): add generate_hirescam_v2 with multi-layer + letterbox support"
```

---

## Task 5: Update __init__.py Exports

**Files:**
- Modify: `backend/app/services/hirescam/__init__.py`

- [ ] **Step 1: Update __init__.py**

```python
# backend/app/services/hirescam/__init__.py
"""HiResCAM explainability services."""
from app.services.hirescam.letterbox import LetterboxParams, letterbox, reverse_letterbox
from app.services.hirescam.postprocess import postprocess_heatmap
from app.services.hirescam.generator import (
    generate_hirescam,
    generate_hirescam_v2,
    find_conv_layers,
    select_target_layer,
)
from app.services.hirescam.colormap import array_to_png, SUPPORTED_COLORMAPS

__all__ = [
    "LetterboxParams",
    "letterbox",
    "reverse_letterbox",
    "postprocess_heatmap",
    "generate_hirescam",
    "generate_hirescam_v2",
    "find_conv_layers",
    "select_target_layer",
    "array_to_png",
    "SUPPORTED_COLORMAPS",
]
```

- [ ] **Step 2: Run all existing tests to verify no regressions**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/ -v`
Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/__init__.py
git commit -m "chore(hirescam): update __init__.py with new exports"
```

---

## Task 6: CLI Experiment Runner

**Files:**
- Create: `backend/scripts/run_hirescam_tuning.py`

- [ ] **Step 1: Implement the CLI runner**

```python
# backend/scripts/run_hirescam_tuning.py
"""CLI tool for HiResCAM tuning experiments.

Generates heatmaps across a grid of configurations and produces
structured output (images + metadata.json + summary.csv).

Usage:
    python scripts/run_hirescam_tuning.py \\
        --model runs/ecg_cls/weights/best.pt \\
        --image data/sample_ecg.png \\
        --output outputs/hirescam_tuning \\
        --input-sizes 1600 2048 \\
        --target-layers last_conv second_last_conv third_last_conv \\
        --smooth-sigmas 0 1.0 1.5 \\
        --top-percents 15 20 25 \\
        --clip-percentiles 99 99.5 \\
        --colormaps turbo inferno \\
        --target-class-mode predicted_class
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from itertools import product
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="HiResCAM tuning experiment runner"
    )
    parser.add_argument("--model", required=True, help="Path to YOLO .pt weights")
    parser.add_argument("--image", required=True, help="Path to input ECG image")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--input-sizes", nargs="+", type=int, default=[1600],
        help="Input sizes to test (default: [1600])"
    )
    parser.add_argument(
        "--target-layers", nargs="+", default=["last_conv"],
        help="Target layers (default: [last_conv])"
    )
    parser.add_argument(
        "--smooth-sigmas", nargs="+", type=float, default=[1.0],
        help="Gaussian smooth sigmas (default: [1.0])"
    )
    parser.add_argument(
        "--top-percents", nargs="+", type=float, default=[20.0],
        help="Top percent thresholds (default: [20.0])"
    )
    parser.add_argument(
        "--clip-percentiles", nargs="+", type=float, default=[99.0],
        help="Clip percentiles (default: [99.0])"
    )
    parser.add_argument(
        "--colormaps", nargs="+", default=["inferno"],
        help="Colormaps to test (default: [inferno])"
    )
    parser.add_argument(
        "--target-class-mode", default="predicted_class",
        choices=["predicted_class", "fixed"],
        help="How to choose target class (default: predicted_class)"
    )
    parser.add_argument(
        "--target-class-idx", type=int, default=0,
        help="Fixed class index (used when target-class-mode=fixed)"
    )
    parser.add_argument(
        "--device", default="cpu", help="Device: cpu or cuda (default: cpu)"
    )
    parser.add_argument(
        "--overlay-alpha", type=float, default=0.45,
        help="Overlay transparency (default: 0.45)"
    )
    return parser.parse_args()


def run_experiment(
    model_path: str,
    image_path: str,
    output_dir: Path,
    config: dict,
    config_idx: int,
    overlay_alpha: float,
    device: str,
) -> dict | None:
    """Run a single experiment configuration.

    Returns:
        Metadata dict for summary.csv, or None on failure.
    """
    from app.services.hirescam.generator import generate_hirescam_v2
    from app.services.hirescam.postprocess import postprocess_heatmap
    from app.services.hirescam.colormap import array_to_png
    from app.services.hirescam.overlay import compose_overlay
    from app.services.hirescam.evaluator import evaluate_explanation
    from app.services.inference.loader import load_model
    from PIL import Image

    try:
        model = load_model(Path(model_path))

        # Determine target class
        if config["target_class_mode"] == "predicted_class":
            result = model.predict(image_path, verbose=False)
            probs = result[0].probs
            target_class_idx = int(probs.top1)
            confidence = float(probs.top1conf)
        else:
            target_class_idx = config["target_class_idx"]
            confidence = None

        # Generate heatmap
        heatmap, lb_params, metadata = generate_hirescam_v2(
            model,
            image_path,
            target_class_idx,
            target_layer_name=config["target_layer"],
            input_size=config["input_size"],
            device=device,
        )

        # Post-process
        processed = postprocess_heatmap(
            heatmap,
            lb_params,
            clip_percentile=config["clip_percentile"],
            smooth_sigma=config["smooth_sigma"],
            top_percent=config["top_percent"],
            colormap=config["colormap"],
        )

        # Save outputs
        cfg_dir = output_dir / f"config_{config_idx:03d}"
        cfg_dir.mkdir(parents=True, exist_ok=True)

        # Original image
        orig = cv2.imread(image_path)
        cv2.imwrite(
            str(cfg_dir / "original.png"),
            cv2.cvtColor(orig, cv2.COLOR_BGR2RGB),
        )

        # Raw heatmap
        np.save(str(cfg_dir / "heatmap_raw.npy"), processed["heatmap_raw"])

        # Normalized heatmap as PNG
        norm_uint8 = (processed["heatmap_norm"] * 255).astype(np.uint8)
        Image.fromarray(norm_uint8, mode="L").save(cfg_dir / "heatmap_norm.png")

        # Colored heatmap
        Image.fromarray(
            processed["heatmap_colored"], mode="RGB"
        ).save(cfg_dir / "heatmap_colored.png")

        # Overlay
        colored_bytes = array_to_png(
            processed["heatmap_norm"], colormap=config["colormap"]
        )
        overlay_bytes = compose_overlay(image_path, colored_bytes)
        with open(cfg_dir / "overlay.png", "wb") as f:
            f.write(overlay_bytes)

        # Mask top area
        mask_uint8 = (processed["mask_top_area"] * 255).astype(np.uint8)
        Image.fromarray(mask_uint8, mode="L").save(cfg_dir / "mask_top_area.png")

        # Metadata
        metadata.update({
            "config_index": config_idx,
            "clip_percentile": config["clip_percentile"],
            "smooth_sigma": config["smooth_sigma"],
            "top_percent": config["top_percent"],
            "colormap": config["colormap"],
            "overlay_alpha": overlay_alpha,
        })
        with open(cfg_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Evaluate
        status, focus_metric = evaluate_explanation(
            processed["heatmap_norm"], confidence=confidence
        )
        metadata["explanation_status"] = status
        metadata["focus_metric"] = focus_metric

        return metadata

    except Exception as e:
        print(f"  [ERROR] Config {config_idx}: {e}", file=sys.stderr)
        return None


def main():
    args = parse_args()

    if not os.path.isfile(args.model):
        print(f"Error: Model file not found: {args.model}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build experiment grid
    grid = list(product(
        args.input_sizes,
        args.target_layers,
        args.smooth_sigmas,
        args.top_percents,
        args.clip_percentiles,
        args.colormaps,
    ))

    print(f"Running {len(grid)} experiments...")
    print(f"  Model: {args.model}")
    print(f"  Image: {args.image}")
    print(f"  Output: {output_dir}")
    print(f"  Device: {args.device}")

    results = []
    for idx, (inp_size, tgt_layer, smooth, top_pct, clip_pct, cmap) in enumerate(grid, 1):
        config = {
            "input_size": inp_size,
            "target_layer": tgt_layer,
            "smooth_sigma": smooth,
            "top_percent": top_pct,
            "clip_percentile": clip_pct,
            "colormap": cmap,
            "target_class_mode": args.target_class_mode,
            "target_class_idx": args.target_class_idx,
        }
        print(
            f"  [{idx}/{len(grid)}] input={inp_size} layer={tgt_layer} "
            f"smooth={smooth} top={top_pct} clip={clip_pct} cmap={cmap}"
        )

        meta = run_experiment(
            args.model, args.image, output_dir, config, idx,
            args.overlay_alpha, args.device,
        )
        if meta:
            results.append(meta)

    # Write summary.csv
    if results:
        csv_path = output_dir / "summary.csv"
        fieldnames = list(results[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nDone. {len(results)}/{len(grid)} experiments succeeded.")
        print(f"Summary: {csv_path}")
    else:
        print("\nNo experiments succeeded.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify script runs (dry help)**

Run: `cd backend && python scripts/run_hirescam_tuning.py --help`
Expected: Shows argparse help text with all arguments

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/run_hirescam_tuning.py
git commit -m "feat(hirescam): add CLI experiment runner for tuning pipeline"
```

---

## Task 7: Integrate v2 Generator into Production Orchestration

**Files:**
- Modify: `backend/app/services/hirescam/orchestrate.py`

- [ ] **Step 1: Update generate_artifacts to use generate_hirescam_v2**

In `backend/app/services/hirescam/orchestrate.py`, find the call to `generate_hirescam` inside `generate_artifacts` and replace it.

Replace:
```python
heatmap_arr = generate_hirescam(
    yolo_model, str(image_path), class_idx, device="cpu"
)
```

With:
```python
from app.services.hirescam.generator import generate_hirescam_v2

heatmap_arr, lb_params, _ = generate_hirescam_v2(
    yolo_model, str(image_path), class_idx,
    target_layer_name="last_conv",
    input_size=1600,
    device="cpu",
)
```

- [ ] **Step 2: Run all tests to verify no regressions**

Run: `cd backend && python -m pytest tests/unit/services/hirescam/ tests/integration/test_hirescam_api.py -v`
Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/orchestrate.py
git commit -m "feat(hirescam): use generate_hirescam_v2 in production orchestration"
```

---

## Task 8: Add scipy Dependency

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: Add scipy to dependencies**

In `backend/pyproject.toml`, add `"scipy>=1.12"` to the `[project.dependencies]` list.

- [ ] **Step 2: Verify install**

Run: `cd backend && pip install -e ".[inference]"`
Expected: scipy installed

- [ ] **Step 3: Commit**

```bash
git add backend/pyproject.toml
git commit -m "chore: add scipy dependency for gaussian smoothing"
```

---

## Task 9: Final Verification — Full Test Suite

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -v --tb=short`
Expected: ALL tests PASS (unit + integration)

- [ ] **Step 2: Run frontend tests**

Run: `cd frontend && npx vitest run`
Expected: ALL tests PASS

- [ ] **Step 3: Verify CLI runner with --help**

Run: `cd backend && python scripts/run_hirescam_tuning.py --help`
Expected: Shows help text with all arguments

---

## Summary

| Task | Files | Tests |
|------|-------|-------|
| 1. Letterbox | `letterbox.py` + test | 8 |
| 2. Colormap | `colormap.py` modify + test | +4 |
| 3. Postprocess | `postprocess.py` + test | 6 |
| 4. Generator v2 | `generator.py` modify + test | 7 |
| 5. Exports | `__init__.py` modify | regression |
| 6. CLI runner | `run_hirescam_tuning.py` | manual |
| 7. Orchestrate | `orchestrate.py` modify | regression |
| 8. Dependencies | `pyproject.toml` | — |
| 9. Final verification | — | full suite |

**Total new tests: 25 + regression**
