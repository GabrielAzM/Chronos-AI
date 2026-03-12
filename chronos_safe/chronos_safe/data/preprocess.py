"""State standardization and dataset sample construction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from chronos_safe.domain.state import SystemState
from chronos_safe.physics.frames import standardize_state


@dataclass(slots=True)
class ProcessedSample:
    ids: list[str]
    masses: np.ndarray
    positions: np.ndarray
    velocities: np.ndarray
    target_delta_acc: np.ndarray
    teacher_positions_next: np.ndarray
    teacher_velocities_next: np.ndarray
    mask: np.ndarray
    metadata: dict[str, object]


def effective_delta_acceleration(
    teacher_next: SystemState,
    quick_next: SystemState,
    dt_days: float,
) -> np.ndarray:
    velocity_delta = teacher_next.velocities - quick_next.velocities
    return velocity_delta / dt_days


def pad_array(array: np.ndarray, target_shape: tuple[int, ...], fill_value: float = 0.0) -> np.ndarray:
    padded = np.full(target_shape, fill_value=fill_value, dtype=np.float64)
    slices = tuple(slice(0, min(src, dst)) for src, dst in zip(array.shape, target_shape, strict=False))
    padded[slices] = array[slices]
    return padded


def pad_ids(ids: list[str], max_bodies: int) -> list[str]:
    padded = list(ids)
    while len(padded) < max_bodies:
        padded.append(f"pad_{len(padded):02d}")
    return padded


def build_processed_sample(
    initial_state: SystemState,
    teacher_next: SystemState,
    quick_next: SystemState,
    max_bodies: int,
    dt_days: float,
) -> ProcessedSample:
    current = standardize_state(initial_state)
    teacher = standardize_state(teacher_next)
    quick = standardize_state(quick_next)
    n = current.num_bodies
    target_delta_acc = effective_delta_acceleration(teacher, quick, dt_days)
    mask = np.zeros((max_bodies,), dtype=bool)
    mask[:n] = True
    return ProcessedSample(
        ids=pad_ids(current.ids, max_bodies),
        masses=pad_array(current.masses, (max_bodies,)),
        positions=pad_array(current.positions, (max_bodies, 3)),
        velocities=pad_array(current.velocities, (max_bodies, 3)),
        target_delta_acc=pad_array(target_delta_acc, (max_bodies, 3)),
        teacher_positions_next=pad_array(teacher.positions, (max_bodies, 3)),
        teacher_velocities_next=pad_array(teacher.velocities, (max_bodies, 3)),
        mask=mask,
        metadata={**current.metadata, "num_bodies": n, "dt_days": dt_days},
    )
