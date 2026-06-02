import numpy as np
import pytest

from app.services.hirescam.letterbox import LetterboxParams, letterbox, reverse_letterbox


class TestLetterboxParams:
    def test_dataclass_fields(self):
        p = LetterboxParams(
            ratio=0.714, pad_top=123, pad_bottom=123,
            pad_left=0, pad_right=0, orig_h=1572, orig_w=2213, target_size=1600
        )
        assert p.ratio == 0.714
        assert p.pad_top == 123
        assert p.orig_h == 1572


class TestLetterbox:
    def test_output_is_square(self):
        img = np.random.randint(0, 255, (1572, 2213, 3), dtype=np.uint8)
        out, params = letterbox(img, target_size=1600)
        assert out.shape == (1600, 1600, 3)

    def test_params_contain_orig_dims(self):
        img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        out, params = letterbox(img, target_size=416)
        assert params.orig_h == 100
        assert params.orig_w == 200
        assert params.target_size == 416
        assert out.shape == (416, 416, 3)

    def test_fill_color_applied(self):
        img = np.ones((50, 100, 3), dtype=np.uint8) * 128
        out, params = letterbox(img, target_size=200, fill_color=(0, 0, 0))
        assert out[0, 0, 0] == 0

    def test_grayscale_input_rejected(self):
        img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-channel"):
            letterbox(img, target_size=200)


class TestReverseLetterbox:
    def test_roundtrip_dimensions(self):
        orig = np.random.randint(0, 255, (1572, 2213, 3), dtype=np.uint8)
        padded, params = letterbox(orig, target_size=1600)
        recovered = reverse_letterbox(padded, params)
        assert recovered.shape == (1572, 2213, 3)

    def test_heatmap_roundtrip_2d(self):
        from PIL import Image
        orig = np.random.rand(1572, 2213).astype(np.float32)
        orig_pil = Image.fromarray((orig * 255).astype(np.uint8), mode="L")
        resized = orig_pil.resize((1600, 1600), Image.BILINEAR)
        arr = np.array(resized).astype(np.float32) / 255.0
        params = LetterboxParams(
            ratio=1600 / 2213, pad_top=0, pad_bottom=0,
            pad_left=0, pad_right=0, orig_h=1572, orig_w=2213, target_size=1600
        )
        recovered = reverse_letterbox(arr, params)
        assert recovered.shape == (1572, 2213)

    def test_crop_removes_padding(self):
        arr = np.ones((200, 200), dtype=np.float32)
        params = LetterboxParams(
            ratio=0.5, pad_top=50, pad_bottom=50,
            pad_left=50, pad_right=50, orig_h=100, orig_w=100, target_size=200
        )
        recovered = reverse_letterbox(arr, params)
        assert recovered.shape == (100, 100)
