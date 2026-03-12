"""Plotting and report summary helpers."""

from __future__ import annotations

from pathlib import Path


def write_validation_summary(path: str | Path, report: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "CHRONOS-SAFE Apophis Validation Summary",
        f"Fixture: {report['fixture_name']}",
        f"Steps: {report['steps']}",
        f"dt_days: {report['dt_days']}",
        f"Fallback count: {report['fallback_count']}",
        f"Comparison metrics: {report['comparison_metrics']}",
        f"Hybrid metrics: {report['hybrid_metrics']}",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
