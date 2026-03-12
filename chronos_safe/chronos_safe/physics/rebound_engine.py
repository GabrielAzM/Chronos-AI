"""Reference engine backed by REBOUND when available."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chronos_safe.config.constants import DEFAULT_REFERENCE_SUBSTEPS
from chronos_safe.domain.state import SystemState
from chronos_safe.physics.quick_integrator import QuickIntegrator, pairwise_accelerations

try:
    import rebound  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    rebound = None


@dataclass(slots=True)
class ReboundReferenceEngine:
    dt_days: float
    substeps: int = DEFAULT_REFERENCE_SUBSTEPS
    use_rebound: bool = True

    def backend_name(self) -> str:
        if rebound is not None and self.use_rebound:
            return "rebound"
        return "numpy_reference"

    def acceleration(self, state: SystemState) -> np.ndarray:
        return pairwise_accelerations(state.masses, state.positions)

    def step(self, state: SystemState) -> SystemState:
        if rebound is not None and self.use_rebound:
            return self._step_with_rebound(state)
        return self._step_with_numpy_reference(state)

    def _step_with_numpy_reference(self, state: SystemState) -> SystemState:
        reference = state.copy()
        sub_dt = self.dt_days / float(self.substeps)
        integrator = QuickIntegrator(dt_days=sub_dt)
        for _ in range(self.substeps):
            reference = integrator.step(reference)
        reference.metadata["integrator"] = self.backend_name()
        reference.metadata["dt_days"] = self.dt_days
        return reference

    def _step_with_rebound(self, state: SystemState) -> SystemState:
        sim = rebound.Simulation()
        sim.units = ("AU", "days", "Msun")
        sim.integrator = "ias15"
        for body_id, mass, position, velocity in zip(state.ids, state.masses, state.positions, state.velocities, strict=True):
            sim.add(
                m=float(mass),
                x=float(position[0]),
                y=float(position[1]),
                z=float(position[2]),
                vx=float(velocity[0]),
                vy=float(velocity[1]),
                vz=float(velocity[2]),
                hash=body_id,
            )
        sim.move_to_com()
        sim.integrate(self.dt_days)
        positions = []
        velocities = []
        for body_id in state.ids:
            particle = sim.particles[body_id]
            positions.append([particle.x, particle.y, particle.z])
            velocities.append([particle.vx, particle.vy, particle.vz])
        reference = SystemState(
            ids=list(state.ids),
            masses=state.masses.copy(),
            positions=np.asarray(positions, dtype=np.float64),
            velocities=np.asarray(velocities, dtype=np.float64),
            metadata={**state.metadata, "integrator": self.backend_name(), "dt_days": self.dt_days},
        )
        return reference
