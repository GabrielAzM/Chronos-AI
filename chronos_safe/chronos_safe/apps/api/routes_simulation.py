"""Simulation routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

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


@router.post("/simulate")
def simulate(request: SimulateRequest) -> dict[str, object]:
    client = HorizonsClient()
    initial_state = client.load_fixture(request.fixture_name)
    model = load_torch_model(request.checkpoint_path) if request.checkpoint_path else None
    scaler = PhysicalScaler.load(request.scaler_path) if request.scaler_path else None
    ood_guard = OODGuard.load(request.ood_guard_path) if request.ood_guard_path else None
    engine = HybridEngine(
        quick_integrator=QuickIntegrator(dt_days=request.dt_days),
        reference_engine=ReboundReferenceEngine(dt_days=request.dt_days, use_rebound=SETTINGS.use_rebound_if_available),
        model=model,
        scaler=scaler,
        ood_guard=ood_guard,
    )
    result = run_hybrid_rollout(initial_state, engine, RolloutConfig(steps=request.steps, dt_days=request.dt_days))
    return result.to_dict()


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
