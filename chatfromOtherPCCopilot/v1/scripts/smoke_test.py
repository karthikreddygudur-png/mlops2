"""Post-deploy smoke test: verifies /health and one /predict call.

Exits non-zero so a CI/CD pipeline fails when the deployment is unhealthy.
"""

from __future__ import annotations

import argparse
import io
import sys
import time

import requests
from PIL import Image


def wait_for_health(base_url: str, timeout: float, interval: float = 2.0) -> dict:
    deadline = time.monotonic() + timeout
    last_error = "no attempt made"

    while time.monotonic() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(interval)

    raise TimeoutError(f"/health not ready within {timeout}s: {last_error}")


def sample_image_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (224, 224), color=(140, 110, 80)).save(buffer, format="JPEG")
    return buffer.getvalue()


def check_prediction(base_url: str) -> dict:
    response = requests.post(
        f"{base_url}/predict",
        files={"file": ("sample.jpg", sample_image_bytes(), "image/jpeg")},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    for key in ("label", "probabilities", "latency_ms"):
        if key not in payload:
            raise AssertionError(f"missing '{key}' in prediction response: {payload}")

    total = sum(payload["probabilities"].values())
    if abs(total - 1.0) > 1e-3:
        raise AssertionError(f"probabilities sum to {total}, expected 1.0")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the deployed service.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    try:
        health = wait_for_health(base_url, args.timeout)
        print(f"[PASS] /health -> {health}")

        if not health.get("model_loaded"):
            print("[FAIL] service is up but no model is loaded")
            return 1

        prediction = check_prediction(base_url)
        print(
            f"[PASS] /predict -> label={prediction['label']} "
            f"latency={prediction['latency_ms']}ms"
        )
    except Exception as exc:
        print(f"[FAIL] smoke test failed: {exc}")
        return 1

    print("[PASS] smoke test succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
