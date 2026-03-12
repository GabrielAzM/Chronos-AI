"""FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from chronos_safe.apps.api.routes_data import router as data_router
from chronos_safe.apps.api.routes_simulation import router as simulation_router
from chronos_safe.apps.api.routes_training import router as training_router
from chronos_safe.apps.api.schemas import HealthResponse
from chronos_safe.apps.api.web_ui import build_catalog_payload, render_dashboard_html
from chronos_safe.version import __version__

app = FastAPI(title="CHRONOS-SAFE", version=__version__)
app.include_router(data_router)
app.include_router(training_router)
app.include_router(simulation_router)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(render_dashboard_html())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/ui/catalog")
def ui_catalog() -> dict[str, object]:
    return build_catalog_payload()
