"""Run a single YOLO classification inference and map to data-model enums."""
import time
from typing import Any

from app.services.inference.mapping import ENUM_ORDER


def run_inference(model: Any, image_path: str, *, device: str = "cpu") -> dict[str, Any]:
    t0 = time.perf_counter()
    res = model.predict(image_path, device=device, verbose=False)[0]
    elapsed = (time.perf_counter() - t0) * 1000
    probs_list = res.probs.data.tolist()
    top1 = int(res.probs.top1)
    probabilities = {ENUM_ORDER[i]: round(float(p), 4) for i, p in enumerate(probs_list)}
    return {
        "predicted_class": ENUM_ORDER[top1],
        "confidence": round(float(res.probs.top1conf), 4),
        "probabilities": probabilities,
        "inference_ms": round(elapsed, 1),
    }
