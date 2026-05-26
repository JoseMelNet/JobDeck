"""Presentation helpers for the web UI."""

from app.interfaces.web.presentation.profile_quality import build_profile_quality_summary
from app.interfaces.web.presentation.profile_view_model import build_profile_labor_contract

__all__ = ["build_profile_labor_contract", "build_profile_quality_summary"]
