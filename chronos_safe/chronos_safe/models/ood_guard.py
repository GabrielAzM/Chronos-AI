"""OOD scoring and guard thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from chronos_safe.utils.serialization import read_json, write_json


def _flatten_features(masses: np.ndarray, positions: np.ndarray, velocities: np.ndarray, mask: np.ndarray) -> np.ndarray:
    features = np.concatenate([masses[..., None], positions, velocities], axis=-1)
    features = features * mask[..., None]
    return features.reshape(features.shape[0], -1)


def _match_feature_dim(features: np.ndarray, feature_dim: int) -> np.ndarray:
    if features.shape[1] == feature_dim:
        return features
    if features.shape[1] < feature_dim:
        padded = np.zeros((features.shape[0], feature_dim), dtype=np.float64)
        padded[:, : features.shape[1]] = features
        return padded
    return features[:, :feature_dim]


@dataclass(slots=True)
class OODGuard:
    centroid: np.ndarray | None = None
    variance: np.ndarray | None = None
    threshold: float = 6.0
    metadata: dict[str, object] = field(default_factory=dict)

    def fit(self, masses: np.ndarray, positions: np.ndarray, velocities: np.ndarray, mask: np.ndarray) -> "OODGuard":
        features = _flatten_features(masses, positions, velocities, mask)
        self.centroid = features.mean(axis=0)
        self.variance = features.var(axis=0) + 1.0e-6
        scores = self.score_batch(masses, positions, velocities, mask)
        self.threshold = float(np.percentile(scores, 95)) if scores.size else self.threshold
        self.metadata = {"feature_dim": int(features.shape[1])}
        return self

    def score_batch(self, masses: np.ndarray, positions: np.ndarray, velocities: np.ndarray, mask: np.ndarray) -> np.ndarray:
        if self.centroid is None or self.variance is None:
            return np.zeros((masses.shape[0],), dtype=np.float64)
        features = _flatten_features(masses, positions, velocities, mask)
        features = _match_feature_dim(features, self.centroid.shape[0])
        delta = features - self.centroid[None, :]
        return np.sqrt(np.mean((delta * delta) / self.variance[None, :], axis=1))

    def score_single(self, masses: np.ndarray, positions: np.ndarray, velocities: np.ndarray, mask: np.ndarray) -> float:
        return float(self.score_batch(masses[None, ...], positions[None, ...], velocities[None, ...], mask[None, ...])[0])

    def is_safe(self, score: float) -> bool:
        return score <= self.threshold

    def save(self, path: str) -> None:
        payload = {
            "centroid": None if self.centroid is None else self.centroid.tolist(),
            "variance": None if self.variance is None else self.variance.tolist(),
            "threshold": self.threshold,
            "metadata": self.metadata,
        }
        write_json(path, payload)

    @classmethod
    def load(cls, path: str) -> "OODGuard":
        payload = read_json(path)
        return cls(
            centroid=None if payload["centroid"] is None else np.asarray(payload["centroid"], dtype=np.float64),
            variance=None if payload["variance"] is None else np.asarray(payload["variance"], dtype=np.float64),
            threshold=float(payload["threshold"]),
            metadata=dict(payload.get("metadata", {})),
        )
