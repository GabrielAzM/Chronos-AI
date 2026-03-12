"""Dataset generation routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from chronos_safe.apps.api.schemas import GenerateGeneralistRequest, GenerateSpecialistRequest
from chronos_safe.data.specialist_generator import SpecialistGenerationConfig, generate_specialist_dataset
from chronos_safe.data.synthetic_generator import SyntheticGenerationConfig, generate_generalist_dataset

router = APIRouter(prefix="/generate", tags=["data"])


@router.post("/generalist")
def generate_generalist(request: GenerateGeneralistRequest) -> dict[str, object]:
    output_dir = generate_generalist_dataset(
        SyntheticGenerationConfig(
            output_dir=Path(request.output_dir),
            num_samples=request.num_samples,
            min_bodies=request.min_bodies,
            max_bodies=request.max_bodies,
            dt_days=request.dt_days,
        )
    )
    return {"status": "ok", "kind": "generalist", "output_dir": str(output_dir.as_posix())}


@router.post("/specialist")
def generate_specialist(request: GenerateSpecialistRequest) -> dict[str, object]:
    output_dir = generate_specialist_dataset(
        SpecialistGenerationConfig(
            output_dir=Path(request.output_dir),
            fixture_name=request.fixture_name,
            num_samples=request.num_samples,
            dt_days=request.dt_days,
        )
    )
    return {"status": "ok", "kind": "specialist", "output_dir": str(output_dir.as_posix())}
