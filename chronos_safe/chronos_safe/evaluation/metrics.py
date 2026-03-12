"""Simulation metrics."""

from __future__ import annotations

import numpy as np

from chronos_safe.domain.state import SystemState
from chronos_safe.physics.invariants import angular_momentum, total_energy


def _align_states(reference: list[SystemState], candidate: list[SystemState]) -> tuple[list[SystemState], list[SystemState]]:
    length = min(len(reference), len(candidate))
    return reference[:length], candidate[:length]


def position_error(reference: SystemState, candidate: SystemState) -> float:
    return float(np.mean(np.linalg.norm(reference.positions - candidate.positions, axis=1)))


def velocity_error(reference: SystemState, candidate: SystemState) -> float:
    return float(np.mean(np.linalg.norm(reference.velocities - candidate.velocities, axis=1)))


def earth_apophis_distance(state: SystemState) -> float | None:
    if "earth" not in state.ids or "apophis" not in state.ids:
        return None
    earth = state.body_index("earth")
    apophis = state.body_index("apophis")
    return float(np.linalg.norm(state.positions[earth] - state.positions[apophis]))


def rollout_metrics(states: list[SystemState]) -> dict[str, float]:
    initial_energy = total_energy(states[0])
    initial_l = angular_momentum(states[0])
    final_energy = total_energy(states[-1])
    final_l = angular_momentum(states[-1])
    energy_drift = abs(final_energy - initial_energy) / max(abs(initial_energy), 1.0e-12)
    angular_drift = float(np.linalg.norm(final_l - initial_l) / max(np.linalg.norm(initial_l), 1.0e-12))
    apophis_distance = earth_apophis_distance(states[-1])
    metrics = {
        "steps": float(len(states) - 1),
        "energy_drift": float(energy_drift),
        "angular_momentum_drift": angular_drift,
    }
    if apophis_distance is not None:
        metrics["earth_apophis_distance_final_au"] = apophis_distance
    return metrics


def compare_rollouts(reference_states: list[SystemState], candidate_states: list[SystemState]) -> dict[str, float]:
    reference_states, candidate_states = _align_states(reference_states, candidate_states)
    position_errors = np.asarray(
        [position_error(ref_state, cand_state) for ref_state, cand_state in zip(reference_states, candidate_states, strict=True)],
        dtype=np.float64,
    )
    velocity_errors = np.asarray(
        [velocity_error(ref_state, cand_state) for ref_state, cand_state in zip(reference_states, candidate_states, strict=True)],
        dtype=np.float64,
    )
    final_ref_distance = earth_apophis_distance(reference_states[-1])
    final_candidate_distance = earth_apophis_distance(candidate_states[-1])
    metrics = {
        "mean_position_error_au": float(position_errors.mean()),
        "final_position_error_au": float(position_errors[-1]),
        "mean_velocity_error_au_day": float(velocity_errors.mean()),
        "final_velocity_error_au_day": float(velocity_errors[-1]),
    }
    if final_ref_distance is not None and final_candidate_distance is not None:
        metrics["earth_apophis_distance_error_au"] = abs(final_candidate_distance - final_ref_distance)
    return metrics
