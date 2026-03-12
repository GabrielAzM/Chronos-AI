"""Unit conversions."""

from __future__ import annotations

from chronos_safe.config.constants import (
    AU_IN_METERS,
    DAY_IN_SECONDS,
    SOLAR_MASS_IN_KG,
)


def meters_to_au(value_m: float) -> float:
    return value_m / AU_IN_METERS


def au_to_meters(value_au: float) -> float:
    return value_au * AU_IN_METERS


def seconds_to_days(value_s: float) -> float:
    return value_s / DAY_IN_SECONDS


def days_to_seconds(value_days: float) -> float:
    return value_days * DAY_IN_SECONDS


def kg_to_solar_mass(value_kg: float) -> float:
    return value_kg / SOLAR_MASS_IN_KG


def solar_mass_to_kg(value_sm: float) -> float:
    return value_sm * SOLAR_MASS_IN_KG
