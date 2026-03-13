"""Simulation routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from chronos_safe.apps.api.schemas import SimulateRequest
from chronos_safe.config.settings import SETTINGS
from chronos_safe.data.horizons_client import HorizonsClient
from chronos_safe.data.scalers import PhysicalScaler
from chronos_safe.models.ood_guard import OODGuard
from chronos_safe.physics.quick_integrator import QuickIntegrator
from chronos_safe.physics.rebound_engine import ReboundReferenceEngine
from chronos_safe.simulation.hybrid_engine import HybridEngine, load_torch_model
from chronos_safe.simulation.mission_apophis import ApophisValidationConfig, run_apophis_validation
from chronos_safe.simulation.rollout import RolloutConfig, run_hybrid_rollout

router = APIRouter(tags=["simulation"])


def _build_engine(request: SimulateRequest) -> HybridEngine:
    try:
        model = load_torch_model(request.checkpoint_path) if request.checkpoint_path else None
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    scaler = PhysicalScaler.load(request.scaler_path) if request.scaler_path else None
    ood_guard = OODGuard.load(request.ood_guard_path) if request.ood_guard_path else None
    return HybridEngine(
        quick_integrator=QuickIntegrator(dt_days=request.dt_days),
        reference_engine=ReboundReferenceEngine(dt_days=request.dt_days, use_rebound=SETTINGS.use_rebound_if_available),
        model=model,
        scaler=scaler,
        ood_guard=ood_guard,
    )


def _trajectory_payload(result, dt_days: float, source: str) -> dict[str, object]:
    return {
        "source": source,
        "ids": list(result.states[0].ids),
        "frames": [state.positions.tolist() for state in result.states],
        "dt_days": dt_days,
        "metrics": dict(result.metrics),
        "fallback_events": [event.to_dict() for event in result.fallback_events],
    }


@router.post("/simulate")
def simulate(request: SimulateRequest) -> dict[str, object]:
    client = HorizonsClient()
    initial_state = client.load_fixture(request.fixture_name)
    engine = _build_engine(request)
    result = run_hybrid_rollout(initial_state, engine, RolloutConfig(steps=request.steps, dt_days=request.dt_days))
    return result.to_dict()


@router.post("/simulate/trajectory")
def simulate_trajectory(request: SimulateRequest) -> dict[str, object]:
    client = HorizonsClient()
    initial_state = client.load_fixture(request.fixture_name)
    engine = _build_engine(request)
    result = run_hybrid_rollout(initial_state, engine, RolloutConfig(steps=request.steps, dt_days=request.dt_days))
    return _trajectory_payload(result, request.dt_days, request.fixture_name)


@router.post("/validate/apophis")
def validate_apophis(request: SimulateRequest) -> dict[str, object]:
    return run_apophis_validation(
        ApophisValidationConfig(
            steps=request.steps,
            dt_days=request.dt_days,
            fixture_name=request.fixture_name,
            checkpoint_path=None if request.checkpoint_path is None else Path(request.checkpoint_path),
            scaler_path=None if request.scaler_path is None else Path(request.scaler_path),
            ood_guard_path=None if request.ood_guard_path is None else Path(request.ood_guard_path),
        )
    )
