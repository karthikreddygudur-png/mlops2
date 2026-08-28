"""Train the baseline classifier and log the run to MLflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import torch
from sklearn.metrics import confusion_matrix
from torch import nn
from torch.utils.data import DataLoader

from src.config import CLASS_NAMES, MODEL_PATH, PARAMS, PROJECT_ROOT, RAW_DIR
from src.data import build_dataloaders, set_seed
from src.model import SimpleCNN, save_model

ARTIFACT_DIR = PROJECT_ROOT / "reports"


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer | None,
    device: str,
) -> tuple[float, float]:
    training = optimizer is not None
    model.train(training)

    total_loss, correct, seen = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            logits = model(images)
            loss = criterion(logits, labels)

            if optimizer is not None:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * labels.size(0)
            correct += int((logits.argmax(1) == labels).sum())
            seen += labels.size(0)

    return total_loss / max(seen, 1), correct / max(seen, 1)


@torch.inference_mode()
def collect_predictions(
    model: nn.Module, loader: DataLoader, device: str
) -> tuple[list[int], list[int]]:
    model.eval()
    y_true: list[int] = []
    y_pred: list[int] = []
    for images, labels in loader:
        preds = model(images.to(device)).argmax(1).cpu()
        y_true.extend(labels.tolist())
        y_pred.extend(preds.tolist())
    return y_true, y_pred


def plot_curves(history: dict[str, list[float]], path: Path) -> None:
    fig, (ax_loss, ax_acc) = plt.subplots(1, 2, figsize=(11, 4))
    epochs = range(1, len(history["train_loss"]) + 1)

    ax_loss.plot(epochs, history["train_loss"], marker="o", label="train")
    ax_loss.plot(epochs, history["val_loss"], marker="o", label="val")
    ax_loss.set(title="Loss", xlabel="epoch", ylabel="loss")
    ax_loss.legend()

    ax_acc.plot(epochs, history["train_acc"], marker="o", label="train")
    ax_acc.plot(epochs, history["val_acc"], marker="o", label="val")
    ax_acc.set(title="Accuracy", xlabel="epoch", ylabel="accuracy")
    ax_acc.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_confusion(y_true: list[int], y_pred: list[int], path: Path) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(CLASS_NAMES))))
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.imshow(cm, cmap="Blues")
    ax.set(
        title="Confusion matrix (test)",
        xlabel="predicted",
        ylabel="actual",
        xticks=range(len(CLASS_NAMES)),
        yticks=range(len(CLASS_NAMES)),
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
    )
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main() -> None:
    train_cfg = PARAMS["train"]
    data_cfg = PARAMS["data"]

    parser = argparse.ArgumentParser(description="Train the cats-vs-dogs baseline model.")
    parser.add_argument("--epochs", type=int, default=train_cfg["epochs"])
    parser.add_argument("--batch-size", type=int, default=train_cfg["batch_size"])
    parser.add_argument("--learning-rate", type=float, default=train_cfg["learning_rate"])
    parser.add_argument("--subset-per-class", type=int, default=data_cfg["subset_per_class"])
    parser.add_argument("--data-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--run-name", type=str, default="simple-cnn")
    args = parser.parse_args()

    set_seed()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_loader, val_loader, test_loader = build_dataloaders(
        root=args.data_dir,
        batch_size=args.batch_size,
        subset_per_class=args.subset_per_class,
        train_frac=data_cfg["splits"]["train"],
        val_frac=data_cfg["splits"]["val"],
        num_workers=train_cfg["num_workers"],
    )

    model = SimpleCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    mlflow.set_tracking_uri(PARAMS["mlflow"]["tracking_uri"])
    mlflow.set_experiment(PARAMS["mlflow"]["experiment_name"])

    with mlflow.start_run(run_name=args.run_name):
        mlflow.log_params(
            {
                "architecture": "SimpleCNN",
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "learning_rate": args.learning_rate,
                "subset_per_class": args.subset_per_class,
                "image_size": PARAMS["image_size"],
                "device": device,
                "train_samples": len(train_loader.dataset),
                "val_samples": len(val_loader.dataset),
                "test_samples": len(test_loader.dataset),
            }
        )

        history: dict[str, list[float]] = {
            "train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []
        }

        for epoch in range(1, args.epochs + 1):
            train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc = run_epoch(model, val_loader, criterion, None, device)

            history["train_loss"].append(train_loss)
            history["train_acc"].append(train_acc)
            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_acc)

            mlflow.log_metrics(
                {
                    "train_loss": train_loss,
                    "train_accuracy": train_acc,
                    "val_loss": val_loss,
                    "val_accuracy": val_acc,
                },
                step=epoch,
            )
            print(
                f"epoch {epoch}/{args.epochs} "
                f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
                f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}",
                flush=True,
            )

        test_loss, test_acc = run_epoch(model, test_loader, criterion, None, device)
        mlflow.log_metrics({"test_loss": test_loss, "test_accuracy": test_acc})
        print(f"test_loss={test_loss:.4f} test_acc={test_acc:.4f}", flush=True)

        curves_path = ARTIFACT_DIR / "training_curves.png"
        cm_path = ARTIFACT_DIR / "confusion_matrix.png"
        plot_curves(history, curves_path)
        y_true, y_pred = collect_predictions(model, test_loader, device)
        plot_confusion(y_true, y_pred, cm_path)

        metrics_path = ARTIFACT_DIR / "train_metrics.json"
        metrics_path.write_text(
            json.dumps(
                {"history": history, "test_loss": test_loss, "test_accuracy": test_acc},
                indent=2,
            ),
            encoding="utf-8",
        )

        save_model(
            model,
            MODEL_PATH,
            metadata={"test_accuracy": test_acc, "epochs": args.epochs},
        )

        for artifact in (curves_path, cm_path, metrics_path, MODEL_PATH):
            mlflow.log_artifact(str(artifact))

    print(f"saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
