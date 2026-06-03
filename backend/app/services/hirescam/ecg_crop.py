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
