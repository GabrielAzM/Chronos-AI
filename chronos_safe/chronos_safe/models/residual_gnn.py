"""Residual graph neural network."""

from __future__ import annotations

from dataclasses import dataclass

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - optional dependency
    torch = None
    nn = None


@dataclass(slots=True)
class ResidualGNNConfig:
    hidden_dim: int = 64
    num_message_passing_steps: int = 2
    dropout: float = 0.1
    residual_scale: float = 1.0


def _require_torch() -> None:
    if torch is None or nn is None:  # pragma: no cover - exercised only without torch
        raise RuntimeError("PyTorch is required for ResidualGNN. Install the 'ml' extras.")


if nn is not None:
    class MLP(nn.Module):
        def __init__(self, in_features: int, hidden_dim: int, out_features: int, dropout: float) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(in_features, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, out_features),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)


    class ResidualGNN(nn.Module):
        def __init__(self, config: ResidualGNNConfig | None = None) -> None:
            super().__init__()
            _require_torch()
            self.config = config or ResidualGNNConfig()
            node_dim = 7
            edge_dim = 13
            hidden_dim = self.config.hidden_dim
            self.node_encoder = MLP(node_dim, hidden_dim, hidden_dim, self.config.dropout)
            self.edge_mlp = MLP(hidden_dim * 2 + edge_dim, hidden_dim, hidden_dim, self.config.dropout)
            self.node_update = MLP(hidden_dim * 2, hidden_dim, hidden_dim, self.config.dropout)
            self.head = nn.Linear(hidden_dim, 3)

        def _edge_features(
            self,
            masses: torch.Tensor,
            positions: torch.Tensor,
            velocities: torch.Tensor,
        ) -> torch.Tensor:
            delta_r = positions[:, :, None, :] - positions[:, None, :, :]
            delta_v = velocities[:, :, None, :] - velocities[:, None, :, :]
            dist = torch.linalg.norm(delta_r, dim=-1, keepdim=True).clamp_min(1.0e-8)
            direction = delta_r / dist
            inv_dist = 1.0 / dist
            inv_dist2 = 1.0 / (dist * dist)
            mass_ratio = masses[:, :, None, None] / masses[:, None, :, None].clamp_min(1.0e-12)
            return torch.cat([delta_r, delta_v, dist, direction, inv_dist, inv_dist2, mass_ratio], dim=-1)

        def forward(
            self,
            masses: torch.Tensor,
            positions: torch.Tensor,
            velocities: torch.Tensor,
            mask: torch.Tensor,
        ) -> torch.Tensor:
            node_features = torch.cat([masses[..., None], positions, velocities], dim=-1)
            node_latent = self.node_encoder(node_features)
            edge_features = self._edge_features(masses, positions, velocities)
            active_mask = (mask[:, :, None] & mask[:, None, :]).unsqueeze(-1)
            identity_mask = ~torch.eye(mask.shape[1], device=mask.device, dtype=torch.bool)[None, :, :, None]

            for _ in range(self.config.num_message_passing_steps):
                source = node_latent[:, :, None, :].expand(-1, -1, node_latent.shape[1], -1)
                target = node_latent[:, None, :, :].expand(-1, node_latent.shape[1], -1, -1)
                messages = self.edge_mlp(torch.cat([source, target, edge_features], dim=-1))
                messages = messages * active_mask * identity_mask
                aggregated = torch.sum(messages, dim=2)
                node_latent = self.node_update(torch.cat([node_latent, aggregated], dim=-1))

            residual = self.head(node_latent) * self.config.residual_scale
            return residual * mask[..., None]
else:
    class ResidualGNN:  # pragma: no cover - exercised only without torch
        def __init__(self, config: ResidualGNNConfig | None = None) -> None:
            _require_torch()
