"""Simulation and evaluation results."""

from __future__ import annotations

from dataclasses import dataclass, field

from chronos_safe.domain.state import SystemState
from chronos_safe.domain.types import JsonDict


@dataclass(slots=True)
class FallbackEvent:
    step: int
    time_days: float
    reason: str
    affected_bodies: list[str]
    score: float | None
    action: str

    def to_dict(self) -> JsonDict:
        return {
            "step": self.step,
            "time_days": self.time_days,
            "reason": self.reason,
            "affected_bodies": list(self.affected_bodies),
            "score": self.score,
            "action": self.action,
        }


@dataclass(slots=True)
class SimulationResult:
    initial_state: SystemState
    states: list[SystemState]
    fallback_events: list[FallbackEvent]
    metrics: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        return {
            "initial_state": self.initial_state.to_dict(),
            "states": [state.to_dict() for state in self.states],
            "fallback_events": [event.to_dict() for event in self.fallback_events],
            "metrics": dict(self.metrics),
        }


@dataclass(slots=True)
class BenchmarkResult:
    name: str
    runtime_seconds: float
    metrics: JsonDict

    def to_dict(self) -> JsonDict:
        return {
            "name": self.name,
            "runtime_seconds": self.runtime_seconds,
            "metrics": dict(self.metrics),
        }
