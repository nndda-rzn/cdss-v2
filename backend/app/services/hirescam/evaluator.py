"""Evaluate HiResCAM explanation quality using signal-region IoU."""
import numpy as np

# Fixed center region covers 70% of image center (ECG signal area)
CENTER_FRACTION = 0.70

# Thresholds for explanation status
THRESHOLD_GOOD = 0.60  # >60% of activation in signal region
THRESHOLD_DIFFUSE = 0.30  # 30-60% = diffuse


def evaluate_explanation(
    heatmap: np.ndarray,
    *,
    confidence: float | None = None,
    rgb_image: np.ndarray | None = None,
) -> tuple[str, float]:
    """Evaluate HiResCAM explanation quality.

    Args:
        heatmap: 2D numpy array [0..1] of the heatmap.
        confidence: Model confidence score (0..1), optional.
        rgb_image: Optional RGB image for signal-mask IoU evaluation.

    Returns:
        Tuple of (explanation_status, focus_metric).
    """
    if heatmap.ndim != 2:
        raise ValueError(f"Expected 2D heatmap, got {heatmap.ndim}D")

    if rgb_image is not None:
        focus_metric = compute_signal_mask_iou(heatmap, rgb_image)
    else:
        focus_metric = _compute_signal_region_iou(heatmap)

    # Determine status
    status = _classify_status(focus_metric, confidence)

    return status, float(focus_metric)


def compute_signal_mask_iou(
    heatmap: np.ndarray,
    rgb_image: np.ndarray,
    *,
    signal_threshold: int = 120,
    blur_radius: int = 5,
) -> float:
    """Compute fraction of heatmap activation overlapping with ECG signal regions.

    More accurate than center-crop for ECG images where signals may not
    be centered.
    """
    import cv2

    from app.services.hirescam.signal_mask import create_signal_mask

    mask = create_signal_mask(rgb_image, signal_threshold=signal_threshold, blur_radius=blur_radius)

    if mask.shape != heatmap.shape:
        mask = cv2.resize(
            mask, (heatmap.shape[1], heatmap.shape[0]), interpolation=cv2.INTER_LINEAR
        )

    total = float(heatmap.sum())
    if total == 0:
        return 0.0

    masked_activation = float((heatmap * mask).sum())
    return masked_activation / total


def _compute_signal_region_iou(heatmap: np.ndarray) -> float:
    """Compute fraction of heatmap activation in the center signal region.

    Uses a fixed center crop (70% of image) as approximation of ECG signal area.
    Returns ratio: activation_in_center / total_activation.
    """
    h, w = heatmap.shape
    # Center crop boundaries
    crop_h = int(h * CENTER_FRACTION)
    crop_w = int(w * CENTER_FRACTION)
    start_h = (h - crop_h) // 2
    start_w = (w - crop_w) // 2

    center_region = heatmap[start_h : start_h + crop_h, start_w : start_w + crop_w]
    total_activation = float(heatmap.sum())
    center_activation = float(center_region.sum())

    if total_activation == 0:
        return 0.0

    return center_activation / total_activation


def _classify_status(
    focus_metric: float,
    confidence: float | None,
) -> str:
    """Classify explanation status based on focus metric and confidence."""
    # Low confidence override
    if confidence is not None and confidence < 0.40:
        return "low-confidence"

    if focus_metric >= THRESHOLD_GOOD:
        return "good"
    elif focus_metric >= THRESHOLD_DIFFUSE:
        return "diffuse"
    else:
        return "off-target"
