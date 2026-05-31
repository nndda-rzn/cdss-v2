"""Compute an image-quality score and status from blur/brightness/contrast/noise."""
from typing import overload

import cv2
import numpy as np

_WEIGHTS = {"blur": 0.35, "contrast": 0.25, "brightness": 0.20, "noise": 0.20}


def _decode_gray(data: bytes) -> cv2.typing.MatLike:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Unable to decode image for quality assessment")
    return img


def _metrics(gray: cv2.typing.MatLike) -> dict[str, float]:
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    contrast = float(gray.std())
    smoothed = cv2.GaussianBlur(gray, (3, 3), 0)
    noise = float(np.abs(gray.astype(np.float64) - smoothed.astype(np.float64)).std())
    return {"blur": blur, "noise": noise,
            "brightness": brightness, "contrast": contrast}


def _score(metrics: dict[str, float]) -> tuple[float, str]:
    sub = {
        "blur": min(metrics["blur"] / 100.0, 1.0),
        "brightness": max(1.0 - abs(metrics["brightness"] - 130.0) / 130.0, 0.0),
        "contrast": min(metrics["contrast"] / 60.0, 1.0),
        "noise": max(1.0 - metrics["noise"] / 30.0, 0.0),
    }
    composite = sum(sub[k] * _WEIGHTS[k] for k in _WEIGHTS)
    composite = round(composite, 3)
    status = "good" if composite >= 0.7 else "acceptable" if composite >= 0.4 else "poor"
    return composite, status


@overload
def assess_quality(data: bytes) -> tuple[float, str]: ...
@overload
def assess_quality(
    data: bytes, *, detailed: bool
) -> tuple[float, str, dict[str, float]]: ...


def assess_quality(
    data: bytes, *, detailed: bool = False
) -> tuple[float, str] | tuple[float, str, dict[str, float]]:
    gray = _decode_gray(data)
    metrics = _metrics(gray)
    score, status = _score(metrics)
    if detailed:
        return score, status, metrics
    return score, status
