"""Shared Jinja2 template configuration for the web UI."""

from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = TEMPLATES_DIR.parent / "static"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _static_version(path: str) -> int:
    target = STATIC_DIR / path
    try:
        return int(target.stat().st_mtime)
    except OSError:
        return 0


templates.env.globals["static_version"] = _static_version
