"""Data loading, preprocessing and splitting for the cats-vs-dogs classifier."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from src.config import CLASS_NAMES, IMAGE_SIZE, NORM_MEAN, NORM_STD, SEED

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def preprocess_image(image: Image.Image, image_size: int = IMAGE_SIZE) -> torch.Tensor:
    """Convert a PIL image into a normalized CxHxW float tensor for the model.

    Used by both training and the inference API so the two paths cannot drift.
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"expected PIL.Image.Image, got {type(image).__name__}")

    pipeline = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]
    )
    return pipeline(image.convert("RGB"))


def build_train_transform(image_size: int = IMAGE_SIZE) -> transforms.Compose:
    """Training-time augmentation for better generalization."""
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]
    )


def build_eval_transform(image_size: int = IMAGE_SIZE) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]
    )


def discover_samples(
    root: Path, subset_per_class: int | None = None, seed: int = SEED
) -> list[tuple[Path, int]]:
    """Collect (path, label) pairs from `root/<class_name>/*` directories."""
    rng = random.Random(seed)
    samples: list[tuple[Path, int]] = []

    for label, class_name in enumerate(CLASS_NAMES):
        class_dir = root / class_name
        if not class_dir.is_dir():
            raise FileNotFoundError(f"missing class directory: {class_dir}")

        files = sorted(
            p for p in class_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        rng.shuffle(files)
        if subset_per_class is not None:
            files = files[:subset_per_class]
        samples.extend((p, label) for p in files)

    rng.shuffle(samples)
    return samples


def split_samples(
    samples: list[tuple[Path, int]],
    train_frac: float = 0.8,
    val_frac: float = 0.1,
) -> tuple[list[tuple[Path, int]], list[tuple[Path, int]], list[tuple[Path, int]]]:
    """Split into train/val/test. The test fraction is the remainder."""
    if not 0 < train_frac < 1 or not 0 <= val_frac < 1 or train_frac + val_frac >= 1:
        raise ValueError("fractions must be positive and leave a non-empty test split")

    n = len(samples)
    n_train = int(n * train_frac)
    n_val = int(n * val_frac)
    return samples[:n_train], samples[n_train : n_train + n_val], samples[n_train + n_val :]


class CatsDogsDataset(Dataset):
    def __init__(
        self, samples: list[tuple[Path, int]], transform: transforms.Compose | None = None
    ) -> None:
        self.samples = samples
        self.transform = transform or build_eval_transform()

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        path, label = self.samples[index]
        with Image.open(path) as img:
            tensor = self.transform(img.convert("RGB"))
        return tensor, label


def build_dataloaders(
    root: Path,
    batch_size: int = 32,
    subset_per_class: int | None = None,
    train_frac: float = 0.8,
    val_frac: float = 0.1,
    num_workers: int = 0,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    samples = discover_samples(root, subset_per_class=subset_per_class)
    train_s, val_s, test_s = split_samples(samples, train_frac, val_frac)

    train_ds = CatsDogsDataset(train_s, build_train_transform())
    val_ds = CatsDogsDataset(val_s, build_eval_transform())
    test_ds = CatsDogsDataset(test_s, build_eval_transform())

    common = {"batch_size": batch_size, "num_workers": num_workers}
    return (
        DataLoader(train_ds, shuffle=True, **common),
        DataLoader(val_ds, shuffle=False, **common),
        DataLoader(test_ds, shuffle=False, **common),
    )
