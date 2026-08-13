"""Backward-compatible Zeabur entrypoint that runs Ombre Brain only."""

from __future__ import annotations

from pathlib import Path
import runpy


runpy.run_path(str(Path(__file__).with_name("server.py")), run_name="__main__")
