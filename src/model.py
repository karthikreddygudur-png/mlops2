"""Baseline CNN and inference helpers."""

from __future__ import annotations

from pathlib import Path

import torch
from PIL import Image
from torch import nn

from src.config import CLASS_NAMES, IMAGE_SIZE
from src.data import preprocess_image


class SimpleCNN(nn.Module):
    """Four-block convolutional baseline for 224x224 RGB input."""

    def __init__(self, num_classes: int = len(CLASS_NAMES)) -> None:
        super().__init__()
        channels = [(3, 32), (32, 64), (64, 128), (128, 128)]
        blocks: list[nn.Module] = []
        for in_ch, out_ch in channels:
            blocks += [
                nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            ]
        self.features = nn.Sequential(*blocks)
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


def save_model(model: nn.Module, path: Path, metadata: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "class_names": CLASS_NAMES,
            "image_size": IMAGE_SIZE,
            "metadata": metadata or {},
        },
        path,
    )


def load_model(path: Path, device: str = "cpu") -> tuple[nn.Module, dict]:
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    model = SimpleCNN(num_classes=len(checkpoint["class_names"]))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval().to(device)
    return model, checkpoint


@torch.inference_mode()
def predict_image(
    model: nn.Module,
    image: Image.Image,
    class_names: list[str] | None = None,
    device: str = "cpu",
) -> tuple[str, dict[str, float]]:
    """Return the predicted label and per-class probabilities."""
    names = class_names or CLASS_NAMES
    batch = preprocess_image(image).unsqueeze(0).to(device)
    probs = torch.softmax(model(batch), dim=1).squeeze(0)
    probabilities = {name: round(float(probs[i]), 6) for i, name in enumerate(names)}
    return names[int(probs.argmax())], probabilities
