"""Training loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from chronos_safe.data.datasets import ChronosDataset, DatasetBundle
from chronos_safe.models.ood_guard import OODGuard
from chronos_safe.models.residual_gnn import ResidualGNN, ResidualGNNConfig
from chronos_safe.training.checkpointing import save_model_checkpoint, save_training_manifest
from chronos_safe.training.losses import composite_loss
from chronos_safe.utils.device import get_device
from chronos_safe.utils.seed import set_seed

try:
    import torch
    from torch.utils.data import DataLoader, random_split
except ImportError:  # pragma: no cover - optional dependency
    torch = None
    DataLoader = None
    random_split = None


@dataclass(slots=True)
class TrainingConfig:
    dataset_dir: Path
    output_dir: Path
    epochs: int = 20
    batch_size: int = 16
    learning_rate: float = 1.0e-3
    weight_decay: float = 1.0e-5
    validation_fraction: float = 0.2
    patience: int = 5
    device: str = "cpu"
    seed: int = 42
    initial_checkpoint: Path | None = None
    model: ResidualGNNConfig = field(default_factory=ResidualGNNConfig)


def _require_torch() -> None:
    if torch is None or DataLoader is None or random_split is None:  # pragma: no cover
        raise RuntimeError("PyTorch is required for training. Install the 'ml' extras.")


def _split_dataset(dataset: ChronosDataset, validation_fraction: float, seed: int):
    _require_torch()
    val_size = max(1, int(len(dataset) * validation_fraction))
    train_size = max(1, len(dataset) - val_size)
    if train_size + val_size > len(dataset):
        val_size = len(dataset) - train_size
    generator = torch.Generator().manual_seed(seed)
    return random_split(dataset, [train_size, val_size], generator=generator)


def _epoch(model, loader, optimizer, device: str, train: bool) -> float:
    losses = []
    if train:
        model.train()
    else:
        model.eval()
    for batch in loader:
        masses = batch["masses_scaled"].to(device)
        positions = batch["positions_scaled"].to(device)
        velocities = batch["velocities_scaled"].to(device)
        mask = batch["mask"].to(device)
        target = batch["target_delta_acc_scaled"].to(device)
        if train:
            optimizer.zero_grad()
        with torch.set_grad_enabled(train):
            prediction = model(masses, positions, velocities, mask)
            loss = composite_loss(prediction, target, mask)
            if train:
                loss.backward()
                optimizer.step()
        losses.append(float(loss.detach().cpu()))
    return float(np.mean(losses)) if losses else 0.0


def train_model(config: TrainingConfig) -> dict[str, object]:
    _require_torch()
    set_seed(config.seed)
    dataset = ChronosDataset(config.dataset_dir)
    train_dataset, val_dataset = _split_dataset(dataset, config.validation_fraction, config.seed)
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)

    device = get_device(config.device)
    model = ResidualGNN(config.model).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=2, factor=0.5)
    if config.initial_checkpoint is not None:
        payload = torch.load(config.initial_checkpoint, map_location=device)
        state_dict = payload["model_state_dict"] if "model_state_dict" in payload else payload
        model.load_state_dict(state_dict)

    config.output_dir.mkdir(parents=True, exist_ok=True)
    best_val = float("inf")
    best_epoch = -1
    patience_left = config.patience
    history: list[dict[str, float]] = []

    for epoch in range(1, config.epochs + 1):
        train_loss = _epoch(model, train_loader, optimizer, device, train=True)
        val_loss = _epoch(model, val_loader, optimizer, device, train=False)
        scheduler.step(val_loss)
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
        if val_loss < best_val:
            best_val = val_loss
            best_epoch = epoch
            patience_left = config.patience
            save_model_checkpoint(config.output_dir / "model.pt", model, optimizer, epoch, history[-1])
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    bundle = DatasetBundle.load(config.dataset_dir)
    ood_guard = OODGuard().fit(
        masses=bundle.arrays["masses"],
        positions=bundle.arrays["positions"],
        velocities=bundle.arrays["velocities"],
        mask=bundle.arrays["mask"],
    )
    ood_guard.save(str(config.output_dir / "ood_guard.json"))
    save_training_manifest(
        config.output_dir / "training_manifest.json",
        {
            "dataset_dir": str(config.dataset_dir),
            "output_dir": str(config.output_dir),
            "epochs_requested": config.epochs,
            "best_epoch": best_epoch,
            "best_val_loss": best_val,
            "history": history,
            "device": device,
            "initial_checkpoint": None if config.initial_checkpoint is None else str(config.initial_checkpoint),
        },
    )
    scaler_path = config.dataset_dir / "scaler.json"
    if scaler_path.exists():
        (config.output_dir / "scaler.json").write_text(scaler_path.read_text(encoding="utf-8"), encoding="utf-8")
    return {
        "best_epoch": best_epoch,
        "best_val_loss": best_val,
        "history": history,
        "dataset_dir": str(config.dataset_dir),
        "output_dir": str(config.output_dir),
        "checkpoint_path": str(config.output_dir / "model.pt"),
        "scaler_path": str(config.output_dir / "scaler.json"),
        "ood_guard_path": str(config.output_dir / "ood_guard.json"),
    }
