"""Uncertainty helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency
    torch = None


@dataclass(slots=True)
class UncertaintyEstimate:
    mean: np.ndarray
    std: np.ndarray


def monte_carlo_dropout_predict(
    model: object,
    batch: dict[str, object],
    num_samples: int = 8,
) -> UncertaintyEstimate:
    if torch is None:
        mean = np.zeros_like(batch["positions"])  # type: ignore[index]
        std = np.zeros_like(batch["positions"])  # type: ignore[index]
        return UncertaintyEstimate(mean=mean, std=std)

    model.train()
    outputs = []
    with torch.no_grad():
        for _ in range(num_samples):
            outputs.append(
                model(
                    batch["masses_scaled"],
                    batch["positions_scaled"],
                    batch["velocities_scaled"],
                    batch["mask"],
                ).detach().cpu()
            )
    stacked = torch.stack(outputs, dim=0)
    return UncertaintyEstimate(
        mean=stacked.mean(dim=0).numpy(),
        std=stacked.std(dim=0).numpy(),
    )
