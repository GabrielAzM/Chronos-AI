"""Device helpers."""

from __future__ import annotations


def get_device(preferred: str = "cpu") -> str:
    if preferred == "cpu":
        return "cpu"
    try:
        import torch

        if preferred == "cuda" and torch.cuda.is_available():
            return "cuda"
    except ImportError:
        return "cpu"
    return "cpu"
