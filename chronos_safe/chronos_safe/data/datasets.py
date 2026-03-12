"""Dataset loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from chronos_safe.data.cache import load_manifest, load_npz_bundle
from chronos_safe.data.scalers import PhysicalScaler

try:
    import torch
    from torch.utils.data import Dataset
except ImportError:  # pragma: no cover - optional dependency
    torch = None

    class Dataset:  # type: ignore[override]
        """Fallback protocol-like dataset."""

        pass


@dataclass(slots=True)
class DatasetBundle:
    arrays: dict[str, np.ndarray]
    manifest: dict[str, Any]
    scaler: PhysicalScaler | None = None

    @classmethod
    def load(cls, dataset_root: str | Path) -> "DatasetBundle":
        dataset_root = Path(dataset_root)
        arrays = load_npz_bundle(dataset_root / "dataset.npz")
        manifest = load_manifest(dataset_root / "manifest.json")
        scaler_path = dataset_root / "scaler.json"
        scaler = PhysicalScaler.load(str(scaler_path)) if scaler_path.exists() else None
        return cls(arrays=arrays, manifest=manifest, scaler=scaler)


class ChronosDataset(Dataset):
    def __init__(self, dataset_root: str | Path, use_scaled: bool = True) -> None:
        bundle = DatasetBundle.load(dataset_root)
        self.arrays = bundle.arrays
        self.manifest = bundle.manifest
        self.scaler = bundle.scaler
        if use_scaled and self.scaler is not None:
            self.arrays = self.scaler.transform_batch(self.arrays)
        self.length = int(self.arrays["masses"].shape[0])

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, index: int) -> dict[str, Any]:
        item = {key: value[index] for key, value in self.arrays.items()}
        if torch is None:
            return item
        return {
            key: torch.as_tensor(value, dtype=torch.float32 if value.dtype != np.bool_ else torch.bool)
            for key, value in item.items()
        }
