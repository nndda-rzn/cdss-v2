"""HiResCAM generator tests."""
from unittest.mock import MagicMock

import pytest
import torch

from app.services.hirescam.generator import (
    _find_target_layer,
    generate_hirescam,
)


def test_find_target_layer_returns_conv():
    """Verify _find_target_layer finds a Conv2d layer."""
    model = MagicMock()
    conv = torch.nn.Conv2d(64, 128, kernel_size=3)
    model.model.modules.return_value = [
        torch.nn.Linear(10, 10),
        torch.nn.ReLU(),
        conv,
        torch.nn.AdaptiveAvgPool2d(1),
    ]
    result = _find_target_layer(model)
    assert result is conv


def test_find_target_layer_no_conv_returns_none():
    model = MagicMock()
    model.model.modules.return_value = [
        torch.nn.Linear(10, 10),
        torch.nn.ReLU(),
    ]
    result = _find_target_layer(model)
    assert result is None


def test_find_target_layer_prefers_high_channel_conv():
    """When multiple Conv2d layers exist, prefer one with out_channels > 4."""
    model = MagicMock()
    tiny_conv = torch.nn.Conv2d(3, 2, kernel_size=1)
    big_conv = torch.nn.Conv2d(64, 128, kernel_size=3)
    model.model.modules.return_value = [
        big_conv,
        tiny_conv,
    ]
    result = _find_target_layer(model)
    # big_conv is last and has out_channels > 4, should be selected
    assert result is big_conv


def test_generate_hirescam_no_target_layer_raises():
    """If no Conv2d layer found, should raise RuntimeError."""
    mock_model = MagicMock()
    mock_model.model.modules.return_value = [torch.nn.Linear(10, 10)]

    with pytest.raises(RuntimeError, match="No Conv2d layer"):
        generate_hirescam(mock_model, "fake.jpg", 0)
