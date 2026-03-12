"""Convenience launcher for the CHRONOS-SAFE web interface."""

from __future__ import annotations

import os
import threading
import webbrowser

from chronos_safe.config.settings import SETTINGS
from chronos_safe.utils.logging_utils import configure_logging


def _ensure_runtime_directories() -> None:
    for path in (
        SETTINGS.data_root,
        SETTINGS.data_root / "raw",
        SETTINGS.data_root / "processed",
        SETTINGS.data_root / "cache",
        SETTINGS.data_root / "fixtures",
        SETTINGS.models_root,
        SETTINGS.models_root / "checkpoints",
        SETTINGS.models_root / "scalers",
        SETTINGS.reports_root,
        SETTINGS.reports_root / "figures",
        SETTINGS.reports_root / "benchmarks",
        SETTINGS.reports_root / "validation",
    ):
        path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - runtime dependency error
        raise RuntimeError(
            "uvicorn is required to run the web UI. Install with: python -m pip install -e ."
        ) from exc

    configure_logging(SETTINGS.log_level)
    _ensure_runtime_directories()

    host = os.getenv("CHRONOS_HOST", "127.0.0.1")
    port = int(os.getenv("CHRONOS_PORT", "8000"))
    open_browser = os.getenv("CHRONOS_OPEN_BROWSER", "true").lower() == "true"
    url = f"http://{host}:{port}/"

    if open_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    print(f"CHRONOS-SAFE web UI: {url}")
    uvicorn.run("chronos_safe.apps.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
