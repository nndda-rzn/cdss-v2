"""Compose heatmap overlays and side-by-side comparison images."""
import io

from PIL import Image

ALPHA = 0.4  # Heatmap transparency on overlay


def compose_overlay(original_path: str, heatmap_png: bytes) -> bytes:
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

    blended = Image.blend(orig, heatmap, ALPHA)
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
