"""HiResCAM explainability services."""
from app.services.hirescam.colormap import SUPPORTED_COLORMAPS, array_to_png
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.config_store import get_config, save_config
from app.services.hirescam.generator import generate_hirescam
from app.services.hirescam.generator_v2 import (
    find_conv_layers,
    generate_hirescam_v2,
    select_target_layer,
)
from app.services.hirescam.letterbox import LetterboxParams, letterbox, reverse_letterbox
from app.services.hirescam.postprocess import postprocess_heatmap
from app.services.hirescam.signal_mask import create_signal_mask

__all__ = [
    "HiResCAMConfig",
    "get_config",
    "save_config",
    "LetterboxParams",
    "letterbox",
    "reverse_letterbox",
    "postprocess_heatmap",
    "generate_hirescam",
    "generate_hirescam_v2",
    "find_conv_layers",
    "select_target_layer",
    "array_to_png",
    "SUPPORTED_COLORMAPS",
    "create_signal_mask",
]
