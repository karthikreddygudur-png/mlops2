"""Post-deployment model performance tracking (M5).

Replays a labelled batch against the live service and reports accuracy and latency.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import CLASS_NAMES, PROJECT_ROOT, RAW_DIR
from src.data import discover_samples

REPORT_PATH = PROJECT_ROOT / "reports" / "post_deploy_metrics.json"


def send_batch(base_url: str, samples: list[tuple[Path, int]]) -> list[dict]:
    results: list[dict] = []

    for path, label in samples:
        try:
            with open(path, "rb") as fh:
                response = requests.post(
                    f"{base_url}/predict",
                    files={"file": (path.name, fh, "image/jpeg")},
                    timeout=30,
                )
            response.raise_for_status()
            payload = response.json()
            results.append(
                {
                    "file": path.name,
                    "true_label": CLASS_NAMES[label],
                    "predicted_label": payload["label"],
                    "confidence": max(payload["probabilities"].values()),
                    "latency_ms": payload["latency_ms"],
                    "correct": payload["label"] == CLASS_NAMES[label],
                }
            )
        except (requests.RequestException, KeyError, ValueError) as exc:
            results.append({"file": path.name, "error": str(exc)})

    return results


def summarize(results: list[dict]) -> dict:
    scored = [r for r in results if "error" not in r]
    if not scored:
        return {"total": len(results), "scored": 0, "errors": len(results)}

    latencies = [r["latency_ms"] for r in scored]
    correct = sum(r["correct"] for r in scored)

    return {
        "total": len(results),
        "scored": len(scored),
        "errors": len(results) - len(scored),
        "accuracy": round(correct / len(scored), 4),
        "mean_latency_ms": round(statistics.mean(latencies), 2),
        "p95_latency_ms": round(
            sorted(latencies)[max(int(len(latencies) * 0.95) - 1, 0)], 2
        ),
        "mean_confidence": round(statistics.mean(r["confidence"] for r in scored), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay a labelled batch at the live API.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--data-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    try:
        samples = discover_samples(args.data_dir)[: args.limit]
    except FileNotFoundError as exc:
        print(f"[FAIL] {exc}")
        return 1

    if not samples:
        print(f"[FAIL] no images found under {args.data_dir}")
        return 1

    print(f"replaying {len(samples)} labelled images at {args.base_url}")
    results = send_batch(args.base_url.rstrip("/"), samples)
    summary = summarize(results)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2))
    print(f"report -> {REPORT_PATH}")
    return 0 if summary.get("scored") else 1


if __name__ == "__main__":
    sys.exit(main())
