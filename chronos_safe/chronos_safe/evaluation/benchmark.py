"""Benchmarking helpers."""

from __future__ import annotations

import time

from chronos_safe.domain.results import BenchmarkResult, SimulationResult
from chronos_safe.domain.state import SystemState
from chronos_safe.evaluation.metrics import compare_rollouts
from chronos_safe.physics.quick_integrator import QuickIntegrator
from chronos_safe.physics.rebound_engine import ReboundReferenceEngine
from chronos_safe.simulation.hybrid_engine import HybridEngine
from chronos_safe.simulation.rollout import RolloutConfig, run_hybrid_rollout


def _run_reference_rollout(initial_state: SystemState, reference: ReboundReferenceEngine, config: RolloutConfig) -> SimulationResult:
    states = [initial_state.copy()]
    current = initial_state.copy()
    for _ in range(config.steps):
        current = reference.step(current)
        states.append(current.copy())
    from chronos_safe.evaluation.metrics import rollout_metrics

    return SimulationResult(initial_state=initial_state, states=states, fallback_events=[], metrics=rollout_metrics(states))


def benchmark_rollouts(
    initial_state: SystemState,
    hybrid_engine: HybridEngine,
    reference_engine: ReboundReferenceEngine,
    config: RolloutConfig,
) -> dict[str, object]:
    start = time.perf_counter()
    reference_result = _run_reference_rollout(initial_state, reference_engine, config)
    reference_runtime = time.perf_counter() - start

    start = time.perf_counter()
    hybrid_result = run_hybrid_rollout(initial_state, hybrid_engine, config)
    hybrid_runtime = time.perf_counter() - start

    comparison = compare_rollouts(reference_result.states, hybrid_result.states)
    speedup = reference_runtime / max(hybrid_runtime, 1.0e-12)

    return {
        "reference": reference_result,
        "hybrid": hybrid_result,
        "benchmarks": {
            "reference": BenchmarkResult("reference", reference_runtime, reference_result.metrics),
            "hybrid": BenchmarkResult(
                "hybrid",
                hybrid_runtime,
                {
                    **hybrid_result.metrics,
                    **comparison,
                    "speedup_vs_reference": speedup,
                    "fallback_rate": len(hybrid_result.fallback_events) / max(config.steps, 1),
                },
            ),
        },
    }
