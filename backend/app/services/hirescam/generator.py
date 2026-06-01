"""Generate HiResCAM heatmaps for YOLO classify models using hooks.

Based on Draelos & Carin (2021): element-wise multiply gradients and
activations, then sum over the feature dimension. This produces provably
faithful explanations for CNNs with a final FC layer after convolutions.
"""
from typing import Any

import cv2
import numpy as np
import torch


def generate_hirescam(
    model: Any,
    image_path: str,
    target_class_idx: int,
    *,
    device: str = "cpu",
) -> np.ndarray:
    """Generate HiResCAM heatmap for a YOLO classify model.

    Args:
        model: Loaded ultralytics YOLO model (classify mode).
        image_path: Path to the input ECG image.
        target_class_idx: Index of the predicted class (from model.probs.top1).
        device: "cpu" or "cuda".

    Returns:
        2D numpy array [0..1] of shape matching the input image.
    """
    target_layer = _find_target_layer(model)
    if target_layer is None:
        raise RuntimeError("No Conv2d layer found in YOLO model")

    # Run inference to get the model output
    results = model.predict(image_path, device=device, verbose=False)
    results[0]  # noqa: B018 — trigger result processing

    activations: dict[str, torch.Tensor] = {}
    gradients: dict[str, torch.Tensor] = {}

    def forward_hook(
        module: Any,
        input: Any,
        output: torch.Tensor,
    ) -> None:
        activations["target"] = output.detach()

    def backward_hook(
        module: Any,
        grad_input: Any,
        grad_output: tuple[torch.Tensor | None, ...],
    ) -> None:
        if grad_output[0] is not None:
            gradients["target"] = grad_output[0].detach()

    handle_fwd = target_layer.register_forward_hook(forward_hook)
    handle_bwd = target_layer.register_full_backward_hook(backward_hook)

    try:
        orig_img = cv2.imread(image_path)
        if orig_img is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
        img_tensor = _preprocess_for_model(model, orig_img, device)

        # Forward + backward
        model.model.train()  # Enable gradients
        output = model.model(img_tensor)

        # Get class score (not probs, the raw logits)
        if hasattr(output, "probs"):
            scores = output.probs.data
        else:
            scores = output[0] if isinstance(output, (list | tuple)) else output

        target_score = scores[0, target_class_idx]
        target_score.backward()

        # Compute HiResCAM: sum(grads * activs, axis=features)
        activs = activations["target"].cpu().numpy()  # [1, C, H, W]
        grads = gradients["target"].cpu().numpy()  # [1, C, H, W]

        # Element-wise multiply, then sum over feature dimension
        cams = np.multiply(grads, activs)  # [1, C, H, W]
        cams = np.sum(cams, axis=1)  # [1, H, W]
        cams = np.maximum(cams, 0)  # ReLU

        # Normalize to [0, 1]
        cam: np.ndarray = cams[0]
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max - cam_min > 0:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        # Upsample to original image size
        h, w = orig_img.shape[:2]
        cam_resized = cv2.resize(cam, (w, h), interpolation=cv2.INTER_LINEAR)

        return cam_resized

    finally:
        handle_fwd.remove()
        handle_bwd.remove()
        model.model.eval()


def _find_target_layer(model: Any) -> Any:
    """Auto-detect the last Conv2d layer in a YOLO classify model."""
    layers = list(model.model.modules())
    conv_layers = [m for m in layers if isinstance(m, torch.nn.Conv2d)]
    if not conv_layers:
        return None
    # Return the last Conv2d that has output channels > 4
    # (filters out tiny convs, keeps the meaningful feature layer)
    for conv in reversed(conv_layers):
        if conv.out_channels > 4:
            return conv
    return conv_layers[-1]


def _preprocess_for_model(
    model: Any,
    img: np.ndarray,
    device: str,
) -> torch.Tensor:
    """Preprocess image tensor for YOLO model with gradients enabled."""
    from PIL import Image
    from ultralytics.data.augment import classify_transforms

    # Use YOLO's internal transforms
    transforms = classify_transforms(model.args.imgsz)
    img_pil = Image.fromarray(img)

    tensor = transforms(img_pil)  # [C, H, W]
    tensor = tensor.unsqueeze(0)  # [1, C, H, W]
    tensor = tensor.to(device)
    tensor.requires_grad_(True)
    return tensor
