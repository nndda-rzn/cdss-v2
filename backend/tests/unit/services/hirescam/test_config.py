"""Unit tests for HiResCAMConfig dataclass."""
from app.services.hirescam.config import HiResCAMConfig


class TestHiResCAMConfig:
    def test_defaults(self):
        cfg = HiResCAMConfig()
        assert cfg.target_layer_name == "last_conv"
        assert cfg.input_size == 640
        assert cfg.device == "cpu"
        assert cfg.clip_percentile == 98.0
        assert cfg.smooth_sigma == 0.0
        assert cfg.top_percent == 100.0
        assert cfg.colormap == "jet"
        assert cfg.overlay_alpha == 0.45
        assert cfg.use_signal_mask is True
        assert cfg.roi_x1 == 0.03
        assert cfg.roi_y1 == 0.18
        assert cfg.roi_x2 == 0.98
        assert cfg.roi_y2 == 0.96
        assert cfg.use_roi_crop is True
        assert cfg.cam_threshold == 0.40
        assert cfg.cam_gamma == 2.0
        assert cfg.max_alpha == 0.60

    def test_to_dict_round_trip(self):
        cfg = HiResCAMConfig(
            target_layer_name="third_last_conv",
            input_size=2048,
            smooth_sigma=2.5,
            colormap="turbo",
        )
        d = cfg.to_dict()
        restored = HiResCAMConfig.from_dict(d)
        assert restored == cfg

    def test_from_dict_ignores_unknown_keys(self):
        d = HiResCAMConfig().to_dict()
        d["unknown_key"] = "value"
        d["another"] = 42
        cfg = HiResCAMConfig.from_dict(d)
        assert cfg.colormap == "jet"

    def test_from_dict_empty(self):
        cfg = HiResCAMConfig.from_dict({})
        assert cfg == HiResCAMConfig()

    def test_custom_values(self):
        cfg = HiResCAMConfig(
            input_size=3000,
            clip_percentile=95.0,
            smooth_sigma=0.0,
            top_percent=30.0,
            colormap="jet",
            overlay_alpha=0.6,
        )
        d = cfg.to_dict()
        assert d["input_size"] == 3000
        assert d["colormap"] == "jet"
