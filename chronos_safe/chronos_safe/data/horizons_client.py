"""Offline-first Horizons access."""

from __future__ import annotations

from pathlib import Path

from chronos_safe.config.settings import SETTINGS
from chronos_safe.domain.state import SystemState
from chronos_safe.utils.serialization import read_json

try:
    from astroquery.jplhorizons import Horizons  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    Horizons = None


class HorizonsClient:
    def __init__(self, fixtures_root: Path | None = None) -> None:
        self.fixtures_root = fixtures_root or (SETTINGS.data_root / "fixtures")

    def load_fixture(self, name: str) -> SystemState:
        fixture_path = self.fixtures_root / name
        payload = read_json(fixture_path)
        return SystemState.from_dict(payload)

    def fetch_system(
        self,
        body_names: list[str],
        epoch_jd: float,
        online: bool = False,
    ) -> SystemState:
        if not online or Horizons is None:
            return self.load_fixture("solar_system/simplified_solar_system.json")

        bodies = []
        for body_name in body_names:
            table = Horizons(id=body_name, location="@sun", epochs=epoch_jd).vectors()
            bodies.append(
                {
                    "body_id": body_name.lower(),
                    "mass": 0.0,
                    "position": [float(table["x"][0]), float(table["y"][0]), float(table["z"][0])],
                    "velocity": [float(table["vx"][0]), float(table["vy"][0]), float(table["vz"][0])],
                }
            )
        masses = {
            "sun": 1.0,
            "mercury": 1.6601208254589484e-7,
            "venus": 2.4478382877847715e-6,
            "earth": 3.00348959632e-6,
            "apophis": 3.335e-19,
        }
        return SystemState.from_dict(
            {
                "ids": [body["body_id"] for body in bodies],
                "masses": [masses.get(body["body_id"], 0.0) for body in bodies],
                "positions": [body["position"] for body in bodies],
                "velocities": [body["velocity"] for body in bodies],
                "metadata": {"source": "astroquery_horizons", "epoch_jd": epoch_jd},
            }
        )
