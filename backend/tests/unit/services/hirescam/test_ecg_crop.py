"""ECG crop and paste utilities tests."""
import io
import os
import tempfile

import numpy as np
from PIL import Image

from app.services.hirescam.ecg_crop import crop_ecg_roi, paste_overlay_to_full


def _create_test_image(path: str, size: tuple[int, int] = (100, 100)) -> None:
    """Create a test PNG image."""
    arr = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def test_crop_ecg_roi():
    # Avoid NamedTemporaryFile open state lock on Windows
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    _create_test_image(path, size=(100, 100))
    
    crop_path = None
    try:
        crop_path, bbox = crop_ecg_roi(path, roi_x1=0.1, roi_y1=0.2, roi_x2=0.9, roi_y2=0.8)
        assert crop_path.exists()
        
        # Verify cropped dimensions: (0.9 - 0.1)*100 = 80, (0.8 - 0.2)*100 = 60
        with Image.open(crop_path) as cropped_img:
            assert cropped_img.size == (80, 60)
        assert bbox == (10, 20, 90, 80)
    finally:
        if crop_path is not None and os.path.exists(crop_path):
            os.unlink(crop_path)
        if os.path.exists(path):
            os.unlink(path)


def test_paste_overlay_to_full():
    fd1, path_full = tempfile.mkstemp(suffix=".png")
    os.close(fd1)
    fd2, path_overlay = tempfile.mkstemp(suffix=".png")
    os.close(fd2)
    
    _create_test_image(path_full, size=(100, 100))
    _create_test_image(path_overlay, size=(50, 50))
    
    try:
        roi_bbox = (10, 20, 90, 80)
        result = paste_overlay_to_full(path_full, path_overlay, roi_bbox)
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"
        
        # Verify the result can be opened and has original size
        with Image.open(io.BytesIO(result)) as img_result:
            assert img_result.size == (100, 100)
    finally:
        if os.path.exists(path_full):
            os.unlink(path_full)
        if os.path.exists(path_overlay):
            os.unlink(path_overlay)
