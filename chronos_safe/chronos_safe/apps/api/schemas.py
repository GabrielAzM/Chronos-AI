"""API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    dataset_dir: str
    output_dir: str
    base_checkpoint: str | None = None
    epochs: int = Field(default=20, ge=1)
    batch_size: int = Field(default=16, ge=1)


class GenerateGeneralistRequest(BaseModel):
    output_dir: str
    num_samples: int = Field(default=128, ge=1)
    min_bodies: int = Field(default=2, ge=2)
    max_bodies: int = Field(default=6, ge=2)
    dt_days: float = Field(default=1.0, gt=0.0)


class GenerateSpecialistRequest(BaseModel):
    output_dir: str
    fixture_name: str = "apophis/apophis_fixture.json"
    num_samples: int = Field(default=64, ge=1)
    dt_days: float = Field(default=1.0, gt=0.0)


class SimulateRequest(BaseModel):
    fixture_name: str = "apophis/apophis_fixture.json"
    steps: int = Field(default=30, ge=1)
    dt_days: float = Field(default=1.0, gt=0.0)
    checkpoint_path: str | None = None
    scaler_path: str | None = None
    ood_guard_path: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
