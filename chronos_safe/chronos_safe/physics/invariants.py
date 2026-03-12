"""Conserved quantity calculations."""

from __future__ import annotations

import numpy as np

from chronos_safe.config.constants import GRAVITATIONAL_CONSTANT_AU_DAY, DEFAULT_SOFTENING_AU
from chronos_safe.domain.state import SystemState


def kinetic_energy(state: SystemState) -> float:
    return float(0.5 * np.sum(state.masses[:, None] * state.velocities * state.velocities))


def potential_energy(state: SystemState, softening: float = DEFAULT_SOFTENING_AU) -> float:
    total = 0.0
    for i in range(state.num_bodies):
        for j in range(i + 1, state.num_bodies):
            delta = state.positions[j] - state.positions[i]
            distance = float(np.linalg.norm(delta) + softening)
            total -= GRAVITATIONAL_CONSTANT_AU_DAY * state.masses[i] * state.masses[j] / distance
    return total


def total_energy(state: SystemState) -> float:
    return kinetic_energy(state) + potential_energy(state)


def angular_momentum(state: SystemState) -> np.ndarray:
    return np.sum(np.cross(state.positions, state.masses[:, None] * state.velocities), axis=0)
