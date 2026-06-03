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

    gray = (rgb_image.astype(np.float32).mean(axis=2)).astype(np.uint8)
    mask = (gray < signal_threshold).astype(np.uint8) * 255

    if blur_radius > 0:
        mask_img = Image.fromarray(mask)
        mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        mask = np.asarray(mask_img)

    mask = mask.astype(np.float32) / 255.0
    max_val = mask.max()
    if max_val > 0:
        mask = mask / max_val

    return mask
