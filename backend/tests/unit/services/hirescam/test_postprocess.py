import numpy as np

from app.services.hirescam.letterbox import LetterboxParams
from app.services.hirescam.postprocess import postprocess_heatmap


def _fake_params(orig_h=100, orig_w=200, target_size=416):
    return LetterboxParams(
        ratio=target_size / max(orig_w, orig_h),
        pad_top=0, pad_bottom=0, pad_left=0, pad_right=0,
        orig_h=orig_h, orig_w=orig_w, target_size=target_size,
    )


class TestPostprocessHeatmap:
    def test_output_keys(self):
        hm = np.random.rand(416, 416).astype(np.float32)
        params = _fake_params()
        result = postprocess_heatmap(hm, params)
        assert "heatmap_raw" in result
        assert "heatmap_norm" in result
        assert "heatmap_colored" in result
        assert "mask_top_area" in result

    def test_output_matches_original_dims(self):
        hm = np.random.rand(416, 416).astype(np.float32)
        params = _fake_params(orig_h=150, orig_w=300)
        result = postprocess_heatmap(hm, params)
        assert result["heatmap_norm"].shape == (150, 300)
        assert result["heatmap_colored"].shape == (150, 300, 3)

    def test_clip_percentile(self):
        hm = np.random.rand(64, 64).astype(np.float32)
        hm[0, 0] = 100.0  # outlier
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        result = postprocess_heatmap(hm, params, clip_percentile=99.0)
        assert result["heatmap_norm"].max() <= 1.0

    def test_top_percent_mask(self):
        hm = np.random.rand(64, 64).astype(np.float32) * 0.1
        hm[30:34, 30:34] = 1.0  # small hot spot
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        result = postprocess_heatmap(
            hm, params, top_percent=5.0, smooth_sigma=0, clip_percentile=100
        )
        mask = result["mask_top_area"]
        assert mask.sum() > 0
        assert mask.sum() / mask.size <= 0.20

    def test_smooth_sigma_zero_no_blur(self):
        hm = np.zeros((64, 64), dtype=np.float32)
        hm[32, 32] = 1.0
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        result = postprocess_heatmap(hm, params, smooth_sigma=0)
        assert result["heatmap_norm"].max() == result["heatmap_norm"][32, 32]

    def test_different_colormaps(self):
        hm = np.random.rand(64, 64).astype(np.float32)
        params = _fake_params(orig_h=64, orig_w=64, target_size=64)
        r1 = postprocess_heatmap(hm, params, colormap="turbo")
        r2 = postprocess_heatmap(hm, params, colormap="inferno")
        assert not np.array_equal(r1["heatmap_colored"], r2["heatmap_colored"])
