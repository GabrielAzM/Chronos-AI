"""Fast symplectic integrator."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chronos_safe.config.constants import DEFAULT_SOFTENING_AU, GRAVITATIONAL_CONSTANT_AU_DAY
from chronos_safe.domain.state import SystemState


def pairwise_accelerations(
    masses: np.ndarray,
    positions: np.ndarray,
    softening: float = DEFAULT_SOFTENING_AU,
) -> np.ndarray:
    n = masses.shape[0]
    accelerations = np.zeros_like(positions, dtype=np.float64)
    for i in range(n):
        delta = positions - positions[i]
        dist_sq = np.sum(delta * delta, axis=1) + softening**2
        inv_dist3 = np.where(dist_sq > 0.0, dist_sq ** (-1.5), 0.0)
        contrib = GRAVITATIONAL_CONSTANT_AU_DAY * (masses[:, None] * delta) * inv_dist3[:, None]
        accelerations[i] = np.sum(contrib, axis=0)
        accelerations[i] -= contrib[i]
    return accelerations


@dataclass(slots=True)
class QuickIntegrator:
    dt_days: float
    softening: float = DEFAULT_SOFTENING_AU

    def acceleration(self, state: SystemState) -> np.ndarray:
        return pairwise_accelerations(state.masses, state.positions, self.softening)

    def step(self, state: SystemState) -> SystemState:
        acceleration_0 = self.acceleration(state)
        next_state = state.copy()
        next_state.positions = state.positions + state.velocities * self.dt_days + 0.5 * acceleration_0 * self.dt_days**2
        acceleration_1 = pairwise_accelerations(state.masses, next_state.positions, self.softening)
        next_state.velocities = state.velocities + 0.5 * (acceleration_0 + acceleration_1) * self.dt_days
        next_state.metadata["integrator"] = "quick_verlet"
        next_state.metadata["dt_days"] = self.dt_days
        return next_state
