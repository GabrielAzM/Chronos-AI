"""Rollout orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from chronos_safe.domain.results import SimulationResult
from chronos_safe.domain.state import SystemState
from chronos_safe.evaluation.metrics import rollout_metrics
from chronos_safe.physics.invariants import angular_momentum, total_energy
from chronos_safe.simulation.hybrid_engine import HybridEngine


@dataclass(slots=True)
class RolloutConfig:
    steps: int
    dt_days: float


def run_hybrid_rollout(initial_state: SystemState, engine: HybridEngine, config: RolloutConfig) -> SimulationResult:
    current_state = initial_state.copy()
    states = [current_state.copy()]
    events = []
    baseline_energy = total_energy(current_state)
    baseline_l = angular_momentum(current_state)
    for step in range(1, config.steps + 1):
        output = engine.step(
            current_state=current_state,
            step=step,
            time_days=step * config.dt_days,
            baseline_energy=baseline_energy,
            baseline_angular_momentum=baseline_l,
        )
        current_state = output.state
        states.append(current_state.copy())
        if output.fallback_event is not None:
            events.append(output.fallback_event)
    return SimulationResult(
        initial_state=initial_state,
        states=states,
        fallback_events=events,
        metrics=rollout_metrics(states),
    )
