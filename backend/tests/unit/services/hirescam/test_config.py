"""Unit tests for HiResCAMConfig dataclass."""
from app.services.hirescam.config import HiResCAMConfig


class TestHiResCAMConfig:
    def test_defaults(self):
        cfg = HiResCAMConfig()
        assert cfg.target_layer_name == "last_conv"
        assert cfg.input_size == 1600
        assert cfg.device == "cpu"
        assert cfg.clip_percentile == 99.0
        assert cfg.smooth_sigma == 1.0
        assert cfg.top_percent == 20.0
        assert cfg.colormap == "inferno"
        assert cfg.overlay_alpha == 0.45

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
        assert cfg.colormap == "inferno"

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
