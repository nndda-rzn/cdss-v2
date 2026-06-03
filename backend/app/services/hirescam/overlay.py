"""Compose heatmap overlays and side-by-side comparison images."""
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ALPHA = 0.4  # Heatmap transparency on overlay


def compose_overlay(
    original_path: str, heatmap_png: bytes, *, alpha: float = ALPHA,
) -> bytes:
    """Blend heatmap over original ECG image.

    Args:
        original_path: Path to original ECG image.
        heatmap_png: PNG bytes of the heatmap (inferno colormap).

    Returns:
        PNG bytes of the overlaid image.
    """
    orig = Image.open(original_path).convert("RGB")
    heatmap = Image.open(io.BytesIO(heatmap_png)).convert("RGB")

    # Resize heatmap to match original
    heatmap = heatmap.resize(orig.size, Image.Resampling.LANCZOS)

    blended = Image.blend(orig, heatmap, alpha)
    return _image_to_png_bytes(blended)


def compose_side_by_side(
    original_path: str,
    heatmap_png: bytes,
    overlay_png: bytes,
) -> bytes:
    """Create side-by-side: original | heatmap | overlay.

    Args:
        original_path: Path to original ECG image.
        heatmap_png: PNG bytes of heatmap.
        overlay_png: PNG bytes of overlay.

    Returns:
        PNG bytes of the side-by-side image.
    """
    orig = Image.open(original_path).convert("RGB")
    heatmap = Image.open(io.BytesIO(heatmap_png)).convert("RGB")
    overlay = Image.open(io.BytesIO(overlay_png)).convert("RGB")

    # Resize all to same height
    target_h = orig.size[1]
    heatmap = heatmap.resize(
        (int(target_h * heatmap.size[0] / heatmap.size[1]), target_h),
        Image.Resampling.LANCZOS,
    )
    overlay = overlay.resize(orig.size, Image.Resampling.LANCZOS)

    # Concatenate horizontally
    total_w = orig.size[0] + heatmap.size[0] + overlay.size[0]
    result = Image.new("RGB", (total_w, target_h))
    result.paste(orig, (0, 0))
    result.paste(heatmap, (orig.size[0], 0))
    result.paste(overlay, (orig.size[0] + heatmap.size[0], 0))

    return _image_to_png_bytes(result)


def _image_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


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
            mask_img = mask_img.resize(
                (cam.shape[1], cam.shape[0]), Image.Resampling.BILINEAR
            )
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
        cam_img = cam_img.resize(
            (crop_rgb.shape[1], crop_rgb.shape[0]), Image.Resampling.BILINEAR
        )
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
