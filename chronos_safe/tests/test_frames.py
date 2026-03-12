import numpy as np

from chronos_safe.domain.state import BodyState, SystemState
from chronos_safe.physics.frames import center_of_mass, center_of_mass_velocity, standardize_state


def test_standardize_state_moves_barycenter_to_zero() -> None:
    state = SystemState.from_bodies(
        [
            BodyState("sun", 1.0, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
            BodyState("earth", 3.0e-6, [1.0, 0.0, 0.0], [0.0, 0.017, 0.0]),
        ]
    )
    standardized = standardize_state(state)
    assert np.allclose(center_of_mass(standardized), np.zeros(3), atol=1.0e-12)
    assert np.allclose(center_of_mass_velocity(standardized), np.zeros(3), atol=1.0e-12)
