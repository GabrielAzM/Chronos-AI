"""Project settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from chronos_safe.config.constants import (
    DEFAULT_MAX_ANGULAR_MOMENTUM_DRIFT,
    DEFAULT_MAX_ENERGY_DRIFT,
    DEFAULT_MAX_RESIDUAL_ACCEL_AU_DAY2,
    DEFAULT_MAX_SPEED_AU_DAY,
    DEFAULT_MIN_DISTANCE_AU,
)


@dataclass(slots=True)
class Settings:
    project_root: Path
    data_root: Path
    models_root: Path
    reports_root: Path
    seed: int = 42
    device: str = "cpu"
    log_level: str = "INFO"
    use_rebound_if_available: bool = True
    max_residual_accel_au_day2: float = DEFAULT_MAX_RESIDUAL_ACCEL_AU_DAY2
    max_speed_au_day: float = DEFAULT_MAX_SPEED_AU_DAY
    min_distance_au: float = DEFAULT_MIN_DISTANCE_AU
    max_energy_drift: float = DEFAULT_MAX_ENERGY_DRIFT
    max_angular_momentum_drift: float = DEFAULT_MAX_ANGULAR_MOMENTUM_DRIFT

    @classmethod
    def from_env(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[2]
        data_root = Path(os.getenv("CHRONOS_DATA_ROOT", project_root / "data"))
        models_root = Path(os.getenv("CHRONOS_MODELS_ROOT", project_root / "models"))
        reports_root = Path(os.getenv("CHRONOS_REPORTS_ROOT", project_root / "reports"))
        return cls(
            project_root=project_root,
            data_root=data_root,
            models_root=models_root,
            reports_root=reports_root,
            seed=int(os.getenv("CHRONOS_SEED", "42")),
            device=os.getenv("CHRONOS_DEVICE", "cpu"),
            log_level=os.getenv("CHRONOS_LOG_LEVEL", "INFO"),
            use_rebound_if_available=os.getenv("CHRONOS_USE_REBOUND_IF_AVAILABLE", "true").lower() == "true",
            max_residual_accel_au_day2=float(
                os.getenv("CHRONOS_MAX_RESIDUAL_ACCEL_AU_DAY2", str(DEFAULT_MAX_RESIDUAL_ACCEL_AU_DAY2))
            ),
            max_speed_au_day=float(os.getenv("CHRONOS_MAX_SPEED_AU_DAY", str(DEFAULT_MAX_SPEED_AU_DAY))),
            min_distance_au=float(os.getenv("CHRONOS_MIN_DISTANCE_AU", str(DEFAULT_MIN_DISTANCE_AU))),
            max_energy_drift=float(os.getenv("CHRONOS_MAX_ENERGY_DRIFT", str(DEFAULT_MAX_ENERGY_DRIFT))),
            max_angular_momentum_drift=float(
                os.getenv("CHRONOS_MAX_ANGULAR_MOMENTUM_DRIFT", str(DEFAULT_MAX_ANGULAR_MOMENTUM_DRIFT))
            ),
        )


SETTINGS = Settings.from_env()
