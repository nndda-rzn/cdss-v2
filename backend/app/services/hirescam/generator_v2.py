"""HiResCAM v2: multi-layer targeting + configurable input size with letterbox."""
from __future__ import annotations

from typing import Any

import cv2
import numpy as np
import torch

from app.services.hirescam.generator import _disable_inplace, _restore_inplace


def find_conv_layers(model: Any) -> list:
    """Return ALL Conv2d layers with out_channels > 4, ordered first to last.

    Args:
        model: Ultralytics YOLO model wrapper.

    Returns:
        List of Conv2d modules.

    Raises:
        RuntimeError: If no valid Conv2d layers found.
    """
    layers = list(model.model.modules())
    conv_layers = [
        m for m in layers
        if isinstance(m, torch.nn.Conv2d) and m.out_channels > 4
    ]
    if not conv_layers:
        raise RuntimeError("No Conv2d layer with out_channels > 4 found in model")
    return conv_layers


def select_target_layer(layers: list, name: str) -> Any:
    """Select a target layer by name.

    Args:
        layers: List of Conv2d layers from find_conv_layers().
        name: One of 'last_conv', 'second_last_conv', 'third_last_conv'.

    Returns:
        The selected Conv2d layer.

    Raises:
        ValueError: If name is unknown or layers list is too short.
    """
    index_map = {
        "last_conv": -1,
        "second_last_conv": -2,
        "third_last_conv": -3,
    }
    if name not in index_map:
        raise ValueError(
            f"Unknown target layer '{name}'. Choose from: {list(index_map.keys())}"
        )
    idx = index_map[name]
    if abs(idx) > len(layers):
        raise ValueError(
            f"Model has {len(layers)} conv layers, cannot select '{name}'"
        )
    return layers[idx]


def generate_hirescam_v2(
    model: Any,
    image_path: str,
    target_class_idx: int,
    *,
    target_layer_name: str = "last_conv",
    input_size: int = 1600,
    device: str = "cpu",
) -> tuple[np.ndarray, Any, dict]:
    """Generate HiResCAM heatmap with configurable input size and target layer.

    Uses custom letterbox preprocessing instead of YOLO's classify_transforms,
    enabling proper reverse mapping to prevent overlay shift.

    Args:
        model: Ultralytics YOLO model wrapper.
        image_path: Path to the input ECG image.
        target_class_idx: Index of the target class for gradient computation.
        target_layer_name: Which conv layer to hook (last_conv, second_last_conv, third_last_conv).
        input_size: Square input size for the model (e.g. 1600, 2048).
        device: 'cpu' or 'cuda'.

    Returns:
        (raw_heatmap, letterbox_params, metadata) where raw_heatmap is 2D [0..1] float32.
    """
    from app.services.hirescam.letterbox import letterbox as custom_letterbox
    from app.services.hirescam.letterbox import reverse_letterbox

    conv_layers = find_conv_layers(model)
    target_layer = select_target_layer(conv_layers, target_layer_name)

    # Warm-up predict (ensures model is loaded)
    model.predict(image_path, verbose=False)

    # Register hooks
    activations: dict[str, torch.Tensor] = {}
    gradients: dict[str, torch.Tensor] = {}

    def fwd_hook(module, inp, output):
        activations["target"] = output.detach()

    def bwd_hook(module, grad_in, grad_out):
        if grad_out[0] is not None:
            gradients["target"] = grad_out[0].detach()

    handle_fwd = target_layer.register_forward_hook(fwd_hook)
    handle_bwd = target_layer.register_full_backward_hook(bwd_hook)

    old_states = _disable_inplace(model.model)

    try:
        # Read + custom letterbox preprocess
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        padded, lb_params = custom_letterbox(img_rgb, target_size=input_size)

        # To tensor (ImageNet normalization)
        tensor = padded.astype(np.float32) / 255.0
        tensor = (tensor - np.array([0.485, 0.456, 0.406])) / np.array(
            [0.229, 0.224, 0.225]
        )
        tensor = tensor.transpose(2, 0, 1)  # CHW
        tensor = torch.from_numpy(tensor).unsqueeze(0).to(device)
        tensor.requires_grad_(True)

        # Forward
        model.model.train()
        output = model.model(tensor)

        # Extract logit for target class
        if hasattr(output, "probs") and output.probs is not None:
            target_score = output.probs.data[0, target_class_idx]
        else:
            logits = output if isinstance(output, torch.Tensor) else output[0]
            target_score = logits[0, target_class_idx]

        # Backward
        model.model.zero_grad()
        target_score.backward()

        # HiResCAM computation
        activs = activations["target"].cpu().numpy()[0]  # (C, H, W)
        grads = gradients["target"].cpu().numpy()[0]  # (C, H, W)

        cams = np.multiply(grads, activs)
        cam = np.sum(cams, axis=0)  # sum over channels
        cam = np.maximum(cam, 0)  # ReLU

        # Normalize
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max - cam_min > 1e-8:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        # Resize to letterbox size then reverse-map to original
        cam_resized = cv2.resize(
            cam, (input_size, input_size), interpolation=cv2.INTER_LINEAR
        )
        heatmap = reverse_letterbox(cam_resized, lb_params)

        # Metadata
        target_layer_info = str(target_layer)
        confidence = float(target_score.detach().cpu())

        metadata = {
            "image_path": image_path,
            "original_size": [lb_params.orig_h, lb_params.orig_w],
            "input_size": input_size,
            "target_layer": target_layer_name,
            "target_layer_info": target_layer_info,
            "target_class_id": target_class_idx,
            "confidence": confidence,
            "letterbox_ratio": lb_params.ratio,
            "letterbox_padding": {
                "top": lb_params.pad_top,
                "bottom": lb_params.pad_bottom,
                "left": lb_params.pad_left,
                "right": lb_params.pad_right,
            },
        }

        return heatmap, lb_params, metadata

    finally:
        handle_fwd.remove()
        handle_bwd.remove()
        _restore_inplace(old_states)
        model.model.eval()
