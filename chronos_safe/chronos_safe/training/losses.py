"""Training losses."""

from __future__ import annotations

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency
    torch = None


def _require_torch() -> None:
    if torch is None:  # pragma: no cover - exercised only without torch
        raise RuntimeError("PyTorch is required for training.")


def masked_mse(prediction, target, mask):
    _require_torch()
    diff = (prediction - target) * mask[..., None]
    denom = mask.sum().clamp_min(1)
    return torch.sum(diff * diff) / denom


def residual_norm_penalty(prediction, mask, weight: float = 1.0e-3):
    _require_torch()
    norm = torch.linalg.norm(prediction * mask[..., None], dim=-1)
    denom = mask.sum().clamp_min(1)
    return weight * torch.sum(norm) / denom


def composite_loss(prediction, target, mask):
    return masked_mse(prediction, target, mask) + residual_norm_penalty(prediction, mask)
