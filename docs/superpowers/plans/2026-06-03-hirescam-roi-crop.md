# HiResCAM ROI Crop Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crop ECG ROI before YOLO inference + HiResCAM generation, then paste the overlay back onto the full report — matching the Kaggle pipeline that produces accurate, focused heatmaps.

**Architecture:** Add `ecg_crop.py` module with `crop_ecg_roi()` and `paste_overlay_to_full()`. Wire crop into both inference orchestrate (for predict) and HiResCAM orchestrate (for CAM + overlay). All HiResCAM functions accept path strings, so cropped images are saved to temp files before passing downstream.

**Tech Stack:** Python, Pillow, OpenCV, numpy, tempfile, SQLAlchemy.

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `backend/app/services/hirescam/ecg_crop.py` | **Create** | `crop_ecg_roi()`, `paste_overlay_to_full()` |
| `backend/app/services/hirescam/config.py:8-26` | **Modify** | Add `roi_x1`, `roi_y1`, `roi_x2`, `roi_y2` fields |
| `backend/app/services/inference/orchestrate.py:106-151` | **Modify** | Crop before `run_inference()` |
| `backend/app/services/hirescam/orchestrate.py:23-145` | **Modify** | Crop before HiResCAM, paste back after overlay |
| `backend/app/services/hirescam/overlay.py:9-28` | **Modify** | Update `compose_overlay()` to support crop coords |

---

## Task 1: Create `ecg_crop.py` — Crop and Paste Functions

**Files:**
- Create: `backend/app/services/hirescam/ecg_crop.py`

- [ ] **Step 1: Write `ecg_crop.py`**

```python
"""ECG ROI cropping utilities for HiResCAM pipeline."""
from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image


def crop_ecg_roi(
    image_path: str | Path,
    *,
    roi_x1: float = 0.03,
    roi_y1: float = 0.23,
    roi_x2: float = 0.98,
    roi_y2: float = 0.94,
) -> tuple[Path, tuple[int, int, int, int]]:
    """Crop ECG signal ROI from full report image.

    Args:
        image_path: Path to full ECG report image.
        roi_x1: Left edge as fraction of width (0..1).
        roi_y1: Top edge as fraction of height (0..1).
        roi_x2: Right edge as fraction of width (0..1).
        roi_y2: Bottom edge as fraction of height (0..1).

    Returns:
        (temp_crop_path, (abs_x1, abs_y1, abs_x2, abs_y2)) where temp_crop_path
        is a temporary PNG file that must be cleaned up by the caller.
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    abs_x1 = int(w * roi_x1)
    abs_y1 = int(h * roi_y1)
    abs_x2 = int(w * roi_x2)
    abs_y2 = int(h * roi_y2)

    crop_box = (abs_x1, abs_y1, abs_x2, abs_y2)
    cropped = img.crop(crop_box)

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="ecg_crop_")
    cropped.save(tmp.name, format="PNG")
    tmp.close()

    return Path(tmp.name), (abs_x1, abs_y1, abs_x2, abs_y2)


def paste_overlay_to_full(
    full_image_path: str | Path,
    overlay_image_path: str | Path,
    roi_bbox: tuple[int, int, int, int],
) -> bytes:
    """Paste overlay image back onto full report at ROI coordinates.

    Args:
        full_image_path: Path to original full ECG report.
        overlay_image_path: Path to overlay image (heatmap blended with crop).
        roi_bbox: (abs_x1, abs_y1, abs_x2, abs_y2) pixel coordinates.

    Returns:
        PNG bytes of the full report with overlay pasted at ROI.
    """
    import io

    full = Image.open(full_image_path).convert("RGB")
    overlay = Image.open(overlay_image_path).convert("RGB")

    # Resize overlay to match ROI dimensions
    roi_w = roi_bbox[2] - roi_bbox[0]
    roi_h = roi_bbox[3] - roi_bbox[1]
    overlay = overlay.resize((roi_w, roi_h), Image.Resampling.LANCZOS)

    full.paste(overlay, (roi_bbox[0], roi_bbox[1]))

    buf = io.BytesIO()
    full.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
```

- [ ] **Step 2: Verify no syntax errors**

Run: `python -c "from app.services.hirescam.ecg_crop import crop_ecg_roi, paste_overlay_to_full; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/ecg_crop.py
git commit -m "feat(hirescam): add ecg_crop module for ROI cropping and paste-back"
```

---

## Task 2: Add ROI Coordinates to HiResCAMConfig

**Files:**
- Modify: `backend/app/services/hirescam/config.py:8-26`

- [ ] **Step 1: Add ROI fields to config**

```python
@dataclass
class HiResCAMConfig:
    # ... existing fields ...
    signal_mask_blur_radius: int = 5
    roi_x1: float = 0.03
    roi_y1: float = 0.23
    roi_x2: float = 0.98
    roi_y2: float = 0.94
    use_roi_crop: bool = True
```

- [ ] **Step 2: Verify config loads**

Run: `python -c "from app.services.hirescam.config import HiResCAMConfig; c = HiResCAMConfig(); print(c.roi_x1, c.roi_y1, c.roi_x2, c.roi_y2, c.use_roi_crop)"`
Expected: `0.03 0.23 0.98 0.94 True`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/config.py
git commit -m "feat(hirescam): add ROI crop coordinates to HiResCAMConfig"
```

---

## Task 3: Wire ROI Crop into Inference Pipeline

**Files:**
- Modify: `backend/app/services/inference/orchestrate.py:106-151`

- [ ] **Step 1: Update `_run_one()` to crop before inference**

Replace `_run_one` function (lines 106-151):

```python
def _run_one(
    session: Session,
    *,
    study_id: int,
    model: ModelMetadata,
    model_dir: Path,
    image_path: Path,
) -> None:
    from app.services.hirescam.config import HiResCAMConfig
    from app.services.hirescam.ecg_crop import crop_ecg_roi

    row = session.scalar(
        select(AIAnalysis).where(
            AIAnalysis.ecg_study_id == study_id,
            AIAnalysis.model_metadata_id == model.id,
        )
    )
    is_new = row is None
    if row is None:
        row = AIAnalysis(
            ecg_study_id=study_id,
            model_metadata_id=model.id,
            status="failed",
        )

    crop_path = None
    try:
        config = HiResCAMConfig()
        if config.use_roi_crop:
            crop_path, _ = crop_ecg_roi(
                str(image_path),
                roi_x1=config.roi_x1,
                roi_y1=config.roi_y1,
                roi_x2=config.roi_x2,
                roi_y2=config.roi_y2,
            )
            inference_path = str(crop_path)
        else:
            inference_path = str(image_path)

        resolved = str(Path(model_dir) / model.model_file_path)
        loaded = load_model(resolved)
        started = datetime.now(UTC)
        out = run_inference(loaded, inference_path, device="cpu")
        finished = datetime.now(UTC)
        row.predicted_class = out["predicted_class"]
        row.confidence_score = out["confidence"]
        row.probability_json = out["probabilities"]
        row.inference_time_ms = int(out["inference_ms"])
        row.device_used = "cpu"
        row.status = "success"
        row.error_message = None
        row.inference_started_at = started
        row.inference_finished_at = finished
    except Exception as exc:  # noqa: BLE001 - isolate per-model failure
        row.status = "failed"
        row.error_message = str(exc)[:500]
        row.device_used = "cpu"
    finally:
        if crop_path is not None:
            crop_path.unlink(missing_ok=True)

    if is_new:
        session.add(row)
```

- [ ] **Step 2: Verify no syntax errors**

Run: `python -c "from app.services.inference.orchestrate import analyze_study; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/inference/orchestrate.py
git commit -m "feat(inference): crop ECO ROI before YOLO predict"
```

---

## Task 4: Wire ROI Crop into HiResCAM Pipeline

**Files:**
- Modify: `backend/app/services/hirescam/orchestrate.py:23-145`

- [ ] **Step 1: Update `generate_artifacts()` to crop before HiResCAM and paste back**

Replace `generate_artifacts` function (lines 23-145):

```python
def generate_artifacts(
    session: Session,
    *,
    analysis: AIAnalysis,
    storage_root: Path,
    model_dir: Path,
    config: HiResCAMConfig | None = None,
) -> HiResCAMArtifact | None:
    """Generate HiResCAM artifacts for a single successful AIAnalysis row."""
    if analysis.status != "success" or analysis.predicted_class is None:
        return None

    existing = session.scalar(
        select(HiResCAMArtifact).where(HiResCAMArtifact.ai_analysis_id == analysis.id)
    )
    if existing is not None:
        return existing

    if config is None:
        config = get_config(session)

    study = session.get(ECGStudy, analysis.ecg_study_id)
    if study is None:
        return None

    model = session.get(ModelMetadata, analysis.model_metadata_id)
    if model is None:
        return None

    image_path = Path(storage_root) / study.image_original_path
    if not image_path.exists():
        return None

    crop_path = None
    try:
        from app.services.hirescam.ecg_crop import crop_ecg_roi, paste_overlay_to_full

        model_path = Path(model_dir) / model.model_file_path
        yolo_model = load_model(str(model_path))

        class_idx = _class_to_index(analysis.predicted_class)

        # Crop ROI if enabled
        if config.use_roi_crop:
            crop_path, roi_bbox = crop_ecg_roi(
                str(image_path),
                roi_x1=config.roi_x1,
                roi_y1=config.roi_y1,
                roi_x2=config.roi_x2,
                roi_y2=config.roi_y2,
            )
            cam_source = str(crop_path)
        else:
            cam_source = str(image_path)
            roi_bbox = None

        heatmap_arr, lb_params, _ = generate_hirescam_v2(
            yolo_model, cam_source, class_idx,
            target_layer_name=config.target_layer_name,
            input_size=config.input_size,
            device=config.device,
        )

        processed = postprocess_heatmap(
            heatmap_arr,
            lb_params,
            clip_percentile=config.clip_percentile,
            smooth_sigma=config.smooth_sigma,
            top_percent=config.top_percent,
            colormap=config.colormap,
        )

        # Apply signal mask to focus heatmap on ECG signals
        if config.use_signal_mask:
            from app.services.hirescam.signal_mask import create_signal_mask

            rgb_img = np.array(Image.open(cam_source).convert("RGB"))
            sig_mask = create_signal_mask(
                rgb_img,
                blur_radius=config.signal_mask_blur_radius,
            )
            norm_heatmap = processed["heatmap_norm"]
            masked = (
                (1.0 - config.signal_mask_strength) * norm_heatmap
                + config.signal_mask_strength * (norm_heatmap * sig_mask)
            )
            m_min, m_max = masked.min(), masked.max()
            if m_max - m_min > 1e-8:
                masked = (masked - m_min) / (m_max - m_min)
            else:
                masked = np.zeros_like(masked)
            processed["heatmap_norm"] = masked

        heatmap_png = array_to_png(processed["heatmap_norm"], colormap=config.colormap)

        # Generate overlay on crop
        overlay_png = compose_overlay(cam_source, heatmap_png, alpha=config.overlay_alpha)

        # Paste overlay back to full report if ROI crop is enabled
        if config.use_roi_crop and roi_bbox is not None:
            full_overlay_png = paste_overlay_to_full(
                str(image_path),
                overlay_png,
                roi_bbox,
            )
            # Also compose side-by-side on full report
            side_by_side_png = compose_side_by_side(
                str(image_path), heatmap_png, full_overlay_png,
            )
        else:
            full_overlay_png = overlay_png
            side_by_side_png = compose_side_by_side(
                str(image_path), heatmap_png, overlay_png,
            )

        status, focus_metric = evaluate_explanation(
            heatmap_arr,
            confidence=analysis.confidence_score,
            rgb_image=rgb_img if config.use_signal_mask else None,
        )

        heatmap_dir = storage_root / "heatmaps" / str(analysis.id)
        heatmap_dir.mkdir(parents=True, exist_ok=True)

        heatmap_path = heatmap_dir / "heatmap.png"
        overlay_path = heatmap_dir / "overlay.png"
        side_by_side_path = heatmap_dir / "side_by_side.png"

        heatmap_path.write_bytes(heatmap_png)
        overlay_path.write_bytes(full_overlay_png)
        side_by_side_path.write_bytes(side_by_side_png)

        artifact = HiResCAMArtifact(
            ai_analysis_id=analysis.id,
            heatmap_path=str(heatmap_path.relative_to(heatmap_dir.parent)),
            overlay_path=str(overlay_path.relative_to(heatmap_dir.parent)),
            side_by_side_path=str(side_by_side_path.relative_to(heatmap_dir.parent)),
            explanation_status=status,
            focus_metric=focus_metric,
            colormap_used=config.colormap,
        )
        session.add(artifact)
        return artifact

    except Exception:
        return None
    finally:
        if crop_path is not None:
            crop_path.unlink(missing_ok=True)
```

- [ ] **Step 2: Verify no syntax errors**

Run: `python -c "from app.services.hirescam.orchestrate import generate_artifacts; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/hirescam/orestrate.py
git commit -m "feat(hirescam): wire ROI crop into HiResCAM pipeline with paste-back"
```

---

## Task 5: Test End-to-End with Real ECG Image

**Files:**
- None (manual verification)

- [ ] **Step 1: Start Flask backend**

Run: `cd backend && .venv\Scripts\python.exe -m flask run --port 5000`
Expected: Server starts without errors.

- [ ] **Step 2: Run analysis on an encounter**

```bash
curl -X POST http://localhost:5000/api/ai/analyze \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model_ids": [1]}'
```

Expected: Response with `status: "success"`.

- [ ] **Step 3: Check HiResCAM artifact paths**

```bash
curl http://localhost:5000/api/ai/encounters/<id>/studies/<id> \
  -H "Authorization: Bearer <token>"
```

Expected: `overlay_path` and `side_by_side_path` present in response.

- [ ] **Step 4: View overlay image**

Open `http://localhost:5000/storage/heatmaps/<analysis_id>/overlay.png` in browser.

Expected: Full ECG report with heatmap overlay ONLY in the ECG signal region (not on header/footer/text).

- [ ] **Step 5: Compare with old overlay**

If old overlays exist, compare side-by-side. New overlay should show:
- Header text clean (no heatmap)
- Footer text clean (no heatmap)
- Heatmap concentrated on ECG signal lines

- [ ] **Step 6: Commit verification**

```bash
git add -A
git commit -m "test(hirescam): verify ROI crop pipeline end-to-end"
```

---

## Task 6: Update Tuning UI for ROI Crop Toggle

**Files:**
- Modify: `frontend/src/features/hirescam_tuning/components/ConfigPanel.tsx`

- [ ] **Step 1: Add ROI crop toggle to config panel**

```tsx
// Add to ConfigPanel.tsx form fields
<div className="flex items-center gap-2">
  <input
    type="checkbox"
    id="use_roi_crop"
    checked={config.use_roi_crop}
    onChange={(e) => updateConfig({ use_roi_crop: e.target.checked })}
  />
  <label htmlFor="use_roi_crop">Use ROI Crop</label>
</div>
```

- [ ] **Step 2: Add ROI coordinate fields (shown when toggle is on)**

```tsx
{config.use_roi_crop && (
  <div className="grid grid-cols-2 gap-2">
    <label>
      X1
      <input type="number" step="0.01" value={config.roi_x1}
        onChange={(e) => updateConfig({ roi_x1: parseFloat(e.target.value) })} />
    </label>
    <label>
      Y1
      <input type="number" step="0.01" value={config.roi_y1}
        onChange={(e) => updateConfig({ roi_y1: parseFloat(e.target.value) })} />
    </label>
    <label>
      X2
      <input type="number" step="0.01" value={config.roi_x2}
        onChange={(e) => updateConfig({ roi_x2: parseFloat(e.target.value) })} />
    </label>
    <label>
      Y2
      <input type="number" step="0.01" value={config.roi_y2}
        onChange={(e) => updateConfig({ roi_y2: parseFloat(e.target.value) })} />
    </label>
  </div>
)}
```

- [ ] **Step 3: Verify UI renders**

Run: `cd frontend && npm run dev`
Expected: Config panel shows ROI crop toggle and coordinate fields.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/hirescam_tuning/components/ConfigPanel.tsx
git commit -m "feat(tuning): add ROI crop toggle and coordinate fields to config panel"
```

---

## Self-Review Checklist

- [ ] **Spec coverage:** All 6 tasks implement the ROI crop pipeline.
- [ ] **Placeholder scan:** No TBD/TODO/placeholder steps.
- [ ] **Type consistency:** All function signatures match across files.
- [ ] **Error handling:** Crop temp files cleaned up in `finally` blocks.
- [ ] **Backward compatibility:** `use_roi_crop=False` disables crop (original behavior).
