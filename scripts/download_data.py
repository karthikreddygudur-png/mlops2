"""Download and arrange the Cats vs Dogs dataset into data/raw/{cat,dog}/.

Primary source is the Kaggle dataset named in the assignment (needs a Kaggle API
token). Falls back to the Microsoft Dogs-vs-Cats archive, which needs no account.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

import requests

from src.config import RAW_DIR

MICROSOFT_URL = (
    "https://download.microsoft.com/download/3/E/1/"
    "3E1C3F21-ECDB-4869-8368-6DEBA77B919F/kagglecatsanddogs_5340.zip"
)
KAGGLE_DATASET = "bhavikjikadara/dog-and-cat-classification-dataset"


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"archive already present: {dest}")
        return dest

    print(f"downloading {url}")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in response.iter_content(chunk_size=1 << 20):
                fh.write(chunk)

    print(f"saved -> {dest} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def try_kaggle(target: Path) -> bool:
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except (ImportError, OSError):
        return False

    try:
        api = KaggleApi()
        api.authenticate()
        print(f"downloading Kaggle dataset {KAGGLE_DATASET}")
        api.dataset_download_files(KAGGLE_DATASET, path=str(target), unzip=True)
        return True
    except Exception as exc:
        print(f"kaggle download unavailable ({exc}); falling back")
        return False


def organize(extract_root: Path, out_dir: Path) -> dict[str, int]:
    """Move images into data/raw/cat and data/raw/dog, skipping corrupt files."""
    from PIL import Image

    aliases = {"cat": ("cat", "cats"), "dog": ("dog", "dogs")}
    counts: dict[str, int] = {}

    for class_name, names in aliases.items():
        source_dirs = [
            d for d in extract_root.rglob("*") if d.is_dir() and d.name.lower() in names
        ]
        if not source_dirs:
            raise FileNotFoundError(f"no source directory found for class '{class_name}'")

        dest = out_dir / class_name
        dest.mkdir(parents=True, exist_ok=True)
        kept = 0

        for source in source_dirs:
            for image_path in source.iterdir():
                if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                try:
                    with Image.open(image_path) as img:
                        img.verify()
                except Exception:
                    continue
                shutil.copy2(image_path, dest / image_path.name)
                kept += 1

        counts[class_name] = kept

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch the cats-vs-dogs dataset.")
    parser.add_argument("--out-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--work-dir", type=Path, default=Path("data/_download"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    if try_kaggle(args.work_dir):
        extract_root = args.work_dir
    else:
        archive = download(MICROSOFT_URL, args.work_dir / "catsdogs.zip")
        extract_root = args.work_dir / "extracted"
        if not extract_root.exists():
            print("extracting archive")
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(extract_root)

    counts = organize(extract_root, args.out_dir)
    print(f"dataset ready under {args.out_dir}: {counts}")
    print("next: dvc add data/raw && git add data/raw.dvc && git commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
