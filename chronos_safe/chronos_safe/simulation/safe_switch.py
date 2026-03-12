"""Safety guard and fallback decisions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chronos_safe.config.settings import SETTINGS
from chronos_safe.domain.results import FallbackEvent
from chronos_safe.domain.state import SystemState
from chronos_safe.physics.invariants import angular_momentum, total_energy


@dataclass(slots=True)
class SafetyDecision:
    safe: bool
    reason: str
    score: float | None = None


def min_pair_distance(state: SystemState) -> float:
    min_distance = float("inf")
    for i in range(state.num_bodies):
        for j in range(i + 1, state.num_bodies):
            distance = float(np.linalg.norm(state.positions[i] - state.positions[j]))
            min_distance = min(min_distance, distance)
    return min_distance if np.isfinite(min_distance) else 0.0


def evaluate_state_safety(
    current_state: SystemState,
    candidate_state: SystemState,
    residual_acceleration: np.ndarray,
    step: int,
    time_days: float,
    ood_score: float | None,
    uncertainty_score: float | None = None,
    ood_threshold: float | None = None,
    uncertainty_threshold: float | None = None,
    baseline_energy: float | None = None,
    baseline_angular_momentum: np.ndarray | None = None,
) -> tuple[SafetyDecision, FallbackEvent | None]:
    if not np.all(np.isfinite(candidate_state.positions)) or not np.all(np.isfinite(candidate_state.velocities)):
        reason = "nan_or_inf"
    elif not np.all(np.isfinite(residual_acceleration)):
        reason = "invalid_residual"
    elif float(np.max(np.linalg.norm(residual_acceleration, axis=1))) > SETTINGS.max_residual_accel_au_day2:
        reason = "residual_limit"
    elif float(np.max(np.linalg.norm(candidate_state.velocities, axis=1))) > SETTINGS.max_speed_au_day:
        reason = "speed_limit"
    elif min_pair_distance(candidate_state) < SETTINGS.min_distance_au:
        reason = "distance_limit"
    elif ood_score is not None and ood_threshold is not None and ood_score > ood_threshold:
        reason = "ood_limit"
    elif uncertainty_score is not None and uncertainty_threshold is not None and uncertainty_score > uncertainty_threshold:
        reason = "uncertainty_limit"
    else:
        reason = ""

    if not reason and baseline_energy is not None:
        energy_drift = abs(total_energy(candidate_state) - baseline_energy) / max(abs(baseline_energy), 1.0e-12)
        if energy_drift > SETTINGS.max_energy_drift:
            reason = "energy_drift"

    if not reason and baseline_angular_momentum is not None:
        current_l = angular_momentum(candidate_state)
        baseline_norm = max(float(np.linalg.norm(baseline_angular_momentum)), 1.0e-12)
        drift = float(np.linalg.norm(current_l - baseline_angular_momentum) / baseline_norm)
        if drift > SETTINGS.max_angular_momentum_drift:
            reason = "angular_momentum_drift"

    if not reason:
        return SafetyDecision(safe=True, reason="accepted", score=ood_score), None

    event = FallbackEvent(
        step=step,
        time_days=time_days,
        reason=reason,
        affected_bodies=list(current_state.ids),
        score=ood_score if ood_score is not None else uncertainty_score,
        action="fallback_to_reference_engine",
    )
    return SafetyDecision(safe=False, reason=reason, score=event.score), event
