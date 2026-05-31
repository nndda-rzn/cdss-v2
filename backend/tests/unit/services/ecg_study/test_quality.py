"""Image quality check tests (synthetic images)."""
import cv2
import numpy as np

from app.services.ecg_study.quality import assess_quality


def _encode(img: cv2.typing.MatLike) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


def test_sharp_image_scores_higher_than_blurry():
    # Sharp: random high-frequency noise -> high Laplacian variance.
    rng = np.random.default_rng(0)
    sharp = rng.integers(0, 256, (256, 256), dtype=np.uint8)
    sharp_score, _ = assess_quality(_encode(sharp))

    # Blurry: heavy Gaussian blur of the same image.
    blurry = cv2.GaussianBlur(sharp, (21, 21), 0)
    blurry_score, _ = assess_quality(_encode(blurry))

    assert sharp_score > blurry_score


def test_metrics_keys_present():
    img = np.full((128, 128), 130, dtype=np.uint8)
    score, status = assess_quality(_encode(img))
    assert 0.0 <= score <= 1.0
    assert status in ("good", "acceptable", "poor")


def test_returns_metrics_via_detailed():
    img = np.full((128, 128), 130, dtype=np.uint8)
    score, status, metrics = assess_quality(_encode(img), detailed=True)
    assert set(metrics) == {"blur", "noise", "brightness", "contrast"}
    assert all(isinstance(metrics[k], float) for k in metrics)
