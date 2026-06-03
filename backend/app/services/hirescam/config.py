"""HiResCAM runtime configuration dataclass."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class HiResCAMConfig:
    """Stores all tunable HiResCAM generation and post-processing parameters.

    Defaults match the original hardcoded values in orchestrate.py.
    """

    target_layer_name: str = "last_conv"
    input_size: int = 1600
    device: str = "cpu"
    clip_percentile: float = 99.0
    smooth_sigma: float = 1.0
    top_percent: float = 20.0
    colormap: str = "inferno"
    overlay_alpha: float = 0.45
    clip_percentile_low: float = 5.0
    use_signal_mask: bool = True
    signal_mask_strength: float = 0.65
    signal_mask_blur_radius: int = 5
    roi_x1: float = 0.03
    roi_y1: float = 0.23
    roi_x2: float = 0.98
    roi_y2: float = 0.94
    use_roi_crop: bool = True

    def to_dict(self) -> dict[str, object]:
        """Serialize to JSON-compatible dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> HiResCAMConfig:
        """Deserialize from dict, ignoring unknown keys."""
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid}
        return cls(**filtered)
