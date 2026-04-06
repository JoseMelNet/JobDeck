"""Dashboard and shell routes for the web UI."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository
from app.interfaces.web.templates import templates

router = APIRouter(tags=["web-dashboard"])

vacancy_repository = VacancyRepository()
application_repository = ApplicationRepository()


def _build_nav(active: str) -> list[dict[str, str | bool]]:
    return [
        {"label": "Nueva Vacante", "href": "/app/vacancies/new", "active": active == "new_vacancy"},
        {"label": "Inbox", "href": "/app/vacancies", "active": active == "vacancies"},
        {"label": "Seguimiento", "href": "/app/applications", "active": active == "applications"},
        {"label": "Mi Perfil", "href": "/app/profile", "active": active == "profile"},
    ]


def _build_metrics() -> list[dict[str, str | int]]:
    stats = application_repository.count_by_status()
    return [
        {"label": "Vacantes", "value": vacancy_repository.count()},
        {"label": "Aplicaciones", "value": stats["Total"]},
        {"label": "Entrevistas", "value": stats["In Interview"]},
        {"label": "Ofertas", "value": stats["Open Offer"]},
        {"label": "Rechazadas", "value": stats["Rejected"]},
    ]


@router.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/app", status_code=302)


@router.get("/app", include_in_schema=False)
def app_redirect() -> RedirectResponse:
    return RedirectResponse(url="/app/vacancies", status_code=302)


@router.get("/app/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "page_title": "CVs Optimizator",
            "active_nav": "vacancies",
            "nav_items": _build_nav("vacancies"),
            "metrics": _build_metrics(),
        },
    )
