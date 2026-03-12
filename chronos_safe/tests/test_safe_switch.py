import numpy as np

from chronos_safe.domain.state import BodyState, SystemState
from chronos_safe.physics.frames import standardize_state
from chronos_safe.simulation.safe_switch import evaluate_state_safety


def test_safe_switch_fallbacks_on_large_residual() -> None:
    state = standardize_state(
        SystemState.from_bodies(
            [
                BodyState("sun", 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
                BodyState("earth", 3.0e-6, [1.0, 0.0, 0.0], [0.0, 0.017, 0.0]),
            ]
        )
    )
    decision, event = evaluate_state_safety(
        current_state=state,
        candidate_state=state,
        residual_acceleration=np.full((2, 3), 10.0),
        step=1,
        time_days=1.0,
        ood_score=0.0,
        ood_threshold=10.0,
    )
    assert not decision.safe
    assert event is not None
    assert event.reason == "residual_limit"
