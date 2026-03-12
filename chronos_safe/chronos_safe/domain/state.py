"""Domain state objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

from chronos_safe.domain.types import ArrayF64, JsonDict


def _as_float_array(value: Iterable[float] | np.ndarray, shape: tuple[int, ...] | None = None) -> ArrayF64:
    array = np.asarray(value, dtype=np.float64)
    if shape is not None and array.shape != shape:
        raise ValueError(f"Expected shape {shape}, received {array.shape}.")
    return array


@dataclass(slots=True)
class BodyState:
    body_id: str
    mass: float
    position: ArrayF64
    velocity: ArrayF64

    def __post_init__(self) -> None:
        self.position = _as_float_array(self.position, (3,))
        self.velocity = _as_float_array(self.velocity, (3,))
        self.mass = float(self.mass)


@dataclass(slots=True)
class SystemState:
    ids: list[str]
    masses: ArrayF64
    positions: ArrayF64
    velocities: ArrayF64
    metadata: JsonDict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.masses = _as_float_array(self.masses)
        self.positions = _as_float_array(self.positions)
        self.velocities = _as_float_array(self.velocities)
        n = len(self.ids)
        if self.masses.shape != (n,):
            raise ValueError(f"Expected masses shape ({n},), received {self.masses.shape}.")
        if self.positions.shape != (n, 3):
            raise ValueError(f"Expected positions shape ({n}, 3), received {self.positions.shape}.")
        if self.velocities.shape != (n, 3):
            raise ValueError(f"Expected velocities shape ({n}, 3), received {self.velocities.shape}.")

    @property
    def num_bodies(self) -> int:
        return len(self.ids)

    def copy(self) -> "SystemState":
        return SystemState(
            ids=list(self.ids),
            masses=self.masses.copy(),
            positions=self.positions.copy(),
            velocities=self.velocities.copy(),
            metadata=dict(self.metadata),
        )

    def body_index(self, body_id: str) -> int:
        return self.ids.index(body_id)

    def to_dict(self) -> JsonDict:
        return {
            "ids": list(self.ids),
            "masses": self.masses.tolist(),
            "positions": self.positions.tolist(),
            "velocities": self.velocities.tolist(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: JsonDict) -> "SystemState":
        return cls(
            ids=list(payload["ids"]),
            masses=np.asarray(payload["masses"], dtype=np.float64),
            positions=np.asarray(payload["positions"], dtype=np.float64),
            velocities=np.asarray(payload["velocities"], dtype=np.float64),
            metadata=dict(payload.get("metadata", {})),
        )

    @classmethod
    def from_bodies(cls, bodies: list[BodyState], metadata: JsonDict | None = None) -> "SystemState":
        ids = [body.body_id for body in bodies]
        masses = np.asarray([body.mass for body in bodies], dtype=np.float64)
        positions = np.stack([body.position for body in bodies], axis=0).astype(np.float64)
        velocities = np.stack([body.velocity for body in bodies], axis=0).astype(np.float64)
        return cls(ids=ids, masses=masses, positions=positions, velocities=velocities, metadata=metadata or {})
