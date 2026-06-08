"""Product-oriented quality summary for the Perfil Laboral workspace."""

from __future__ import annotations

from dataclasses import dataclass

from app.interfaces.web.presentation.profile_view_model import (
    ProfileSectionId,
    build_profile_labor_contract,
)


@dataclass(frozen=True)
class ProfileCoverageSummary:
    key: str
    title: str
    covered: int
    total: int
    percent: int
    tone: str
    summary: str
    gaps: tuple[str, ...]


@dataclass(frozen=True)
class ProfileNextAction:
    section_id: ProfileSectionId
    section_title: str
    title: str
    description: str


@dataclass(frozen=True)
class ProfileQualitySummary:
    overall_label: str
    overall_tone: str
    overall_percent: int
    overall_summary: str
    analysis_coverage: ProfileCoverageSummary
    cv_coverage: ProfileCoverageSummary
    evidence_coverage: ProfileCoverageSummary
    next_action: ProfileNextAction
    alerts: tuple[str, ...]
    future_notes: tuple[str, ...]


_SECTION_TITLES = {
    section.id: section.title
    for section in build_profile_labor_contract().sections
}


def _has_text(value) -> bool:
    return bool(value and str(value).strip())


def _has_positive_number(value) -> bool:
    try:
        return value is not None and value != "" and int(value) > 0
    except (TypeError, ValueError):
        return False


def _has_modalities(profile: dict | None) -> bool:
    if not profile:
        return False
    raw_value = profile.get("modalidades_aceptadas")
    if not raw_value:
        return False
    return any(part.strip() for part in str(raw_value).split(","))


def _has_salary_range(profile: dict | None) -> bool:
    if not profile:
        return False
    return _has_positive_number(profile.get("salario_min")) and _has_positive_number(profile.get("salario_max"))


def _formation_count(education: list[dict], courses: list[dict], certifications: list[dict]) -> int:
    return len(education) + len(courses) + len(certifications)


def _has_experience_detail(experiences: list[dict]) -> bool:
    return any(_has_text(item.get("funciones")) or _has_text(item.get("logros")) for item in experiences)


def _has_project_detail(projects: list[dict]) -> bool:
    return any(_has_text(item.get("funciones")) or _has_text(item.get("logros")) for item in projects)


def _build_coverage_summary(
    *,
    key: str,
    title: str,
    checks: tuple[tuple[str, bool], ...],
) -> ProfileCoverageSummary:
    covered = sum(1 for _, is_covered in checks if is_covered)
    total = len(checks)
    percent = int(round((covered / total) * 100)) if total else 0
    gaps = tuple(label for label, is_covered in checks if not is_covered)

    if percent >= 85:
        tone = "success"
        summary = "Cobertura solida para operar esta parte del perfil."
    elif percent >= 60:
        tone = "info"
        summary = "Base util, pero aun hay huecos que afectan consistencia."
    else:
        tone = "warning"
        summary = "Cobertura insuficiente para confiar del todo en esta salida."

    return ProfileCoverageSummary(
        key=key,
        title=title,
        covered=covered,
        total=total,
        percent=percent,
        tone=tone,
        summary=summary,
        gaps=gaps,
    )


def _section_title(section_id: ProfileSectionId) -> str:
    return _SECTION_TITLES[section_id]


def _build_next_action(
    *,
    profile: dict | None,
    skills: list[dict],
    experiences: list[dict],
    projects: list[dict],
    education: list[dict],
    courses: list[dict],
    certifications: list[dict],
) -> ProfileNextAction:
    if not _has_text(profile.get("titulo_profesional") if profile else None):
        return ProfileNextAction(
            section_id=ProfileSectionId.OBJECTIVE,
            section_title=_section_title(ProfileSectionId.OBJECTIVE),
            title="Define tu foco profesional",
            description="Completa titulo profesional para que el analisis y la estrategia partan de un objetivo claro.",
        )

    if not _has_text(profile.get("ciudad") if profile else None) or not _has_text(profile.get("nivel_actual") if profile else None):
        return ProfileNextAction(
            section_id=ProfileSectionId.OBJECTIVE,
            section_title=_section_title(ProfileSectionId.OBJECTIVE),
            title="Cierra tu contexto de busqueda",
            description="Agrega ciudad y nivel actual para mejorar filtros, matching y decisiones de postulacion.",
        )

    if not _has_salary_range(profile) or not _has_modalities(profile):
        return ProfileNextAction(
            section_id=ProfileSectionId.OBJECTIVE,
            section_title=_section_title(ProfileSectionId.OBJECTIVE),
            title="Aclara tus condiciones para aplicar",
            description="Completa rango salarial y modalidades aceptadas para evitar vacantes fuera de objetivo.",
        )

    if not skills:
        return ProfileNextAction(
            section_id=ProfileSectionId.SIGNALS,
            section_title=_section_title(ProfileSectionId.SIGNALS),
            title="Carga tus senales de afinidad",
            description="Registra skills con nivel para que el perfil pueda compararse mejor contra vacantes.",
        )

    if not experiences:
        return ProfileNextAction(
            section_id=ProfileSectionId.EVIDENCE,
            section_title=_section_title(ProfileSectionId.EVIDENCE),
            title="Agrega evidencia profesional",
            description="Suma al menos una experiencia para respaldar skills, analisis y futuras salidas.",
        )

    if not _has_experience_detail(experiences):
        return ProfileNextAction(
            section_id=ProfileSectionId.EVIDENCE,
            section_title=_section_title(ProfileSectionId.EVIDENCE),
            title="Convierte experiencia en evidencia util",
            description="Agrega funciones o logros a tus experiencias para reforzar analisis, CV y mensajes.",
        )

    if _formation_count(education, courses, certifications) == 0:
        return ProfileNextAction(
            section_id=ProfileSectionId.CREDENTIALS,
            section_title=_section_title(ProfileSectionId.CREDENTIALS),
            title="Refuerza tus credenciales",
            description="Suma educacion, cursos o certificaciones para dar soporte formal al perfil.",
        )

    if not _has_text(profile.get("correo") if profile else None) or not _has_text(
        profile.get("perfil_linkedin") if profile else None
    ):
        return ProfileNextAction(
            section_id=ProfileSectionId.OUTPUTS,
            section_title=_section_title(ProfileSectionId.OUTPUTS),
            title="Completa tus salidas base",
            description="Agrega correo y LinkedIn para dejar listo el perfil de cara al CV y la postulacion.",
        )

    if not projects:
        return ProfileNextAction(
            section_id=ProfileSectionId.EVIDENCE,
            section_title=_section_title(ProfileSectionId.EVIDENCE),
            title="Suma evidencia complementaria",
            description="Agrega un proyecto relevante para ampliar ejemplos concretos de impacto y herramientas.",
        )

    if not _has_project_detail(projects):
        return ProfileNextAction(
            section_id=ProfileSectionId.EVIDENCE,
            section_title=_section_title(ProfileSectionId.EVIDENCE),
            title="Profundiza tus proyectos",
            description="Documenta funciones o logros de proyecto para que sirvan como evidencia reusable.",
        )

    return ProfileNextAction(
        section_id=ProfileSectionId.OUTPUTS,
        section_title=_section_title(ProfileSectionId.OUTPUTS),
        title="Revisa tu salida base",
        description="Valida la vista CV y busca inconsistencias antes de usar el perfil en nuevas postulaciones.",
    )


def _build_alerts(
    *,
    profile: dict | None,
    skills: list[dict],
    experiences: list[dict],
    projects: list[dict],
    education: list[dict],
    courses: list[dict],
    certifications: list[dict],
) -> tuple[str, ...]:
    alerts: list[str] = []

    if not _has_text(profile.get("titulo_profesional") if profile else None):
        alerts.append("Falta titulo profesional, asi que el analisis arranca sin un objetivo claro.")
    if not _has_text(profile.get("ciudad") if profile else None):
        alerts.append("Falta ciudad, lo que debilita filtros de ubicacion y consistencia del CV.")
    if not _has_salary_range(profile):
        alerts.append("Falta rango salarial completo para decidir mejor que vacantes filtrar.")
    if not skills:
        alerts.append("No hay skills registradas, asi que la afinidad con vacantes sigue poco informada.")
    if not experiences:
        alerts.append("No hay experiencias registradas y hoy esa es la evidencia principal del perfil.")
    elif not _has_experience_detail(experiences):
        alerts.append("Hay experiencias sin funciones ni logros, por lo que la evidencia aun es superficial.")
    if _formation_count(education, courses, certifications) == 0:
        alerts.append("No hay credenciales registradas para respaldar el CV base.")
    if not _has_text(profile.get("correo") if profile else None):
        alerts.append("Falta correo y eso deja incompleta la salida base para postulaciones.")
    if not _has_text(profile.get("perfil_linkedin") if profile else None):
        alerts.append("Falta LinkedIn y eso reduce la calidad de la salida y la validacion del perfil.")
    if projects and not _has_project_detail(projects):
        alerts.append("Hay proyectos cargados, pero aun sin funciones o logros que los conviertan en evidencia.")

    return tuple(alerts[:5])


def build_profile_quality_summary(
    *,
    profile: dict | None,
    skills: list[dict],
    experiences: list[dict],
    projects: list[dict],
    education: list[dict],
    courses: list[dict],
    certifications: list[dict],
) -> ProfileQualitySummary:
    formation_registered = _formation_count(education, courses, certifications) > 0

    analysis_coverage = _build_coverage_summary(
        key="analysis",
        title="Cobertura para analisis",
        checks=(
            ("Titulo profesional", _has_text(profile.get("titulo_profesional") if profile else None)),
            ("Ciudad", _has_text(profile.get("ciudad") if profile else None)),
            ("Nivel actual", _has_text(profile.get("nivel_actual") if profile else None)),
            ("Anios de experiencia", _has_positive_number(profile.get("anos_experiencia") if profile else None)),
            ("Rango salarial", _has_salary_range(profile)),
            ("Modalidades aceptadas", _has_modalities(profile)),
            ("Skills registradas", len(skills) > 0),
            ("Experiencias registradas", len(experiences) > 0),
            ("Formacion registrada", formation_registered),
        ),
    )

    cv_coverage = _build_coverage_summary(
        key="cv",
        title="Cobertura para CV base",
        checks=(
            ("Nombre", _has_text(profile.get("nombre") if profile else None)),
            ("Titulo profesional", _has_text(profile.get("titulo_profesional") if profile else None)),
            ("Correo", _has_text(profile.get("correo") if profile else None)),
            ("Ciudad", _has_text(profile.get("ciudad") if profile else None)),
            ("LinkedIn", _has_text(profile.get("perfil_linkedin") if profile else None)),
            ("Skills", len(skills) > 0),
            ("Experiencias", len(experiences) > 0),
            ("Credenciales", formation_registered),
        ),
    )

    evidence_coverage = _build_coverage_summary(
        key="evidence",
        title="Cobertura de evidencia",
        checks=(
            ("Experiencias registradas", len(experiences) > 0),
            ("Experiencias con funciones o logros", _has_experience_detail(experiences)),
            ("Proyectos registrados", len(projects) > 0),
            ("Proyectos con funciones o logros", _has_project_detail(projects)),
        ),
    )

    total_covered = analysis_coverage.covered + cv_coverage.covered + evidence_coverage.covered
    total_possible = analysis_coverage.total + cv_coverage.total + evidence_coverage.total
    overall_percent = int(round((total_covered / total_possible) * 100)) if total_possible else 0

    if overall_percent >= 85:
        overall_label = "Perfil consistente"
        overall_tone = "success"
        overall_summary = "Ya tienes una base solida para analisis, CV y evidencia profesional."
    elif overall_percent >= 60:
        overall_label = "Base util"
        overall_tone = "info"
        overall_summary = "El perfil ya sirve para operar, pero todavia tiene huecos que afectan decision y salida."
    elif overall_percent >= 35:
        overall_label = "Cobertura inicial"
        overall_tone = "warning"
        overall_summary = "La base existe, aunque aun faltan piezas clave para confiar en el perfil."
    else:
        overall_label = "Perfil incompleto"
        overall_tone = "warning"
        overall_summary = "Todavia faltan datos esenciales para usar este perfil como fuente de verdad."

    return ProfileQualitySummary(
        overall_label=overall_label,
        overall_tone=overall_tone,
        overall_percent=overall_percent,
        overall_summary=overall_summary,
        analysis_coverage=analysis_coverage,
        cv_coverage=cv_coverage,
        evidence_coverage=evidence_coverage,
        next_action=_build_next_action(
            profile=profile,
            skills=skills,
            experiences=experiences,
            projects=projects,
            education=education,
            courses=courses,
            certifications=certifications,
        ),
        alerts=_build_alerts(
            profile=profile,
            skills=skills,
            experiences=experiences,
            projects=projects,
            education=education,
            courses=courses,
            certifications=certifications,
        ),
        future_notes=(
            "La calidad actual no calcula relacion entre skills y evidencia porque esa asociacion aun no existe.",
            "Los proyectos hoy cuentan como evidencia visual, pero todavia no alimentan analisis de vacantes ni CV base.",
        ),
    )


__all__ = [
    "ProfileCoverageSummary",
    "ProfileNextAction",
    "ProfileQualitySummary",
    "build_profile_quality_summary",
]
