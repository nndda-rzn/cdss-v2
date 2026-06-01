"""Colormap service tests."""
import numpy as np
import pytest

from app.services.hirescam.colormap import array_to_png


def test_array_to_png_returns_bytes():
    arr = np.random.rand(64, 64).astype(np.float32)
    result = array_to_png(arr)
    assert isinstance(result, bytes)
    assert result[:4] == b"\x89PNG"  # PNG magic


def test_array_to_png_zero_values():
    arr = np.zeros((32, 32), dtype=np.float32)
    result = array_to_png(arr)
    assert isinstance(result, bytes)


def test_array_to_png_one_values():
    arr = np.ones((32, 32), dtype=np.float32)
    result = array_to_png(arr)
    assert isinstance(result, bytes)


def test_array_to_png_1d_raises():
    arr = np.array([0.5, 0.3, 0.8], dtype=np.float32)
    with pytest.raises(ValueError, match="2D"):
        array_to_png(arr)
