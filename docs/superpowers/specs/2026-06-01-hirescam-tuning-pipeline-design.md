# HiResCAM Tuning Pipeline Design Spec

- Status: Accepted
- Date: 2026-06-01
- Author: Maintainer
- Related: ADR-0013 (inferno colormap), Grand PRD Section 10 (HiResCAM), Sprint 4

## Context

HiResCAM explainability layer for YOLO ECG classification models needs a comprehensive tuning pipeline. Current implementation (`backend/app/services/hirescam/generator.py`) has limitations:
- Hardcoded input size (model default 224)
- Only targets last Conv2d layer
- No letterbox reverse mapping (overlay shifts)
- Minimal post-processing (just normalize + resize)
- No structured output for research/audit

The pipeline must support:
- Configurable input sizes (1600, 2048) for higher resolution heatmaps
- Multiple target layers for comparison
- Letterbox reverse mapping to prevent overlay shift
- Comprehensive post-processing (clip, smooth, top_percent)
- Automated experiment grid with structured output
- CPU-first for low-resource settings

## Architecture

### Hybrid: Shared Core + Standalone Runner

Core logic lives in `backend/app/services/hirescam/` (shared with production API).
CLI runner lives in `scripts/run_hirescam_tuning.py` (standalone experiment tool).

### Data Flow

```
Input PNG (2213×1572)
    ↓
letterbox(img, input_size) → padded_img + LetterboxParams(ratio, padding)
    ↓
padded_img → tensor (normalize, to_device, requires_grad)
    ↓
model.model(tensor) → activations[target_layer] + output logits
    ↓
backward(target_class_logit) → gradients[target_layer]
    ↓
HiResCAM = ReLU(sum(activations * gradients, axis=channels))
    ↓
postprocess(heatmap, params) → resized to 2213×1572
    ↓
overlay(original, heatmap, alpha) → final PNG
```

## Components

### 1. Letterbox Module (`letterbox.py`)

**Responsibility:** Custom letterbox preprocessing + reverse mapping.

```python
@dataclass
class LetterboxParams:
    ratio: float           # resize ratio
    pad_top: int           # padding pixels
    pad_bottom: int
    pad_left: int
    pad_right: int
    orig_h: int            # original height
    orig_w: int            # original width
    target_size: int       # target input size

def letterbox(img: np.ndarray, target_size: int, fill_color=(114,114,114)) -> tuple[np.ndarray, LetterboxParams]:
    """Resize image with padding to target_size×target_size."""

def reverse_letterbox(heatmap: np.ndarray, params: LetterboxParams) -> np.ndarray:
    """Remove padding and resize heatmap to original image dimensions."""
```

### 2. Post-processing Module (`postprocess.py`)

**Responsibility:** Heatmap post-processing pipeline.

```python
def postprocess_heatmap(
    heatmap: np.ndarray,
    letterbox_params: LetterboxParams,
    clip_percentile: float = 99.0,
    smooth_sigma: float = 1.0,
    top_percent: float = 20.0,
    colormap: str = "turbo",
) -> dict[str, np.ndarray]:
    """Full post-processing pipeline.
    Returns: {heatmap_raw, heatmap_norm, heatmap_colored, mask_top_area}
    """
```

Pipeline steps:
1. Percentile clipping (remove outliers)
2. Min-max normalization
3. Resize to letterbox size
4. Remove letterbox padding (reverse mapping)
5. Resize to original (2213×1572)
6. Optional Gaussian smoothing
7. Top percent thresholding
8. Apply colormap

### 3. Generator Rewrite (`generator.py`)

**Responsibility:** HiResCAM heatmap generation with multi-layer support.

```python
def find_conv_layers(model: YOLO) -> list[torch.nn.Conv2d]:
    """Return ALL Conv2d layers ordered from first to last."""

def select_target_layer(layers: list, name: str) -> torch.nn.Conv2d:
    """Select layer by name: last_conv, second_last_conv, third_last_conv."""

def generate_hirescam(
    model: YOLO,
    image_path: str,
    target_class_idx: int,
    target_layer_name: str = "last_conv",
    input_size: int = 1600,
    device: str = "cpu",
) -> tuple[np.ndarray, LetterboxParams, dict]:
    """Returns (raw_heatmap, letterbox_params, metadata)."""
```

Key changes:
- Override YOLO's letterbox with custom letterbox
- Extract raw logits (not softmax probabilities)
- Support multiple target layers
- Return letterbox params for reverse mapping

### 4. Colormap Extension (`colormap.py`)

**Responsibility:** Apply colormaps to normalized heatmaps.

```python
SUPPORTED_COLORMAPS = ["inferno", "turbo", "jet", "viridis", "plasma"]

def apply_colormap(heatmap: np.ndarray, colormap: str = "turbo") -> np.ndarray:
    """Apply colormap to normalized heatmap [0..1], return RGB uint8."""
```

### 5. Experiment Runner (`run_hirescam_tuning.py`)

**Responsibility:** CLI tool for automated tuning experiments.

```bash
python scripts/run_hirescam_tuning.py \
  --model runs/ecg_cls/weights/best.pt \
  --image data/sample_ecg.png \
  --output outputs/hirescam_tuning \
  --input-sizes 1600 2048 \
  --target-layers last_conv second_last_conv third_last_conv \
  --smooth-sigmas 0 1.0 1.5 \
  --top-percents 15 20 25 \
  --clip-percentiles 99 99.5 \
  --colormaps turbo inferno \
  --target-class-mode predicted_class
```

## Output Structure

```
outputs/hirescam_tuning/
├── sample_ecg/
│   ├── config_001/
│   │   ├── original.png
│   │   ├── heatmap_raw.npy
│   │   ├── heatmap_norm.png
│   │   ├── overlay.png
│   │   ├── mask_top_area.png
│   │   └── metadata.json
│   ├── config_002/
│   └── ...
└── summary.csv
```

## Metadata Format

```json
{
  "image_path": "data/sample_ecg.png",
  "original_size": [1572, 2213],
  "input_size": 1600,
  "target_layer": "last_conv",
  "target_layer_info": "Conv2d(256, 1280, kernel_size=(1,1))",
  "target_class_id": 0,
  "target_class_name": "myocardial_infarction",
  "confidence": 0.9847,
  "clip_percentile": 99.0,
  "smooth_sigma": 1.0,
  "top_percent": 20.0,
  "overlay_alpha": 0.45,
  "colormap": "turbo",
  "letterbox_ratio": 0.714,
  "letterbox_padding": {"top": 123, "bottom": 123, "left": 0, "right": 0}
}
```

## Constraints

- CPU-first (low-resource settings), optional GPU via `--device cuda`
- Single image processing (batch deferred to future)
- No model training or retraining
- All colormaps supported for tuning; inferno locked for production (ADR-0013)
- Output resolution must match original (2213×1572) — no cropping

## Acceptance Criteria

- [ ] Heatmap overlay aligns precisely with original ECG (no letterbox shift)
- [ ] All 3 target layers produce different heatmaps for comparison
- [ ] Input sizes 1600 and 2048 produce higher resolution heatmaps than default 224
- [ ] Post-processing parameters (clip, smooth, top_percent) are configurable
- [ ] Experiment grid generates all combinations with structured output
- [ ] summary.csv contains all experiment results
- [ ] metadata.json contains all parameters for reproducibility
- [ ] Script runs from CLI with argparse
- [ ] Error handling for missing model/image/layer
