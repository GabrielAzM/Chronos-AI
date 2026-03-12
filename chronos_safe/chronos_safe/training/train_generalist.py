"""Generalist training entrypoint."""

from __future__ import annotations

from pathlib import Path

from chronos_safe.training.trainer import TrainingConfig, train_model


def run_train_generalist(
    dataset_dir: str | Path,
    output_dir: str | Path,
    epochs: int = 20,
    batch_size: int = 16,
    learning_rate: float = 1.0e-3,
) -> dict[str, object]:
    return train_model(
        TrainingConfig(
            dataset_dir=Path(dataset_dir),
            output_dir=Path(output_dir),
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
        )
    )
