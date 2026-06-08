"""Presentation helpers for the Evidence section of Perfil Laboral."""

from __future__ import annotations

from dataclasses import dataclass


def _has_text(value) -> bool:
    return bool(value and str(value).strip())


@dataclass(frozen=True)
class ProfileExperienceEvidenceSummary:
    total: int
    current_count: int
    with_functions_count: int
    with_logros_count: int
    without_substance_count: int


@dataclass(frozen=True)
class ProfileProjectEvidenceSummary:
    total: int
    current_count: int
    with_stack_count: int
    with_functions_count: int
    with_logros_count: int
    without_substance_count: int


@dataclass(frozen=True)
class ProfileEvidenceInventory:
    total_items: int
    experiences: ProfileExperienceEvidenceSummary
    projects: ProfileProjectEvidenceSummary
    alerts: tuple[str, ...]
    summary: str
    is_empty: bool


def build_profile_evidence_inventory(
    experiences: list[dict],
    projects: list[dict],
) -> ProfileEvidenceInventory:
    experience_summary = ProfileExperienceEvidenceSummary(
        total=len(experiences),
        current_count=sum(1 for item in experiences if item.get("es_trabajo_actual")),
        with_functions_count=sum(1 for item in experiences if _has_text(item.get("funciones"))),
        with_logros_count=sum(1 for item in experiences if _has_text(item.get("logros"))),
        without_substance_count=sum(
            1 for item in experiences if not _has_text(item.get("funciones")) and not _has_text(item.get("logros"))
        ),
    )

    project_summary = ProfileProjectEvidenceSummary(
        total=len(projects),
        current_count=sum(1 for item in projects if item.get("es_proyecto_actual")),
        with_stack_count=sum(1 for item in projects if _has_text(item.get("stack"))),
        with_functions_count=sum(1 for item in projects if _has_text(item.get("funciones"))),
        with_logros_count=sum(1 for item in projects if _has_text(item.get("logros"))),
        without_substance_count=sum(
            1 for item in projects if not _has_text(item.get("funciones")) and not _has_text(item.get("logros"))
        ),
    )

    is_empty = experience_summary.total == 0 and project_summary.total == 0
    alerts: list[str] = []

    if is_empty:
        alerts.append("Aun no hay evidencia registrada para respaldar el perfil.")
    if experience_summary.total and experience_summary.without_substance_count:
        alerts.append(
            f"Hay {experience_summary.without_substance_count} experiencia(s) sin funciones ni logros."
        )
    if project_summary.total and project_summary.without_substance_count:
        alerts.append(
            f"Hay {project_summary.without_substance_count} proyecto(s) sin descripcion ni logros."
        )
    if project_summary.total and project_summary.with_stack_count < project_summary.total:
        alerts.append("Algunos proyectos aun no registran stack, lo que debilita la lectura tecnica.")
    if experience_summary.total == 0 and project_summary.total > 0:
        alerts.append("Hoy solo hay proyectos; sumar experiencia laboral daria mas contexto a la evidencia.")
    if experience_summary.total > 0 and project_summary.total == 0:
        alerts.append("Hoy solo hay experiencias; un proyecto relevante ampliaria la biblioteca de evidencia.")

    if is_empty:
        summary = "Todavia no existe una biblioteca de evidencia profesional en el perfil."
    else:
        summary = (
            f"{experience_summary.total} experiencia(s) y {project_summary.total} proyecto(s) "
            f"construyen la biblioteca actual de evidencia profesional."
        )

    return ProfileEvidenceInventory(
        total_items=experience_summary.total + project_summary.total,
        experiences=experience_summary,
        projects=project_summary,
        alerts=tuple(alerts[:4]),
        summary=summary,
        is_empty=is_empty,
    )


__all__ = [
    "ProfileEvidenceInventory",
    "ProfileExperienceEvidenceSummary",
    "ProfileProjectEvidenceSummary",
    "build_profile_evidence_inventory",
]
