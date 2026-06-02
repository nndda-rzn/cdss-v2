"""Heatmap post-processing pipeline for HiResCAM tuning."""
from __future__ import annotations

import io

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from app.services.hirescam.colormap import array_to_png
from app.services.hirescam.letterbox import LetterboxParams, reverse_letterbox


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
