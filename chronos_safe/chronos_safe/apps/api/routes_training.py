"""Training routes."""

from __future__ import annotations

from fastapi import APIRouter

from chronos_safe.apps.api.schemas import TrainRequest
from chronos_safe.training.train_generalist import run_train_generalist
from chronos_safe.training.train_specialist import run_train_specialist

router = APIRouter(prefix="/train", tags=["training"])


@router.post("/generalist")
def train_generalist(request: TrainRequest) -> dict[str, object]:
    return run_train_generalist(
        dataset_dir=request.dataset_dir,
        output_dir=request.output_dir,
        epochs=request.epochs,
        batch_size=request.batch_size,
    )


@router.post("/specialist")
def train_specialist(request: TrainRequest) -> dict[str, object]:
    return run_train_specialist(
        dataset_dir=request.dataset_dir,
        output_dir=request.output_dir,
        epochs=request.epochs,
        batch_size=request.batch_size,
    )
