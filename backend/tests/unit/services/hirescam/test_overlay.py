"""Overlay composer tests."""
import os
import tempfile

import numpy as np
from PIL import Image

from app.services.hirescam.colormap import array_to_png
from app.services.hirescam.overlay import (
    clean_cam,
    compose_overlay,
    compose_side_by_side,
    make_transparent_cam_overlay,
    paste_roi_overlay_to_full,
)


def _create_test_image(path: str, size: tuple[int, int] = (224, 224)) -> None:
    """Create a small test PNG image."""
    arr = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def test_compose_overlay_returns_png_bytes():
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        _create_test_image(path)
        heatmap = array_to_png(np.random.rand(64, 64).astype(np.float32))
        result = compose_overlay(path, heatmap)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"
    finally:
        os.unlink(path)


def test_compose_side_by_side_returns_png_bytes():
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        _create_test_image(path)
        heatmap = array_to_png(np.random.rand(64, 64).astype(np.float32))
        overlay = array_to_png(np.random.rand(64, 64).astype(np.float32))
        result = compose_side_by_side(path, heatmap, overlay)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"
    finally:
        os.unlink(path)


def test_clean_cam_discards_low_activation():
    crop_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    crop_img = Image.fromarray(crop_arr, mode="RGB")
    cam = np.random.rand(10, 10).astype(np.float32)
    # Set at least one value to 1.0 to ensure max works
    cam[0, 0] = 1.0
    cleaned = clean_cam(cam, crop_img, threshold=0.5, use_signal_mask=False)
    assert cleaned.shape == (10, 10)
    assert np.all(cleaned[cam < 0.5] == 0)


def test_make_transparent_cam_overlay_returns_png_bytes():
    crop_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    crop_img = Image.fromarray(crop_arr, mode="RGB")
    cam = np.random.rand(100, 100).astype(np.float32)
    result = make_transparent_cam_overlay(crop_img, cam, max_alpha=0.6)
    assert isinstance(result, bytes)
    assert result[:4] == b"\x89PNG"


def test_paste_roi_overlay_to_full_returns_png_bytes():
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        _create_test_image(path, size=(200, 200))
        crop_arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        crop_img = Image.fromarray(crop_arr, mode="RGB")
        cam = np.random.rand(100, 100).astype(np.float32)
        crop_overlay = make_transparent_cam_overlay(crop_img, cam, max_alpha=0.6)
        
        result = paste_roi_overlay_to_full(path, crop_overlay, (20, 20, 180, 180))
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"
    finally:
        os.unlink(path)

