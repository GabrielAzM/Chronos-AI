import numpy as np
import pytest

torch = pytest.importorskip("torch")

from chronos_safe.models.residual_gnn import ResidualGNN, ResidualGNNConfig


def test_model_forward_produces_finite_output() -> None:
    model = ResidualGNN(ResidualGNNConfig(hidden_dim=16, num_message_passing_steps=1))
    masses = torch.ones((2, 4), dtype=torch.float32)
    positions = torch.as_tensor(np.random.randn(2, 4, 3), dtype=torch.float32)
    velocities = torch.as_tensor(np.random.randn(2, 4, 3), dtype=torch.float32)
    mask = torch.tensor([[True, True, True, False], [True, True, True, True]])
    output = model(masses, positions, velocities, mask)
    assert output.shape == (2, 4, 3)
    assert torch.isfinite(output).all()
