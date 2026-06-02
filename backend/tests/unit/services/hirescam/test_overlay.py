"""Overlay composer tests."""
import tempfile

import numpy as np
from PIL import Image

from app.services.hirescam.colormap import array_to_png
from app.services.hirescam.overlay import compose_overlay, compose_side_by_side


def _create_test_image(path: str, size: tuple[int, int] = (224, 224)) -> None:
    """Create a small test PNG image."""
    arr = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def test_compose_overlay_returns_png_bytes():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        _create_test_image(f.name)
        heatmap = array_to_png(np.random.rand(64, 64).astype(np.float32))
        result = compose_overlay(f.name, heatmap)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"


def test_compose_side_by_side_returns_png_bytes():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        _create_test_image(f.name)
        heatmap = array_to_png(np.random.rand(64, 64).astype(np.float32))
        overlay = array_to_png(np.random.rand(64, 64).astype(np.float32))
        result = compose_side_by_side(f.name, heatmap, overlay)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"
