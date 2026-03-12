import pytest

from chronos_safe.physics.units import (
    au_to_meters,
    days_to_seconds,
    kg_to_solar_mass,
    meters_to_au,
    seconds_to_days,
    solar_mass_to_kg,
)


def test_distance_roundtrip() -> None:
    value = 123_456_789.0
    assert meters_to_au(au_to_meters(value)) == pytest.approx(value)


def test_time_roundtrip() -> None:
    value = 3.5
    assert seconds_to_days(days_to_seconds(value)) == pytest.approx(value)


def test_mass_roundtrip() -> None:
    value = 0.002
    assert kg_to_solar_mass(solar_mass_to_kg(value)) == pytest.approx(value)
