"""FastAPI inference service for the cats-vs-dogs classifier."""

from __future__ import annotations

import io
import json
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from src.config import MODEL_PATH
from src.model import load_model, predict_image

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
MODEL_FILE = Path(os.getenv("MODEL_PATH", MODEL_PATH))

logging.basicConfig(
    level=logging.INFO, format="%(message)s", stream=sys.stdout, force=True
)
logger = logging.getLogger("catdog-api")

STATE: dict[str, object] = {"model": None, "class_names": None, "requests": 0}


class PredictionResponse(BaseModel):
    label: str
    probabilities: dict[str, float]
    latency_ms: float
    request_id: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    requests_served: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    if MODEL_FILE.exists():
        model, checkpoint = load_model(MODEL_FILE)
        STATE["model"] = model
        STATE["class_names"] = checkpoint["class_names"]
        logger.info(json.dumps({"event": "model_loaded", "path": str(MODEL_FILE)}))
    else:
        logger.warning(json.dumps({"event": "model_missing", "path": str(MODEL_FILE)}))
    yield
    STATE["model"] = None


app = FastAPI(
    title="Cats vs Dogs Classifier",
    description="MLOps Assignment 2 inference service",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured request logging. Records metadata only, never payload bytes."""
    request_id = str(uuid.uuid4())
    started = time.perf_counter()

    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000

    logger.info(
        json.dumps(
            {
                "event": "request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": round(elapsed_ms, 2),
            }
        )
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=STATE["model"] is not None,
        requests_served=int(STATE["requests"]),
    )


@app.post("/predict", response_model=PredictionResponse, tags=["inference"])
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    if STATE["model"] is None:
        raise HTTPException(status_code=503, detail="model is not loaded")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="uploaded file is empty")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="uploaded file is too large")

    try:
        image = Image.open(io.BytesIO(payload))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="file is not a readable image")

    started = time.perf_counter()
    label, probabilities = predict_image(
        STATE["model"], image, class_names=STATE["class_names"]
    )
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    request_id = str(uuid.uuid4())
    STATE["requests"] = int(STATE["requests"]) + 1

    logger.info(
        json.dumps(
            {
                "event": "prediction",
                "request_id": request_id,
                "label": label,
                "confidence": max(probabilities.values()),
                "image_size_bytes": len(payload),
                "latency_ms": latency_ms,
            }
        )
    )

    return PredictionResponse(
        label=label,
        probabilities=probabilities,
        latency_ms=latency_ms,
        request_id=request_id,
    )


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse(
        {"service": "cats-vs-dogs", "endpoints": ["/health", "/predict", "/metrics", "/docs"]}
    )
