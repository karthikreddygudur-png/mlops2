"""Unit tests for model utilities and the inference path."""

from __future__ import annotations

import math

import torch
from PIL import Image

from src.config import CLASS_NAMES, IMAGE_SIZE
from src.model import SimpleCNN, load_model, predict_image, save_model


def make_image() -> Image.Image:
    return Image.new("RGB", (300, 200), color=(10, 200, 90))


def test_model_forward_returns_logits_per_class():
    model = SimpleCNN()
    logits = model(torch.randn(2, 3, IMAGE_SIZE, IMAGE_SIZE))
    assert logits.shape == (2, len(CLASS_NAMES))


def test_predict_image_returns_valid_label_and_probabilities():
    model = SimpleCNN().eval()
    label, probabilities = predict_image(model, make_image())

    assert label in CLASS_NAMES
    assert set(probabilities) == set(CLASS_NAMES)
    assert all(0.0 <= p <= 1.0 for p in probabilities.values())
    assert math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-4)


def test_predict_image_label_matches_highest_probability():
    model = SimpleCNN().eval()
    label, probabilities = predict_image(model, make_image())
    assert label == max(probabilities, key=probabilities.get)


def test_save_and_load_model_roundtrip(tmp_path):
    path = tmp_path / "model.pt"
    save_model(SimpleCNN().eval(), path, metadata={"test_accuracy": 0.9})

    assert path.exists()
    loaded, checkpoint = load_model(path)

    assert checkpoint["class_names"] == CLASS_NAMES
    assert checkpoint["image_size"] == IMAGE_SIZE
    assert checkpoint["metadata"]["test_accuracy"] == 0.9

    label, _ = predict_image(loaded, make_image())
    assert label in CLASS_NAMES


def test_loaded_model_is_deterministic(tmp_path):
    path = tmp_path / "model.pt"
    save_model(SimpleCNN().eval(), path)
    loaded, _ = load_model(path)

    image = make_image()
    first = predict_image(loaded, image)[1]
    second = predict_image(loaded, image)[1]
    assert first == second
