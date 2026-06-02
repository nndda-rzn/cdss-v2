"""Explanation status evaluator tests."""
import numpy as np
import pytest

from app.services.hirescam.evaluator import evaluate_explanation


def test_good_status_high_focus():
    """Heatmap concentrated in center should be 'good'."""
    heatmap = np.zeros((100, 100), dtype=np.float32)
    heatmap[30:70, 30:70] = 1.0  # Center region
    status, metric = evaluate_explanation(heatmap, confidence=0.85)
    assert status == "good"
    assert metric >= 0.95  # Almost all activation in center


def test_diffuse_status_medium_focus():
    """Heatmap spread across image should be 'diffuse'."""
    heatmap = np.ones((100, 100), dtype=np.float32) * 0.5
    status, metric = evaluate_explanation(heatmap, confidence=0.70)
    assert status == "diffuse"


def test_off_target_status_low_focus():
    """Heatmap in corners should be 'off-target'."""
    heatmap = np.zeros((100, 100), dtype=np.float32)
    heatmap[0:15, 0:15] = 1.0  # Top-left corner
    heatmap[85:100, 85:100] = 1.0  # Bottom-right corner
    status, metric = evaluate_explanation(heatmap, confidence=0.75)
    assert status == "off-target"
    assert metric < 0.30


def test_low_confidence_override():
    """Low confidence should return 'low-confidence' regardless of focus."""
    heatmap = np.zeros((100, 100), dtype=np.float32)
    heatmap[30:70, 30:70] = 1.0
    status, _ = evaluate_explanation(heatmap, confidence=0.20)
    assert status == "low-confidence"


def test_zero_activation_returns_zero_metric():
    """Empty heatmap should return 0.0 metric."""
    heatmap = np.zeros((50, 50), dtype=np.float32)
    status, metric = evaluate_explanation(heatmap, confidence=0.80)
    assert metric == 0.0
    assert status == "off-target"


def test_1d_array_raises():
    with pytest.raises(ValueError, match="2D"):
        evaluate_explanation(np.array([0.5, 0.3]), confidence=0.80)


def test_no_confidence_returns_focus_based_status():
    """Without confidence, status is purely based on focus metric."""
    heatmap = np.zeros((100, 100), dtype=np.float32)
    heatmap[30:70, 30:70] = 1.0
    status, _ = evaluate_explanation(heatmap, confidence=None)
    assert status == "good"
