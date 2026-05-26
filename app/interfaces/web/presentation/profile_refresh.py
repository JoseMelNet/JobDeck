"""Refresh contract for HTMX interactions inside Perfil Laboral."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.interfaces.web.presentation.profile_view_model import ProfileSectionId


class ProfileRefreshAction(str, Enum):
    BASICS = "basics"
    SKILLS = "skills"
    EXPERIENCES = "experiences"
    PROJECTS = "projects"
    CREDENTIALS = "credentials"


@dataclass(frozen=True)
class ProfileRefreshPlan:
    action: ProfileRefreshAction
    primary_template: str
    redirect_section: ProfileSectionId
    refresh_summary: bool
    refresh_signals: bool
    refresh_cv_preview: bool


PROFILE_REFRESH_PLANS = {
    ProfileRefreshAction.BASICS: ProfileRefreshPlan(
        action=ProfileRefreshAction.BASICS,
        primary_template="profile/_basics.html",
        redirect_section=ProfileSectionId.OBJECTIVE,
        refresh_summary=True,
        # Transicional: Senales sigue montando _skills_shell, que hoy conserva
        # estado derivado del perfil y debe mantenerse sincronizado via HTMX.
        refresh_signals=True,
        refresh_cv_preview=True,
    ),
    ProfileRefreshAction.SKILLS: ProfileRefreshPlan(
        action=ProfileRefreshAction.SKILLS,
        primary_template="profile/_skills_shell.html",
        redirect_section=ProfileSectionId.SIGNALS,
        refresh_summary=True,
        refresh_signals=False,
        refresh_cv_preview=True,
    ),
    ProfileRefreshAction.EXPERIENCES: ProfileRefreshPlan(
        action=ProfileRefreshAction.EXPERIENCES,
        primary_template="profile/_experiences_shell.html",
        redirect_section=ProfileSectionId.EVIDENCE,
        refresh_summary=True,
        # Transicional: el shell de Senales aun comparte dependencias derivadas
        # con Resumen y debe refrescarse hasta separar esos acoplamientos.
        refresh_signals=True,
        refresh_cv_preview=True,
    ),
    ProfileRefreshAction.PROJECTS: ProfileRefreshPlan(
        action=ProfileRefreshAction.PROJECTS,
        primary_template="profile/_projects_shell.html",
        redirect_section=ProfileSectionId.EVIDENCE,
        refresh_summary=True,
        # Transicional: proyectos no cambian skills, pero Senales sigue siendo
        # un punto de montaje heredado para estado derivado del perfil.
        refresh_signals=True,
        refresh_cv_preview=False,
    ),
    ProfileRefreshAction.CREDENTIALS: ProfileRefreshPlan(
        action=ProfileRefreshAction.CREDENTIALS,
        primary_template="profile/_formation_shell.html",
        redirect_section=ProfileSectionId.CREDENTIALS,
        refresh_summary=True,
        # Transicional: mantener Senales al dia evita desfasar el estado
        # compartido mientras Resumen y Skills sigan acoplados via shell.
        refresh_signals=True,
        refresh_cv_preview=True,
    ),
}


def build_profile_refresh_plan(action: ProfileRefreshAction) -> ProfileRefreshPlan:
    return PROFILE_REFRESH_PLANS[action]


__all__ = [
    "PROFILE_REFRESH_PLANS",
    "ProfileRefreshAction",
    "ProfileRefreshPlan",
    "build_profile_refresh_plan",
]
