from unittest.mock import MagicMock

import pytest
import torch.nn as nn

from app.services.hirescam.generator_v2 import (
    find_conv_layers,
    select_target_layer,
)


class _FakeConv(nn.Module):
    def __init__(self, out_channels):
        super().__init__()
        self.conv = nn.Conv2d(3, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class _FakeModel:
    """Mimics ultralytics YOLO wrapper."""
    def __init__(self):
        self._conv1 = _FakeConv(16)
        self._conv2 = _FakeConv(32)
        self._conv3 = _FakeConv(64)
        self._model = nn.Sequential(self._conv1, self._conv2, self._conv3)
        self._model.f = lambda x: x
        self.args = {"imgsz": 224}

    @property
    def model(self):
        return self._model

    def predict(self, *a, **kw):
        return MagicMock()


class TestFindConvLayers:
    def test_returns_all_conv_layers(self):
        fake = _FakeModel()
        layers = find_conv_layers(fake)
        assert len(layers) == 3

    def test_filters_small_output(self):
        """Conv2d with out_channels <= 4 should be excluded."""
        model = MagicMock()
        small_conv = nn.Conv2d(3, 2, kernel_size=1)
        big_conv = nn.Conv2d(3, 64, kernel_size=1)
        model.model.modules.return_value = [small_conv, big_conv]
        layers = find_conv_layers(model)
        assert big_conv in layers
        assert small_conv not in layers

    def test_empty_model_raises(self):
        model = MagicMock()
        model.model.modules.return_value = []
        with pytest.raises(RuntimeError, match="No Conv2d"):
            find_conv_layers(model)


class TestSelectTargetLayer:
    def test_last_conv(self):
        convs = [MagicMock(name="c1"), MagicMock(name="c2"), MagicMock(name="c3")]
        result = select_target_layer(convs, "last_conv")
        assert result is convs[-1]

    def test_second_last_conv(self):
        convs = [MagicMock(name="c1"), MagicMock(name="c2"), MagicMock(name="c3")]
        result = select_target_layer(convs, "second_last_conv")
        assert result is convs[-2]

    def test_third_last_conv(self):
        convs = [MagicMock(name="c1"), MagicMock(name="c2"), MagicMock(name="c3")]
        result = select_target_layer(convs, "third_last_conv")
        assert result is convs[-3]

    def test_unknown_name_raises(self):
        convs = [MagicMock()]
        with pytest.raises(ValueError, match="Unknown target layer"):
            select_target_layer(convs, "nonexistent")

    def test_too_few_layers_raises(self):
        convs = [MagicMock(name="c1")]
        with pytest.raises(ValueError, match="cannot select"):
            select_target_layer(convs, "second_last_conv")
