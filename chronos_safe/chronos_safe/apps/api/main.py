"""FastAPI app."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from chronos_safe.apps.api.routes_data import router as data_router
from chronos_safe.apps.api.routes_simulation import router as simulation_router
from chronos_safe.apps.api.routes_training import router as training_router
from chronos_safe.apps.api.schemas import HealthResponse
from chronos_safe.apps.api.web_ui import build_catalog_payload, render_dashboard_html
from chronos_safe.config.settings import SETTINGS
from chronos_safe.version import __version__

STATIC_DIR = Path(__file__).with_name("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    _ensure_runtime_directories()
    yield

app = FastAPI(
    title="CHRONOS-SAFE",
    version=__version__,
    description=(
        "Plataforma hibrida de simulacao orbital com motor fisico, correcao residual por IA, "
        "validacao Apophis e fallback seguro."
    ),
    lifespan=lifespan,
)
app.include_router(data_router)
app.include_router(training_router)
app.include_router(simulation_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(render_dashboard_html())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/ui/catalog")
def ui_catalog() -> dict[str, object]:
    return build_catalog_payload()
