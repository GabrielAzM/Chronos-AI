"""Reference frame operations."""

from __future__ import annotations

import numpy as np

from chronos_safe.domain.state import SystemState


def center_of_mass(state: SystemState) -> np.ndarray:
    total_mass = np.sum(state.masses)
    return np.sum(state.positions * state.masses[:, None], axis=0) / total_mass


def center_of_mass_velocity(state: SystemState) -> np.ndarray:
    total_mass = np.sum(state.masses)
    return np.sum(state.velocities * state.masses[:, None], axis=0) / total_mass


def to_barycentric(state: SystemState) -> SystemState:
    centered = state.copy()
    centered.positions = centered.positions - center_of_mass(state)
    centered.velocities = centered.velocities - center_of_mass_velocity(state)
    centered.metadata["frame"] = "barycentric"
    return centered


def canonical_order(state: SystemState) -> SystemState:
    order = np.argsort(np.asarray(state.ids))
    ordered = state.copy()
    ordered.ids = [ordered.ids[index] for index in order]
    ordered.masses = ordered.masses[order]
    ordered.positions = ordered.positions[order]
    ordered.velocities = ordered.velocities[order]
    ordered.metadata["ordered"] = True
    return ordered


def standardize_state(state: SystemState) -> SystemState:
    return canonical_order(to_barycentric(state))
