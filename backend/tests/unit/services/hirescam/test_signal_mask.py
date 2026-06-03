"""Tests for signal mask computation."""
import numpy as np

from app.services.hirescam.signal_mask import create_signal_mask


def test_returns_2d_float_array():
    rgb = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
    mask = create_signal_mask(rgb)
    assert mask.ndim == 2
    assert mask.shape == (100, 200)
    assert mask.dtype == np.float32


def test_mask_values_between_0_and_1():
    rgb = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
    mask = create_signal_mask(rgb)
    assert mask.min() >= 0.0
    assert mask.max() <= 1.0


def test_dark_pixels_have_high_mask_value():
    rgb = np.full((100, 200, 3), 255, dtype=np.uint8)
    rgb[40:60, 80:120] = 0
    mask = create_signal_mask(rgb)
    assert mask[50, 100] > mask[10, 10]


def test_custom_threshold():
    rgb = np.full((100, 200, 3), 100, dtype=np.uint8)
    mask_strict = create_signal_mask(rgb, signal_threshold=80)
    mask_loose = create_signal_mask(rgb, signal_threshold=120)
    assert mask_strict.sum() <= mask_loose.sum()


def test_blur_radius_effect():
    rgb = np.zeros((100, 200, 3), dtype=np.uint8)
    rgb[50, 100] = 255
    mask_sharp = create_signal_mask(rgb, blur_radius=0)
    mask_blur = create_signal_mask(rgb, blur_radius=10)
    assert mask_blur.sum() >= mask_sharp.sum()
