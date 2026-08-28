"""Central configuration loaded from params.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = PROJECT_ROOT / "params.yaml"


def load_params(path: Path | None = None) -> dict[str, Any]:
    with open(path or PARAMS_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


PARAMS = load_params()

SEED: int = PARAMS["seed"]
IMAGE_SIZE: int = PARAMS["image_size"]
CLASS_NAMES: list[str] = PARAMS["class_names"]

RAW_DIR = PROJECT_ROOT / PARAMS["data"]["raw_dir"]
PROCESSED_DIR = PROJECT_ROOT / PARAMS["data"]["processed_dir"]
MODEL_PATH = PROJECT_ROOT / PARAMS["train"]["model_out"]

# ImageNet statistics; standard for 3-channel 224x224 inputs.
NORM_MEAN = (0.485, 0.456, 0.406)
NORM_STD = (0.229, 0.224, 0.225)
