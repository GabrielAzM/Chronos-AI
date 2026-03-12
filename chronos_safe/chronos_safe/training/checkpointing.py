"""Checkpoint helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chronos_safe.utils.serialization import write_json

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency
    torch = None


def save_model_checkpoint(
    path: str | Path,
    model: object,
    optimizer: object | None,
    epoch: int,
    metrics: dict[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if torch is None:  # pragma: no cover - exercised only without torch
        raise RuntimeError("PyTorch is required to save model checkpoints.")
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": None if optimizer is None else optimizer.state_dict(),
            "metrics": metrics,
        },
        target,
    )


def load_model_checkpoint(path: str | Path, model: object, optimizer: object | None = None) -> dict[str, Any]:
    if torch is None:  # pragma: no cover - exercised only without torch
        raise RuntimeError("PyTorch is required to load model checkpoints.")
    payload = torch.load(Path(path), map_location="cpu")
    model.load_state_dict(payload["model_state_dict"])
    if optimizer is not None and payload["optimizer_state_dict"] is not None:
        optimizer.load_state_dict(payload["optimizer_state_dict"])
    return payload


def save_training_manifest(path: str | Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)
