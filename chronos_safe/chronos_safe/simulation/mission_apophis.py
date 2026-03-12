"""Offline Apophis validation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chronos_safe.config.settings import SETTINGS
from chronos_safe.data.horizons_client import HorizonsClient
from chronos_safe.data.scalers import PhysicalScaler
from chronos_safe.domain.results import BenchmarkResult
from chronos_safe.evaluation.benchmark import benchmark_rollouts
from chronos_safe.evaluation.metrics import compare_rollouts
from chronos_safe.evaluation.plots import write_validation_summary
from chronos_safe.models.ood_guard import OODGuard
from chronos_safe.physics.quick_integrator import QuickIntegrator
from chronos_safe.physics.rebound_engine import ReboundReferenceEngine
from chronos_safe.simulation.hybrid_engine import HybridEngine, load_torch_model
from chronos_safe.simulation.rollout import RolloutConfig, run_hybrid_rollout
from chronos_safe.utils.serialization import write_json


@dataclass(slots=True)
class ApophisValidationConfig:
    steps: int = 180
    dt_days: float = 1.0
    fixture_name: str = "apophis/apophis_fixture.json"
    report_dir: Path = SETTINGS.reports_root / "validation"
    checkpoint_path: Path | None = None
    scaler_path: Path | None = None
    ood_guard_path: Path | None = None


def run_apophis_validation(config: ApophisValidationConfig) -> dict[str, object]:
    client = HorizonsClient()
    initial_state = client.load_fixture(config.fixture_name)

    model = load_torch_model(config.checkpoint_path) if config.checkpoint_path else None
    scaler = PhysicalScaler.load(str(config.scaler_path)) if config.scaler_path else None
    ood_guard = OODGuard.load(str(config.ood_guard_path)) if config.ood_guard_path else None

    quick = QuickIntegrator(dt_days=config.dt_days)
    reference = ReboundReferenceEngine(dt_days=config.dt_days, use_rebound=SETTINGS.use_rebound_if_available)
    hybrid_engine = HybridEngine(quick_integrator=quick, reference_engine=reference, model=model, scaler=scaler, ood_guard=ood_guard)
    rollout_config = RolloutConfig(steps=config.steps, dt_days=config.dt_days)

    benchmark = benchmark_rollouts(initial_state, hybrid_engine, reference, rollout_config)
    hybrid_result = benchmark["hybrid"]
    comparison_metrics = compare_rollouts(benchmark["reference"].states, hybrid_result.states)

    report = {
        "fixture_name": config.fixture_name,
        "steps": config.steps,
        "dt_days": config.dt_days,
        "hybrid_metrics": hybrid_result.metrics,
        "comparison_metrics": comparison_metrics,
        "fallback_count": len(hybrid_result.fallback_events),
        "benchmark": {name: result.to_dict() for name, result in benchmark["benchmarks"].items()},
    }
    config.report_dir.mkdir(parents=True, exist_ok=True)
    write_json(config.report_dir / "apophis_validation.json", report)
    write_validation_summary(config.report_dir / "apophis_validation_summary.txt", report)
    return report
