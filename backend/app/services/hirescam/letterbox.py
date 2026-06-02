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
    canvas[pad_top : pad_top + new_h, pad_left : pad_left + new_w] = resized

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
            params.pad_top : h - params.pad_bottom,
            params.pad_left : w - params.pad_right,
        ]
    elif heatmap.ndim == 3:
        h, w = heatmap.shape[:2]
        crop = heatmap[
            params.pad_top : h - params.pad_bottom,
            params.pad_left : w - params.pad_right,
        ]
    else:
        raise ValueError(f"Heatmap must be 2D or 3D, got {heatmap.ndim}D")

    return cv2.resize(crop, (params.orig_w, params.orig_h), interpolation=cv2.INTER_LINEAR)
