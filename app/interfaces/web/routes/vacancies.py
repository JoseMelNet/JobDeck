"""HTML routes for vacancy-related pages."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.application.use_cases.create_vacancy import CreateVacancyUseCase
from app.application.use_cases.register_application import RegisterApplicationUseCase
from app.domain.exceptions import AnalysisError, ValidationError
from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository
from app.interfaces.web.routes.dashboard import _build_metrics, _build_nav
from app.interfaces.web.templates import templates

router = APIRouter(tags=["web-vacancies"])
DEFAULT_PAGE_SIZE = 20
PAGE_SIZE_OPTIONS = (10, 20, 50)

vacancy_repository = VacancyRepository()
application_repository = ApplicationRepository()
analysis_repository = AnalysisRepository()
profile_repository = ProfileRepository()
create_vacancy_use_case = CreateVacancyUseCase(vacancy_repository)
analyze_vacancy_use_case = AnalyzeVacancyUseCase(
    vacancy_repository=vacancy_repository,
    profile_repository=profile_repository,
    analysis_repository=analysis_repository,
)
register_application_use_case = RegisterApplicationUseCase(application_repository)

STATUS_META = {
    "En seguimiento": {"tone": "blue", "label": "En seguimiento"},
    "Analizada": {"tone": "green", "label": "Analizada"},
    "Registrada": {"tone": "gray", "label": "Registrada"},
}
INBOX_VIEWS = ["Todas", "Recientes", "Analizadas", "En seguimiento", "Sin analizar"]


def _application_ids_with_tracking() -> set[int]:
    return {item["vacante_id"] for item in application_repository.list_all()}


def _build_vacancy_items(limit: int | None = None) -> list[dict]:
    vacancies = vacancy_repository.list_all()
    vacancies = sorted(vacancies, key=lambda item: item.get("fecha_registro") or "", reverse=True)
    visible_vacancies = vacancies[:limit] if limit else vacancies
    vacancy_ids = [item["id"] for item in visible_vacancies]
    analyses_by_vacancy = analysis_repository.get_by_vacancy_ids(vacancy_ids)
    tracked_vacancy_ids = _application_ids_with_tracking()
    items = []
    for vacancy in visible_vacancies:
        analysis = analyses_by_vacancy.get(vacancy["id"])
        has_application = vacancy["id"] in tracked_vacancy_ids
        status_label = "En seguimiento" if has_application else ("Analizada" if analysis else "Registrada")
        items.append(
            {
                **vacancy,
                "analisis": analysis,
                "status_label": status_label,
                "status_meta": STATUS_META[status_label],
                "score_label": f"{analysis.get('score_total', 0):.0f}" if analysis else "Sin score",
                "has_application": has_application,
            }
        )
    return items


def _filter_vacancy_items(items: list[dict], *, q: str | None, view: str) -> list[dict]:
    if q:
        needle = q.strip().lower()
        items = [
            item
            for item in items
            if needle in item["empresa"].lower() or needle in item["cargo"].lower()
        ]

    if view == "Recientes":
        items = items[:10]
    elif view == "Analizadas":
        items = [item for item in items if item["analisis"]]
    elif view == "En seguimiento":
        items = [item for item in items if item["has_application"]]
    elif view == "Sin analizar":
        items = [item for item in items if not item["analisis"]]
    return items


def _normalize_page_size(page_size: int) -> int:
    return page_size if page_size in PAGE_SIZE_OPTIONS else DEFAULT_PAGE_SIZE


def _resolve_page_for_selected(items: list[dict], selected: int | None, page_size: int, requested_page: int) -> int:
    if selected is None:
        return requested_page
    selected_index = next((index for index, item in enumerate(items) if item["id"] == selected), None)
    if selected_index is None:
        return requested_page
    return (selected_index // page_size) + 1


def _paginate_items(items: list[dict], page: int, page_size: int) -> tuple[list[dict], dict]:
    total_items = len(items)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    current_page = min(max(page, 1), total_pages)
    start = (current_page - 1) * page_size
    end = start + page_size
    return items[start:end], {
        "page": current_page,
        "page_size": page_size,
        "page_size_options": PAGE_SIZE_OPTIONS,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
        "prev_page": current_page - 1,
        "next_page": current_page + 1,
    }


def _selected_vacancy(selected_id: int | None) -> dict | None:
    items = _build_vacancy_items(limit=None)
    if not items:
        return None
    if selected_id is None:
        return items[0]
    return next((item for item in items if item["id"] == selected_id), items[0])


def _flash_message(flash: str | None) -> tuple[str, str] | None:
    if flash == "vacancy_created":
        return ("success", "Vacante registrada y analizada. Revisa el resultado en Inbox.")
    if flash == "vacancy_created_without_analysis":
        return ("info", "Vacante registrada. El analisis se omitio porque no hay perfil activo.")
    if flash == "vacancy_analysis_failed":
        return ("warning", "Vacante registrada, pero el analisis no pudo completarse.")
    if flash == "interest_error":
        return ("warning", "No se pudo enviar la vacante a Seguimiento.")
    return None


def _build_inbox_context(
    selected: int | None,
    flash: str | None,
    q: str | None,
    view: str,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict:
    normalized_view = view if view in INBOX_VIEWS else "Todas"
    normalized_page_size = _normalize_page_size(page_size)
    all_items = _build_vacancy_items(limit=None)
    filtered_items = _filter_vacancy_items(all_items, q=q, view=normalized_view)
    resolved_page = _resolve_page_for_selected(filtered_items, selected, normalized_page_size, page)
    items, pagination = _paginate_items(filtered_items, resolved_page, normalized_page_size)
    selected_vacancy = next((item for item in items if item["id"] == selected), None) if selected else (items[0] if items else None)
    return {
        "vacancies": items,
        "selected_vacancy": selected_vacancy,
        "flash_message": _flash_message(flash),
        "query": q or "",
        "current_view": normalized_view,
        "pagination": pagination,
        "inbox_views": INBOX_VIEWS,
        "summary": {
            "total": len(filtered_items),
            "analizadas": sum(1 for item in filtered_items if item["analisis"]),
            "seguimiento": sum(1 for item in filtered_items if item["has_application"]),
        },
    }


@router.get("/app/vacancies")
def vacancies_index(
    request: Request,
    selected: int | None = None,
    flash: str | None = None,
    q: str | None = None,
    view: str = "Todas",
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    context = _build_inbox_context(selected=selected, flash=flash, q=q, view=view, page=page, page_size=page_size)
    return templates.TemplateResponse(
        request=request,
        name="vacancies/index.html",
        context={
            "page_title": "Inbox de Vacantes",
            "active_nav": "vacancies",
            "nav_items": _build_nav("vacancies"),
            "metrics": _build_metrics(),
            **context,
        },
    )


@router.get("/app/vacancies/new")
def vacancy_new(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="vacancies/new.html",
        context={
            "page_title": "Nueva Vacante",
            "active_nav": "new_vacancy",
            "nav_items": _build_nav("new_vacancy"),
            "metrics": _build_metrics(),
        },
    )


@router.post("/app/vacancies/new")
def vacancy_create(
    empresa: str = Form(...),
    cargo: str = Form(...),
    modalidad: str = Form(...),
    descripcion: str = Form(...),
    link: str | None = Form(default=None),
):
    try:
        result = create_vacancy_use_case.execute(
            empresa=empresa,
            cargo=cargo,
            modalidad=modalidad,
            descripcion=descripcion,
            link=link,
        )
    except ValidationError:
        return RedirectResponse(url="/app/vacancies/new?flash=validation_error", status_code=303)

    if not result["success"] or not result.get("id"):
        return RedirectResponse(url="/app/vacancies/new?flash=save_error", status_code=303)

    vacancy_id = result["id"]
    try:
        analysis_result = analyze_vacancy_use_case.execute(vacancy_id)
    except AnalysisError:
        return RedirectResponse(
            url=f"/app/vacancies?selected={vacancy_id}&flash=vacancy_analysis_failed",
            status_code=303,
        )

    if analysis_result["omitido"]:
        return RedirectResponse(
            url=f"/app/vacancies?selected={vacancy_id}&flash=vacancy_created_without_analysis",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/app/vacancies?selected={vacancy_id}&flash=vacancy_created",
        status_code=303,
    )


@router.get("/app/vacancies/{vacancy_id}/detail", response_class=HTMLResponse)
def vacancy_detail_partial(request: Request, vacancy_id: int):
    vacancy = _selected_vacancy(vacancy_id)
    return templates.TemplateResponse(
        request=request,
        name="vacancies/_detail.html",
        context={"request": request, "selected_vacancy": vacancy},
    )


@router.get("/app/vacancies/list", response_class=HTMLResponse)
def vacancy_list_partial(
    request: Request,
    selected: int | None = None,
    q: str | None = None,
    view: str = "Todas",
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    context = _build_inbox_context(selected=selected, flash=None, q=q, view=view, page=page, page_size=page_size)
    return templates.TemplateResponse(
        request=request,
        name="vacancies/_list.html",
        context={"request": request, **context},
    )


@router.post("/app/vacancies/{vacancy_id}/interest")
def mark_vacancy_as_interesting(vacancy_id: int):
    existing = application_repository.list_by_vacancy(vacancy_id)
    if existing:
        application_id = existing[0]["id"]
        return RedirectResponse(
            url=f"/app/applications?selected={application_id}&flash=already_tracking",
            status_code=303,
        )

    result = register_application_use_case.execute(
        vacante_id=vacancy_id,
        fecha_aplicacion=date.today(),
        estado="Pending",
        nombre_recruiter=None,
        email_recruiter=None,
        telefono_recruiter=None,
        notas="Marcada desde Inbox web como vacante de interes.",
    )
    if result["success"]:
        return RedirectResponse(
            url=f"/app/applications?selected={result['id']}&flash=interest_created",
            status_code=303,
        )

    return RedirectResponse(url="/app/vacancies?flash=interest_error", status_code=303)
