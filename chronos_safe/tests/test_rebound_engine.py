import numpy as np

from chronos_safe.domain.state import BodyState, SystemState
from chronos_safe.physics.frames import standardize_state
from chronos_safe.physics.rebound_engine import ReboundReferenceEngine


def test_reference_engine_two_body_step_is_finite() -> None:
    state = standardize_state(
        SystemState.from_bodies(
            [
                BodyState("sun", 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
                BodyState("earth", 3.0e-6, [1.0, 0.0, 0.0], [0.0, 0.01720209895, 0.0]),
            ]
        )
    )
    engine = ReboundReferenceEngine(dt_days=1.0, use_rebound=False)
    next_state = engine.step(state)
    assert np.all(np.isfinite(next_state.positions))
    assert np.all(np.isfinite(next_state.velocities))
    assert next_state.metadata["integrator"] in {"rebound", "numpy_reference"}
