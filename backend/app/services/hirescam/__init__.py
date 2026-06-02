"""HiResCAM explainability services."""
from app.services.hirescam.colormap import SUPPORTED_COLORMAPS, array_to_png
from app.services.hirescam.generator import generate_hirescam
from app.services.hirescam.generator_v2 import (
    find_conv_layers,
    generate_hirescam_v2,
    select_target_layer,
)
from app.services.hirescam.letterbox import LetterboxParams, letterbox, reverse_letterbox
from app.services.hirescam.postprocess import postprocess_heatmap

__all__ = [
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
]
