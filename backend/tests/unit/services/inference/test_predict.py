from app.services.inference.predict import run_inference


class _Probs:
    def __init__(self, data, top1):
        self.data = type("T", (), {"tolist": lambda self: data})()
        self.top1 = top1
        self.top1conf = data[top1]


class _Res:
    def __init__(self, data, top1):
        self.probs = _Probs(data, top1)


class _Model:
    def __init__(self, data, top1):
        self._r = _Res(data, top1)

    def predict(self, *a, **k):
        return [self._r]


def test_run_inference_maps_enum():
    # YOLO index order: 0 abnormal, 1 homi, 2 mi, 3 normal
    m = _Model([0.1, 0.15, 0.7, 0.05], top1=2)
    out = run_inference(m, "x.jpg", device="cpu")
    assert out["predicted_class"] == "mi"
    assert round(out["confidence"], 2) == 0.7
    assert set(out["probabilities"]) == {"abnormal", "homi", "mi", "normal"}
    assert out["probabilities"]["normal"] == 0.05
    assert out["inference_ms"] >= 0
