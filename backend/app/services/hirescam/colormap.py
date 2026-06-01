"""Render 2D numpy arrays to inferno-colormap PNGs (ADR-0013)."""
import io

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for headless servers
import matplotlib.cm as cm  # noqa: E402
import matplotlib.colors as mcolors  # noqa: E402
import numpy as np
from PIL import Image

_COLORMAP = cm.inferno  # type: ignore[attr-defined]
_NORMALIZER = mcolors.Normalize(vmin=0.0, vmax=1.0)


def array_to_png(
    arr: np.ndarray,
    *,
    colormap: str = "inferno",
) -> bytes:
    """Convert a 2D float array [0..1] to PNG bytes using inferno colormap.

    Args:
        arr: 2D numpy array, values in [0, 1].
        colormap: Colormap name (default "inferno").

    Returns:
        PNG image bytes.
    """
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D array, got {arr.ndim}D")

    rgb = _apply_colormap(arr)
    return _to_png_bytes(rgb)


def _apply_colormap(arr: np.ndarray) -> np.ndarray:
    """Apply inferno colormap to normalized 2D array, return uint8 RGB."""
    rgba: np.ndarray = _COLORMAP(_NORMALIZER(arr))  # (H, W, 4), values [0, 1]
    rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    return rgb


def _to_png_bytes(rgb: np.ndarray) -> bytes:
    """Convert uint8 RGB array to PNG bytes."""
    img = Image.fromarray(rgb, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
