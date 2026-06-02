"""Apply colormaps to normalized heatmaps."""
from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib.colors import Normalize
from PIL import Image

SUPPORTED_COLORMAPS = ["inferno", "turbo", "jet", "viridis", "plasma"]

_COLORMAP_REGISTRY = {
    name: matplotlib.colormaps[name] for name in SUPPORTED_COLORMAPS
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
