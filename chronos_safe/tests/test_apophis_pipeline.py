from pathlib import Path

from chronos_safe.simulation.mission_apophis import ApophisValidationConfig, run_apophis_validation


def test_apophis_pipeline_generates_report(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    report = run_apophis_validation(ApophisValidationConfig(steps=5, dt_days=1.0, report_dir=report_dir))
    assert "comparison_metrics" in report
    assert "benchmark" in report
    assert (report_dir / "apophis_validation.json").exists()
    assert (report_dir / "apophis_validation_summary.txt").exists()
