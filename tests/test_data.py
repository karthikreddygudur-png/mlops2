"""Unit tests for the data preprocessing pipeline."""

from __future__ import annotations

import pytest
import torch
from PIL import Image

from src.config import IMAGE_SIZE
from src.data import preprocess_image, split_samples


def make_image(size=(320, 240), mode="RGB") -> Image.Image:
    return Image.new(mode, size, color=(120, 90, 60) if mode == "RGB" else 120)


def test_preprocess_image_returns_expected_shape():
    tensor = preprocess_image(make_image())
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (3, IMAGE_SIZE, IMAGE_SIZE)
    assert tensor.dtype == torch.float32


def test_preprocess_image_converts_grayscale_to_three_channels():
    assert preprocess_image(make_image(mode="L")).shape[0] == 3


@pytest.mark.parametrize("size", [(64, 64), (1000, 300), (224, 224)])
def test_preprocess_image_normalizes_any_input_size(size):
    tensor = preprocess_image(make_image(size=size))
    assert tensor.shape == (3, IMAGE_SIZE, IMAGE_SIZE)
    # Normalized values leave the raw [0, 1] range.
    assert tensor.min() < 0.0 or tensor.max() > 1.0


def test_preprocess_image_rejects_non_image_input():
    with pytest.raises(TypeError):
        preprocess_image("not-an-image")


def test_split_samples_partitions_without_overlap():
    samples = [(f"img_{i}.jpg", i % 2) for i in range(100)]
    train, val, test = split_samples(samples, train_frac=0.8, val_frac=0.1)

    assert (len(train), len(val), len(test)) == (80, 10, 10)
    assert len(train) + len(val) + len(test) == len(samples)
    assert set(train).isdisjoint(val)
    assert set(train).isdisjoint(test)
    assert set(val).isdisjoint(test)


def test_split_samples_rejects_invalid_fractions():
    with pytest.raises(ValueError):
        split_samples([("a.jpg", 0)], train_frac=0.95, val_frac=0.1)
