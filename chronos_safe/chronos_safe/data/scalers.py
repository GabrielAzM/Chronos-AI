"""Physical scaling utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chronos_safe.utils.serialization import read_json, write_json


def _safe_scale(value: float, minimum: float = 1.0e-8) -> float:
    return float(max(abs(value), minimum))


@dataclass(slots=True)
class PhysicalScaler:
    mass_scale: float = 1.0
    position_scale: float = 1.0
    velocity_scale: float = 1.0
    target_scale: float = 1.0

    def fit(
        self,
        masses: np.ndarray,
        positions: np.ndarray,
        velocities: np.ndarray,
        targets: np.ndarray,
        mask: np.ndarray,
    ) -> "PhysicalScaler":
        masses_active = masses[mask]
        positions_active = positions[np.repeat(mask[:, :, None], 3, axis=2)]
        velocities_active = velocities[np.repeat(mask[:, :, None], 3, axis=2)]
        targets_active = targets[np.repeat(mask[:, :, None], 3, axis=2)]
        self.mass_scale = _safe_scale(float(np.median(np.abs(masses_active))) if masses_active.size else 1.0)
        self.position_scale = _safe_scale(float(np.percentile(np.abs(positions_active), 90)) if positions_active.size else 1.0)
        self.velocity_scale = _safe_scale(float(np.percentile(np.abs(velocities_active), 90)) if velocities_active.size else 1.0)
        self.target_scale = _safe_scale(float(np.percentile(np.abs(targets_active), 90)) if targets_active.size else 1.0)
        return self

    def transform_batch(self, batch: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        return {
            **batch,
            "masses_scaled": batch["masses"] / self.mass_scale,
            "positions_scaled": batch["positions"] / self.position_scale,
            "velocities_scaled": batch["velocities"] / self.velocity_scale,
            "target_delta_acc_scaled": batch["target_delta_acc"] / self.target_scale,
        }

    def inverse_target(self, value: np.ndarray) -> np.ndarray:
        return value * self.target_scale

    def to_dict(self) -> dict[str, float]:
        return {
            "mass_scale": self.mass_scale,
            "position_scale": self.position_scale,
            "velocity_scale": self.velocity_scale,
            "target_scale": self.target_scale,
        }

    def save(self, path: str) -> None:
        write_json(path, self.to_dict())

    @classmethod
    def load(cls, path: str) -> "PhysicalScaler":
        payload = read_json(path)
        return cls(**payload)
