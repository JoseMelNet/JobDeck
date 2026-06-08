"""Presentation helpers for the Outputs section of Perfil Laboral."""

from __future__ import annotations

from dataclasses import dataclass


def _has_text(value) -> bool:
    return bool(value and str(value).strip())


@dataclass(frozen=True)
class ProfileOutputContactSummary:
    ready_count: int
    total_count: int
    has_name: bool
    has_email: bool
    has_city: bool
    has_phone: bool
    has_linkedin: bool
    has_github: bool


@dataclass(frozen=True)
class ProfileBaseCvOutputSummary:
    is_renderable: bool
    ready_count: int
    total_count: int
    has_name: bool
    has_title: bool
    has_email: bool
    has_linkedin: bool
    has_city: bool
    has_phone: bool
    has_skills: bool
    has_experiences: bool
    has_credentials: bool
    has_dedicated_summary: bool
    uses_title_as_summary: bool


@dataclass(frozen=True)
class ProfileOutputsInventory:
    contact: ProfileOutputContactSummary
    cv_base: ProfileBaseCvOutputSummary
    alerts: tuple[str, ...]
    limits: tuple[str, ...]
    summary: str
    is_empty: bool


def build_profile_outputs_inventory(
    *,
    profile: dict | None,
    skills: list[dict],
    experiences: list[dict],
    education: list[dict],
    courses: list[dict],
    certifications: list[dict],
    cv_preview_html: str | None,
) -> ProfileOutputsInventory:
    has_name = _has_text(profile.get("nombre")) if profile else False
    has_title = _has_text(profile.get("titulo_profesional")) if profile else False
    has_email = _has_text(profile.get("correo")) if profile else False
    has_city = _has_text(profile.get("ciudad")) if profile else False
    has_phone = _has_text(profile.get("celular")) if profile else False
    has_linkedin = _has_text(profile.get("perfil_linkedin")) if profile else False
    has_github = _has_text(profile.get("perfil_github")) if profile else False

    has_skills = bool(skills)
    has_experiences = bool(experiences)
    has_credentials = bool(education or courses or certifications)
    has_dedicated_summary = False
    uses_title_as_summary = has_title and not has_dedicated_summary

    contact = ProfileOutputContactSummary(
        ready_count=sum([has_name, has_email, has_city, has_phone, has_linkedin, has_github]),
        total_count=6,
        has_name=has_name,
        has_email=has_email,
        has_city=has_city,
        has_phone=has_phone,
        has_linkedin=has_linkedin,
        has_github=has_github,
    )
    cv_base = ProfileBaseCvOutputSummary(
        is_renderable=bool(cv_preview_html),
        ready_count=sum(
            [has_name, has_title, has_email, has_linkedin, has_city, has_phone, has_skills, has_experiences, has_credentials]
        ),
        total_count=9,
        has_name=has_name,
        has_title=has_title,
        has_email=has_email,
        has_linkedin=has_linkedin,
        has_city=has_city,
        has_phone=has_phone,
        has_skills=has_skills,
        has_experiences=has_experiences,
        has_credentials=has_credentials,
        has_dedicated_summary=has_dedicated_summary,
        uses_title_as_summary=uses_title_as_summary,
    )

    is_empty = not profile and not has_skills and not has_experiences and not has_credentials
    alerts: list[str] = []
    limits: list[str] = []

    if is_empty:
        alerts.append("Aun no hay datos suficientes para producir salidas reutilizables desde el perfil.")
    if profile and not (has_name and has_email):
        alerts.append("Faltan datos de contacto base para reutilizar mejor el perfil en postulaciones.")
    if cv_base.is_renderable and not has_experiences:
        alerts.append("El CV base aun no muestra experiencia laboral registrada.")
    if cv_base.is_renderable and not has_skills:
        alerts.append("El CV base aun no refleja skills registradas.")
    if cv_base.is_renderable and not has_credentials:
        alerts.append("El CV base aun no cuenta con soporte academico o certificaciones.")

    if uses_title_as_summary:
        limits.append("El resumen profesional actual reutiliza el titulo profesional; aun no existe un resumen dedicado.")
    elif cv_base.is_renderable and not has_dedicated_summary:
        limits.append("El CV base aun no tiene un resumen profesional dedicado.")
    if has_github:
        limits.append("GitHub esta disponible como dato de salida, pero la vista CV base actual aun no lo muestra.")
    limits.append("CV adaptado, cartas y mensajes todavia no estan implementados en esta seccion.")

    if is_empty:
        summary = "Todavia no hay una salida reusable lista para revisar o compartir desde el perfil."
    elif cv_base.is_renderable:
        summary = "Hoy el perfil ya puede producir un CV base y reutilizar datos de contacto para futuras aplicaciones."
    else:
        summary = "Ya hay datos de salida parciales, pero todavia no alcanza para una vista CV base legible."

    return ProfileOutputsInventory(
        contact=contact,
        cv_base=cv_base,
        alerts=tuple(alerts[:4]),
        limits=tuple(limits[:4]),
        summary=summary,
        is_empty=is_empty,
    )


__all__ = [
    "ProfileBaseCvOutputSummary",
    "ProfileOutputContactSummary",
    "ProfileOutputsInventory",
    "build_profile_outputs_inventory",
]
