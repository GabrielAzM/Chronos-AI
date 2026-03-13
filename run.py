"""Outer convenience launcher for the nested CHRONOS-SAFE project."""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent / "chronos_safe"
    project_run = project_root / "run.py"
    if not project_run.exists():
        raise FileNotFoundError(f"Expected CHRONOS-SAFE launcher at: {project_run}")

    os.chdir(project_root)
    sys.path.insert(0, str(project_root))
    runpy.run_path(str(project_run), run_name="__main__")


if __name__ == "__main__":
    main()
