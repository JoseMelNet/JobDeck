"""HTML routes for the profile page."""

from __future__ import annotations

from datetime import date
from html import escape
from urllib.parse import urlencode

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.interfaces.web.presentation.profile_quality import build_profile_quality_summary
from app.interfaces.web.presentation.profile_refresh import (
    ProfileRefreshAction,
    build_profile_refresh_plan,
)
from app.interfaces.web.presentation.profile_signals import build_profile_signals_inventory
from app.interfaces.web.presentation.profile_view_model import (
    ProfileSectionId,
    build_profile_labor_contract,
)
from app.interfaces.web.routes.dashboard import _build_metrics, _build_nav
from app.interfaces.web.templates import templates

router = APIRouter(tags=["web-profile"])

profile_repository = ProfileRepository()
profile_labor_contract = build_profile_labor_contract()

LEVEL_OPTIONS = ["Junior", "Mid", "Senior", "Lead"]
MODALITY_OPTIONS = ["Remoto", "Hibrido", "Presencial"]
SKILL_LEVEL_OPTIONS = ["Basico", "Intermedio", "Avanzado", "Experto"]
EDUCATION_LEVEL_OPTIONS = ["Tecnico", "Tecnologo", "Pregrado", "Especializacion", "Maestria", "Doctorado"]
EDUCATION_STATUS_OPTIONS = ["En curso", "Completado", "Pausado"]
COURSE_STATUS_OPTIONS = ["Planeado", "En curso", "Completado"]
CERTIFICATION_STATUS_OPTIONS = ["Vigente", "Vencida", "En proceso"]
PROFILE_SECTION_TEMPLATE_MAP = {
    ProfileSectionId.SUMMARY.value: "profile/_summary_section.html",
    ProfileSectionId.OBJECTIVE.value: "profile/_objective_section.html",
    ProfileSectionId.SIGNALS.value: "profile/_signals_section.html",
    ProfileSectionId.EVIDENCE.value: "profile/_evidence_section.html",
    ProfileSectionId.CREDENTIALS.value: "profile/_credentials_section.html",
    ProfileSectionId.OUTPUTS.value: "profile/_outputs_section.html",
}

PROFILE_ACTION_REDIRECTS = {
    ProfileRefreshAction.BASICS: build_profile_refresh_plan(ProfileRefreshAction.BASICS).redirect_section,
    ProfileRefreshAction.SKILLS: build_profile_refresh_plan(ProfileRefreshAction.SKILLS).redirect_section,
    ProfileRefreshAction.EXPERIENCES: build_profile_refresh_plan(ProfileRefreshAction.EXPERIENCES).redirect_section,
    ProfileRefreshAction.PROJECTS: build_profile_refresh_plan(ProfileRefreshAction.PROJECTS).redirect_section,
    ProfileRefreshAction.CREDENTIALS: build_profile_refresh_plan(ProfileRefreshAction.CREDENTIALS).redirect_section,
}


def _build_flash_message(flash: str | None) -> tuple[str, str] | None:
    if flash == "profile_saved":
        return ("success", "Los datos principales del perfil fueron guardados.")
    if flash == "skill_added":
        return ("success", "La skill fue agregada al perfil.")
    if flash == "skill_deleted":
        return ("success", "La skill fue eliminada.")
    if flash == "experience_saved":
        return ("success", "La experiencia fue guardada.")
    if flash == "experience_deleted":
        return ("success", "La experiencia fue eliminada.")
    if flash == "project_saved":
        return ("success", "El proyecto fue guardado.")
    if flash == "project_deleted":
        return ("success", "El proyecto fue eliminado.")
    if flash == "education_saved":
        return ("success", "La educacion fue guardada.")
    if flash == "education_deleted":
        return ("success", "La educacion fue eliminada.")
    if flash == "course_saved":
        return ("success", "El curso fue guardado.")
    if flash == "course_deleted":
        return ("success", "El curso fue eliminado.")
    if flash == "certification_saved":
        return ("success", "La certificacion fue guardada.")
    if flash == "certification_deleted":
        return ("success", "La certificacion fue eliminada.")
    if flash == "profile_error":
        return ("warning", "No se pudo completar la accion sobre el perfil.")
    return None


def _format_modalities(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    items = []
    for item in raw_value.split(","):
        normalized = item.strip()
        if not normalized:
            continue
        if normalized == "Híbrido":
            normalized = "Hibrido"
        items.append(normalized)
    return items


def _fmt_month_year(value) -> str:
    if not value:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%m/%Y")
    return str(value)


def _resolve_profile_section(section: str | None) -> str:
    requested = (section or ProfileSectionId.SUMMARY.value).strip().lower()
    valid_sections = {item.id.value for item in profile_labor_contract.sections}
    if requested in valid_sections:
        return requested
    return ProfileSectionId.SUMMARY.value


def _build_profile_url(*, section: str | None = None, flash: str | None = None, shell: bool = False) -> str:
    params: list[tuple[str, str]] = []
    resolved_section = _resolve_profile_section(section)
    if resolved_section != ProfileSectionId.SUMMARY.value:
        params.append(("section", resolved_section))
    if flash:
        params.append(("flash", flash))

    base_path = "/app/profile/shell" if shell else "/app/profile"
    return base_path + (f"?{urlencode(params)}" if params else "")


def _build_profile_redirect_url(*, action: ProfileRefreshAction, flash: str | None = None) -> str:
    return _build_profile_url(section=PROFILE_ACTION_REDIRECTS[action].value, flash=flash)


def _build_profile_sections(active_section: str) -> list[dict[str, str | bool]]:
    return [
        {
            "id": item.id.value,
            "title": item.title,
            "summary": item.summary,
            "href": _build_profile_url(section=item.id.value),
            "shell_href": _build_profile_url(section=item.id.value, shell=True),
            "active": item.id.value == active_section,
        }
        for item in profile_labor_contract.sections
    ]


def _build_cv_preview(profile, skills, experiences, education, courses, certifications) -> str | None:
    if not profile:
        return None

    nombre = escape((profile.get("nombre") or "").upper())
    titulo = escape(profile.get("titulo_profesional") or "")
    contacto = []
    if profile.get("correo"):
        contacto.append(escape(profile["correo"]))
    if profile.get("perfil_linkedin"):
        linkedin = escape(profile["perfil_linkedin"])
        contacto.append(f'<a href="{linkedin}" target="_blank" rel="noreferrer">{linkedin}</a>')
    if profile.get("ciudad"):
        contacto.append(escape(profile["ciudad"]))
    if profile.get("celular"):
        contacto.append(escape(profile["celular"]))

    parts = [
        '<div class="cv-preview">',
        '<header class="cv-preview-header">',
        f'<div class="cv-preview-name">{nombre or "PERFIL PROFESIONAL"}</div>',
        f'<div class="cv-preview-title">{titulo or "Perfil sin titulo"}</div>',
        f'<div class="cv-preview-contact">{" · ".join(contacto) if contacto else "Completa tus datos de contacto"}</div>',
        "</header>",
    ]

    parts.append('<section class="cv-preview-section"><h3>Resumen profesional</h3>')
    parts.append(f"<p>{titulo or 'Completa tu perfil para generar una mejor vista CV.'}</p></section>")

    if skills:
        parts.append('<section class="cv-preview-section"><h3>Habilidades</h3><div class="cv-preview-list">')
        grouped = {}
        for item in skills:
            grouped.setdefault(item["categoria"], []).append(item["skill"])
        for category, values in grouped.items():
            parts.append(
                f'<div class="cv-preview-row"><strong>{escape(category)}:</strong> '
                f'{" · ".join(escape(value) for value in values)}</div>'
            )
        parts.append("</div></section>")

    if experiences:
        parts.append('<section class="cv-preview-section"><h3>Experiencia laboral</h3>')
        for item in experiences:
            period_end = "Actualidad" if item["es_trabajo_actual"] else _fmt_month_year(item["fecha_fin"])
            parts.append('<article class="cv-preview-item">')
            parts.append(
                f'<div class="cv-preview-item-head"><strong>{escape(item["cargo"])}</strong>'
                f"<span>{_fmt_month_year(item['fecha_inicio'])} - {period_end}</span></div>"
            )
            parts.append(f'<div class="cv-preview-sub">{escape(item["empresa"])}')
            if item.get("ciudad"):
                parts.append(f" · {escape(item['ciudad'])}")
            parts.append("</div>")
            for block in [item.get("funciones"), item.get("logros")]:
                if block:
                    for line in str(block).splitlines():
                        clean = escape(line.lstrip("?- ").strip())
                        if clean:
                            parts.append(f"<div class='cv-preview-bullet'>{clean}</div>")
            parts.append("</article>")
        parts.append("</section>")

    if education or certifications or courses:
        parts.append('<section class="cv-preview-section"><h3>Educacion y formacion</h3>')
        for item in education:
            end_label = _fmt_month_year(item["fecha_fin"]) if item["fecha_fin"] else escape(item["status"])
            parts.append(
                f"<div class='cv-preview-row'><strong>{escape(item['titulo'])}</strong> · "
                f"{escape(item['institucion'])} · {escape(item['nivel'])} "
                f"<span>{_fmt_month_year(item['fecha_inicio'])} - {end_label}</span></div>"
            )
        for item in certifications:
            parts.append(
                f"<div class='cv-preview-row'><strong>{escape(item['titulo'])}</strong> · "
                f"{escape(item['institucion'])} <span>{_fmt_month_year(item['fecha_obtencion'])} · {escape(item['status'])}</span></div>"
            )
        if courses:
            parts.append("<div class='cv-preview-row'><strong>Cursos:</strong> ")
            parts.append(" · ".join(escape(item["titulo"]) for item in courses))
            parts.append("</div>")
        parts.append("</section>")

    parts.append("</div>")
    return "".join(parts)


def _build_profile_context(flash: str | None = None, section: str | None = None) -> dict:
    profile = profile_repository.get_active_profile()
    perfil_id = profile["id"] if profile else None

    skills = profile_repository.get_skills(perfil_id) if perfil_id else []
    experiences = profile_repository.get_experiences(perfil_id) if perfil_id else []
    projects = profile_repository.get_projects(perfil_id) if perfil_id else []
    education = profile_repository.get_education(perfil_id) if perfil_id else []
    courses = profile_repository.get_courses(perfil_id) if perfil_id else []
    certifications = profile_repository.get_certifications(perfil_id) if perfil_id else []

    selected_modalities = _format_modalities(profile.get("modalidades_aceptadas")) if profile else []
    active_section = _resolve_profile_section(section)
    active_section_definition = next(item for item in profile_labor_contract.sections if item.id.value == active_section)
    profile_quality = build_profile_quality_summary(
        profile=profile,
        skills=skills,
        experiences=experiences,
        projects=projects,
        education=education,
        courses=courses,
        certifications=certifications,
    )
    profile_signals = build_profile_signals_inventory(skills)

    return {
        "profile": profile,
        "skills": skills,
        "experiences": experiences,
        "projects": projects,
        "education": education,
        "courses": courses,
        "certifications": certifications,
        "flash_message": _build_flash_message(flash),
        "level_options": LEVEL_OPTIONS,
        "modality_options": MODALITY_OPTIONS,
        "selected_modalities": selected_modalities,
        "skill_level_options": SKILL_LEVEL_OPTIONS,
        "education_level_options": EDUCATION_LEVEL_OPTIONS,
        "education_status_options": EDUCATION_STATUS_OPTIONS,
        "course_status_options": COURSE_STATUS_OPTIONS,
        "certification_status_options": CERTIFICATION_STATUS_OPTIONS,
        "cv_preview_html": _build_cv_preview(profile, skills, experiences, education, courses, certifications),
        "profile_quality": profile_quality,
        "profile_signals": profile_signals,
        "profile_quality_action_href": _build_profile_url(section=profile_quality.next_action.section_id.value),
        "profile_sections": _build_profile_sections(active_section),
        "active_profile_section": active_section_definition,
        "active_profile_section_id": active_section,
        "active_profile_section_template": PROFILE_SECTION_TEMPLATE_MAP[active_section],
    }


def _render_profile_shell(request: Request, flash: str, section: str | None = None):
    context = _build_profile_context(flash=flash, section=section)
    return templates.TemplateResponse(
        request=request,
        name="profile/_shell.html",
        context={"request": request, **context},
    )


def _render_profile_refresh_response(
    request: Request,
    *,
    flash: str,
    action: ProfileRefreshAction,
):
    context = _build_profile_context(flash=flash)
    refresh_plan = build_profile_refresh_plan(action)
    return templates.TemplateResponse(
        request=request,
        name="profile/_refresh_response.html",
        context={
            "request": request,
            **context,
            "refresh_plan": refresh_plan,
            "skills_flash_message": context["flash_message"] if action == ProfileRefreshAction.SKILLS and flash else None,
            "basics_flash_message": context["flash_message"] if action == ProfileRefreshAction.BASICS and flash else None,
            "formation_flash_message": (
                context["flash_message"] if action == ProfileRefreshAction.CREDENTIALS and flash else None
            ),
            "projects_flash_message": context["flash_message"] if action == ProfileRefreshAction.PROJECTS and flash else None,
            "experiences_flash_message": (
                context["flash_message"] if action == ProfileRefreshAction.EXPERIENCES and flash else None
            ),
        },
    )


def _render_profile_skills_shell(request: Request, flash: str = "", include_oob: bool = False):
    if include_oob:
        return _render_profile_refresh_response(request, flash=flash, action=ProfileRefreshAction.SKILLS)

    context = _build_profile_context(flash=flash)
    return templates.TemplateResponse(
        request=request,
        name="profile/_skills_shell.html",
        context={
            "request": request,
            **context,
            "skills_flash_message": context["flash_message"] if flash else None,
        },
    )


def _render_profile_basics_shell(request: Request, flash: str = "", include_oob: bool = False):
    if include_oob:
        return _render_profile_refresh_response(request, flash=flash, action=ProfileRefreshAction.BASICS)

    context = _build_profile_context(flash=flash)
    return templates.TemplateResponse(
        request=request,
        name="profile/_basics.html",
        context={
            "request": request,
            **context,
            "basics_flash_message": context["flash_message"] if flash else None,
        },
    )


def _render_profile_formation_shell(request: Request, flash: str = "", include_oob: bool = False):
    if include_oob:
        return _render_profile_refresh_response(request, flash=flash, action=ProfileRefreshAction.CREDENTIALS)

    context = _build_profile_context(flash=flash)
    return templates.TemplateResponse(
        request=request,
        name="profile/_formation_shell.html",
        context={
            "request": request,
            **context,
            "formation_flash_message": context["flash_message"] if flash else None,
        },
    )


def _render_profile_projects_shell(request: Request, flash: str = "", include_oob: bool = False):
    if include_oob:
        return _render_profile_refresh_response(request, flash=flash, action=ProfileRefreshAction.PROJECTS)

    context = _build_profile_context(flash=flash)
    return templates.TemplateResponse(
        request=request,
        name="profile/_projects_shell.html",
        context={
            "request": request,
            **context,
            "projects_flash_message": context["flash_message"] if flash else None,
        },
    )


def _render_profile_experiences_shell(request: Request, flash: str = "", include_oob: bool = False):
    if include_oob:
        return _render_profile_refresh_response(request, flash=flash, action=ProfileRefreshAction.EXPERIENCES)

    context = _build_profile_context(flash=flash)
    return templates.TemplateResponse(
        request=request,
        name="profile/_experiences_shell.html",
        context={
            "request": request,
            **context,
            "experiences_flash_message": context["flash_message"] if flash else None,
        },
    )


@router.get("/app/profile")
def profile_index(request: Request, flash: str | None = None, section: str | None = None):
    context = _build_profile_context(flash=flash, section=section)
    return templates.TemplateResponse(
        request=request,
        name="profile/index.html",
        context={
            "page_title": "Perfil Laboral",
            "active_nav": "profile",
            "nav_items": _build_nav("profile"),
            "metrics": _build_metrics(),
            **context,
        },
    )


@router.get("/app/profile/shell", response_class=HTMLResponse)
def profile_shell_partial(request: Request, flash: str | None = None, section: str | None = None):
    return _render_profile_shell(request, flash or "", section=section)


@router.get("/app/profile/skills", response_class=HTMLResponse)
def profile_skills_partial(request: Request, flash: str | None = None):
    return _render_profile_skills_shell(request, flash or "")


@router.get("/app/profile/basics", response_class=HTMLResponse)
def profile_basics_partial(request: Request, flash: str | None = None):
    return _render_profile_basics_shell(request, flash or "")


@router.get("/app/profile/formation", response_class=HTMLResponse)
def profile_formation_partial(request: Request, flash: str | None = None):
    return _render_profile_formation_shell(request, flash or "")


@router.get("/app/profile/projects", response_class=HTMLResponse)
def profile_projects_partial(request: Request, flash: str | None = None):
    return _render_profile_projects_shell(request, flash or "")


@router.get("/app/profile/experiences", response_class=HTMLResponse)
def profile_experiences_partial(request: Request, flash: str | None = None):
    return _render_profile_experiences_shell(request, flash or "")


@router.post("/app/profile/save")
def save_profile(
    request: Request,
    nombre: str | None = Form(default=None),
    titulo_profesional: str | None = Form(default=None),
    ciudad: str | None = Form(default=None),
    direccion: str | None = Form(default=None),
    celular: str | None = Form(default=None),
    correo: str | None = Form(default=None),
    perfil_linkedin: str | None = Form(default=None),
    perfil_github: str | None = Form(default=None),
    nivel_actual: str = Form(default="Mid"),
    anos_experiencia: int = Form(default=0),
    salario_min: int | None = Form(default=None),
    salario_max: int | None = Form(default=None),
    moneda: str = Form(default="COP"),
    modalidades_aceptadas: list[str] = Form(default=[]),
):
    result = profile_repository.save_profile(
        {
            "nombre": nombre,
            "titulo_profesional": titulo_profesional,
            "ciudad": ciudad,
            "direccion": direccion,
            "celular": celular,
            "correo": correo,
            "perfil_linkedin": perfil_linkedin,
            "perfil_github": perfil_github,
            "nivel_actual": nivel_actual,
            "anos_experiencia": anos_experiencia,
            "salario_min": salario_min,
            "salario_max": salario_max,
            "moneda": moneda,
            "modalidades_aceptadas": ",".join(modalidades_aceptadas) or "Remoto,Hibrido,Presencial",
        }
    )
    flash = "profile_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_basics_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.BASICS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/skills")
def add_skill(
    request: Request,
    categoria: str = Form(...),
    skill: str = Form(...),
    nivel: str = Form(...),
):
    profile = profile_repository.get_active_profile()
    if not profile:
        flash = "profile_error"
    else:
        result = profile_repository.add_skill(profile["id"], categoria, skill, nivel)
        flash = "skill_added" if result["success"] else "profile_error"

    if request.headers.get("HX-Request") == "true":
        return _render_profile_skills_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.SKILLS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/skills/{skill_id}/delete")
def delete_skill(request: Request, skill_id: int):
    result = profile_repository.delete_skill(skill_id)
    flash = "skill_deleted" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_skills_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.SKILLS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/experiences")
def add_experience(
    request: Request,
    cargo: str = Form(...),
    empresa: str = Form(...),
    ciudad: str | None = Form(default=None),
    descripcion_empresa: str | None = Form(default=None),
    fecha_inicio: date = Form(...),
    fecha_fin: date | None = Form(default=None),
    es_trabajo_actual: bool = Form(default=False),
    funciones: str | None = Form(default=None),
    logros: str | None = Form(default=None),
):
    profile = profile_repository.get_active_profile()
    if not profile:
        flash = "profile_error"
    else:
        result = profile_repository.add_experience(
            profile["id"],
            {
                "cargo": cargo,
                "empresa": empresa,
                "ciudad": ciudad,
                "descripcion_empresa": descripcion_empresa,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "es_trabajo_actual": es_trabajo_actual,
                "funciones": funciones,
                "logros": logros,
            },
        )
        flash = "experience_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_experiences_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.EXPERIENCES, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/experiences/{experience_id}/update")
def update_experience(
    request: Request,
    experience_id: int,
    cargo: str = Form(...),
    empresa: str = Form(...),
    ciudad: str | None = Form(default=None),
    descripcion_empresa: str | None = Form(default=None),
    fecha_inicio: date = Form(...),
    fecha_fin: date | None = Form(default=None),
    es_trabajo_actual: bool = Form(default=False),
    funciones: str | None = Form(default=None),
    logros: str | None = Form(default=None),
):
    result = profile_repository.update_experience(
        experience_id,
        {
            "cargo": cargo,
            "empresa": empresa,
            "ciudad": ciudad,
            "descripcion_empresa": descripcion_empresa,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "es_trabajo_actual": es_trabajo_actual,
            "funciones": funciones,
            "logros": logros,
        },
    )
    flash = "experience_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_experiences_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.EXPERIENCES, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/experiences/{experience_id}/delete")
def delete_experience(request: Request, experience_id: int):
    result = profile_repository.delete_experience(experience_id)
    flash = "experience_deleted" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_experiences_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.EXPERIENCES, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/projects")
def add_project(
    request: Request,
    nombre: str = Form(...),
    empresa: str | None = Form(default=None),
    ciudad: str | None = Form(default=None),
    fecha_inicio: date = Form(...),
    fecha_fin: date | None = Form(default=None),
    es_proyecto_actual: bool = Form(default=False),
    stack: str | None = Form(default=None),
    funciones: str | None = Form(default=None),
    logros: str | None = Form(default=None),
    url_repositorio: str | None = Form(default=None),
):
    profile = profile_repository.get_active_profile()
    if not profile:
        flash = "profile_error"
    else:
        result = profile_repository.add_project(
            profile["id"],
            {
                "nombre": nombre,
                "empresa": empresa,
                "ciudad": ciudad,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "es_proyecto_actual": es_proyecto_actual,
                "stack": stack,
                "funciones": funciones,
                "logros": logros,
                "url_repositorio": url_repositorio,
            },
        )
        flash = "project_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_projects_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.PROJECTS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/projects/{project_id}/update")
def update_project(
    request: Request,
    project_id: int,
    nombre: str = Form(...),
    empresa: str | None = Form(default=None),
    ciudad: str | None = Form(default=None),
    fecha_inicio: date = Form(...),
    fecha_fin: date | None = Form(default=None),
    es_proyecto_actual: bool = Form(default=False),
    stack: str | None = Form(default=None),
    funciones: str | None = Form(default=None),
    logros: str | None = Form(default=None),
    url_repositorio: str | None = Form(default=None),
):
    result = profile_repository.update_project(
        project_id,
        {
            "nombre": nombre,
            "empresa": empresa,
            "ciudad": ciudad,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "es_proyecto_actual": es_proyecto_actual,
            "stack": stack,
            "funciones": funciones,
            "logros": logros,
            "url_repositorio": url_repositorio,
        },
    )
    flash = "project_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_projects_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.PROJECTS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/projects/{project_id}/delete")
def delete_project(request: Request, project_id: int):
    result = profile_repository.delete_project(project_id)
    flash = "project_deleted" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_projects_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.PROJECTS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/education")
def add_education(
    request: Request,
    titulo: str = Form(...),
    institucion: str = Form(...),
    ciudad: str | None = Form(default=None),
    nivel: str = Form(default="Pregrado"),
    fecha_inicio: date = Form(...),
    fecha_fin: date | None = Form(default=None),
    status: str = Form(default="Completado"),
):
    profile = profile_repository.get_active_profile()
    if not profile:
        flash = "profile_error"
    else:
        result = profile_repository.add_education(
            profile["id"],
            {
                "titulo": titulo,
                "institucion": institucion,
                "ciudad": ciudad,
                "nivel": nivel,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "status": status,
            },
        )
        flash = "education_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_formation_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.CREDENTIALS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/education/{education_id}/delete")
def delete_education(request: Request, education_id: int):
    result = profile_repository.delete_education(education_id)
    flash = "education_deleted" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_formation_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.CREDENTIALS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/courses")
def add_course(
    request: Request,
    titulo: str = Form(...),
    institucion: str = Form(...),
    fecha_inicio: date | None = Form(default=None),
    fecha_fin: date | None = Form(default=None),
    status: str = Form(default="Completado"),
    url_certificado: str | None = Form(default=None),
):
    profile = profile_repository.get_active_profile()
    if not profile:
        flash = "profile_error"
    else:
        result = profile_repository.add_course(
            profile["id"],
            {
                "titulo": titulo,
                "institucion": institucion,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "status": status,
                "url_certificado": url_certificado,
            },
        )
        flash = "course_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_formation_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.CREDENTIALS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/courses/{course_id}/delete")
def delete_course(request: Request, course_id: int):
    result = profile_repository.delete_course(course_id)
    flash = "course_deleted" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_formation_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.CREDENTIALS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/certifications")
def add_certification(
    request: Request,
    titulo: str = Form(...),
    institucion: str = Form(...),
    fecha_obtencion: date = Form(...),
    fecha_vencimiento: date | None = Form(default=None),
    status: str = Form(default="Vigente"),
    url_certificado: str | None = Form(default=None),
):
    profile = profile_repository.get_active_profile()
    if not profile:
        flash = "profile_error"
    else:
        result = profile_repository.add_certification(
            profile["id"],
            {
                "titulo": titulo,
                "institucion": institucion,
                "fecha_obtencion": fecha_obtencion,
                "fecha_vencimiento": fecha_vencimiento,
                "status": status,
                "url_certificado": url_certificado,
            },
        )
        flash = "certification_saved" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_formation_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.CREDENTIALS, flash=flash),
        status_code=303,
    )


@router.post("/app/profile/certifications/{certification_id}/delete")
def delete_certification(request: Request, certification_id: int):
    result = profile_repository.delete_certification(certification_id)
    flash = "certification_deleted" if result["success"] else "profile_error"
    if request.headers.get("HX-Request") == "true":
        return _render_profile_formation_shell(request, flash, include_oob=True)
    return RedirectResponse(
        url=_build_profile_redirect_url(action=ProfileRefreshAction.CREDENTIALS, flash=flash),
        status_code=303,
    )

