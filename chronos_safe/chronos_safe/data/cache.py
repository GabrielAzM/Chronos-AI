"""NPZ and JSON cache helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from chronos_safe.utils.serialization import read_json, write_json


def save_npz_bundle(path: str | Path, arrays: dict[str, np.ndarray]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(target, **arrays)


def load_npz_bundle(path: str | Path) -> dict[str, np.ndarray]:
    with np.load(Path(path), allow_pickle=False) as payload:
        return {key: payload[key] for key in payload.files}


def save_manifest(path: str | Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def load_manifest(path: str | Path) -> dict[str, Any]:
    return read_json(path)
