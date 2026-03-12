"""Curriculum stages."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CurriculumStage:
    name: str
    min_bodies: int
    max_bodies: int
    num_samples: int


def default_curriculum() -> list[CurriculumStage]:
    return [
        CurriculumStage(name="two_body", min_bodies=2, max_bodies=2, num_samples=64),
        CurriculumStage(name="few_body", min_bodies=3, max_bodies=4, num_samples=96),
        CurriculumStage(name="simplified_solar_system", min_bodies=4, max_bodies=6, num_samples=128),
        CurriculumStage(name="specialist_real", min_bodies=3, max_bodies=3, num_samples=64),
    ]
