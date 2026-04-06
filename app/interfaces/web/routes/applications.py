"""HTML routes for the applications follow-up page."""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.enums.application_status import APPLICATION_STATUSES
from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from app.interfaces.web.routes.dashboard import _build_metrics, _build_nav
from app.interfaces.web.templates import templates

router = APIRouter(tags=["web-applications"])
DEFAULT_PAGE_SIZE = 20
PAGE_SIZE_OPTIONS = (10, 20, 50)

application_repository = ApplicationRepository()
FOLLOW_UP_STATES = [
    "Pending",
    "Applied",
    "Technical Test",
    "In Interview",
    "Open Offer",
    "Rejected",
]

STATUS_LABELS = {
    "Pending": "Pendiente por aplicar",
    "Applied": "Aplicada",
    "Technical Test": "Prueba tecnica",
    "In Interview": "Entrevista",
    "Open Offer": "Oferta",
    "Rejected": "Rechazada",
    "Done": "Cerrada",
}

STATUS_META = {
    "Pending": {"tone": "gray", "label": STATUS_LABELS["Pending"]},
    "Applied": {"tone": "blue", "label": STATUS_LABELS["Applied"]},
    "Technical Test": {"tone": "violet", "label": STATUS_LABELS["Technical Test"]},
    "In Interview": {"tone": "amber", "label": STATUS_LABELS["In Interview"]},
    "Open Offer": {"tone": "green", "label": STATUS_LABELS["Open Offer"]},
    "Rejected": {"tone": "red", "label": STATUS_LABELS["Rejected"]},
    "Done": {"tone": "green", "label": STATUS_LABELS["Done"]},
}


def _build_flash_message(flash: str | None) -> tuple[str, str] | None:
    if flash == "interest_created":
        return ("success", "La vacante paso a Seguimiento como pendiente por aplicar.")
    if flash == "already_tracking":
        return ("info", "La vacante ya estaba en Seguimiento.")
    if flash == "status_updated":
        return ("success", "El estado de la aplicacion fue actualizado.")
    if flash == "application_updated":
        return ("success", "Los datos de la aplicacion fueron actualizados.")
    if flash == "application_deleted":
        return ("success", "La aplicacion fue eliminada.")
    if flash == "application_error":
        return ("warning", "No se pudo completar la accion sobre la aplicacion.")
    return None


def _decorate_applications(applications: list[dict]) -> list[dict]:
    decorated = []
    for item in applications:
        meta = STATUS_META.get(item["estado"], {"tone": "gray", "label": item["estado"]})
        decorated.append({**item, "status_meta": meta})
    return decorated


def _filter_applications(applications: list[dict], q: str | None, state: str) -> list[dict]:
    if q:
        needle = q.strip().lower()
        applications = [
            item
            for item in applications
            if needle in item["empresa"].lower() or needle in item["cargo"].lower()
        ]
    if state != "Todos":
        applications = [item for item in applications if item["estado"] == state]
    return applications


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


def _build_tracking_context(
    selected: int | None,
    flash: str | None,
    q: str | None,
    state: str,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict:
    normalized_state = state if state in (["Todos"] + FOLLOW_UP_STATES) else "Todos"
    normalized_page_size = _normalize_page_size(page_size)
    applications = application_repository.list_all()
    if applications:
        applications = sorted(
            applications,
            key=lambda item: item.get("fecha_aplicacion") or item.get("fecha_registro") or "",
            reverse=True,
        )
        applications = _decorate_applications(applications)
        applications = _filter_applications(applications, q=q, state=normalized_state)
    resolved_page = _resolve_page_for_selected(applications, selected, normalized_page_size, page)
    paged_applications, pagination = _paginate_items(applications, resolved_page, normalized_page_size)

    selected_application = None
    if paged_applications:
        if selected is None:
            selected_application = paged_applications[0]
        else:
            selected_application = next((item for item in paged_applications if item["id"] == selected), paged_applications[0])

    return {
        "applications": paged_applications,
        "selected_application": selected_application,
        "flash_message": _build_flash_message(flash),
        "follow_up_states": FOLLOW_UP_STATES,
        "all_statuses": list(APPLICATION_STATUSES),
        "status_labels": STATUS_LABELS,
        "query": q or "",
        "current_state": normalized_state,
        "pagination": pagination,
    }


@router.get("/app/applications")
def applications_index(
    request: Request,
    selected: int | None = None,
    flash: str | None = None,
    q: str | None = None,
    state: str = "Todos",
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    context = _build_tracking_context(selected=selected, flash=flash, q=q, state=state, page=page, page_size=page_size)
    return templates.TemplateResponse(
        request=request,
        name="applications/index.html",
        context={
            "page_title": "Seguimiento",
            "active_nav": "applications",
            "nav_items": _build_nav("applications"),
            "metrics": _build_metrics(),
            **context,
        },
    )


@router.get("/app/applications/shell", response_class=HTMLResponse)
def applications_shell_partial(
    request: Request,
    selected: int | None = None,
    flash: str | None = None,
    q: str | None = None,
    state: str = "Todos",
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    context = _build_tracking_context(selected=selected, flash=flash, q=q, state=state, page=page, page_size=page_size)
    return templates.TemplateResponse(
        request=request,
        name="applications/_shell.html",
        context={"request": request, **context},
    )


@router.get("/app/applications/{application_id}/detail", response_class=HTMLResponse)
def application_detail_partial(
    request: Request,
    application_id: int,
    q: str | None = None,
    state: str = "Todos",
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    context = _build_tracking_context(selected=application_id, flash=None, q=q, state=state, page=page, page_size=page_size)
    return templates.TemplateResponse(
        request=request,
        name="applications/_detail.html",
        context={"request": request, **context},
    )


@router.post("/app/applications/{application_id}/status")
def update_application_status(
    request: Request,
    application_id: int,
    target_state: str = Form(...),
    q: str | None = Form(default=None),
    state: str = Form(default="Todos"),
):
    result = application_repository.update_status(application_id, target_state)
    flash = "status_updated" if result["success"] else "application_error"
    if request.headers.get("HX-Request") == "true":
        context = _build_tracking_context(selected=application_id, flash=flash, q=q, state=state)
        return templates.TemplateResponse(
            request=request,
            name="applications/_shell.html",
            context={"request": request, **context},
        )
    return RedirectResponse(url=f"/app/applications?selected={application_id}&flash={flash}", status_code=303)


@router.post("/app/applications/{application_id}/update")
def update_application_data(
    request: Request,
    application_id: int,
    estado: str = Form(...),
    nombre_recruiter: str | None = Form(default=None),
    email_recruiter: str | None = Form(default=None),
    telefono_recruiter: str | None = Form(default=None),
    notas: str | None = Form(default=None),
    q: str | None = Form(default=None),
    state: str = Form(default="Todos"),
):
    result = application_repository.update(
        application_id,
        estado=estado,
        nombre_recruiter=nombre_recruiter,
        email_recruiter=email_recruiter,
        telefono_recruiter=telefono_recruiter,
        notas=notas,
    )
    flash = "application_updated" if result["success"] else "application_error"
    if request.headers.get("HX-Request") == "true":
        context = _build_tracking_context(selected=application_id, flash=flash, q=q, state=state)
        return templates.TemplateResponse(
            request=request,
            name="applications/_shell.html",
            context={"request": request, **context},
        )
    return RedirectResponse(url=f"/app/applications?selected={application_id}&flash={flash}", status_code=303)


@router.post("/app/applications/{application_id}/delete")
def delete_application(
    request: Request,
    application_id: int,
    q: str | None = Form(default=None),
    state: str = Form(default="Todos"),
):
    result = application_repository.delete(application_id)
    flash = "application_deleted" if result["success"] else "application_error"
    if request.headers.get("HX-Request") == "true":
        context = _build_tracking_context(selected=None, flash=flash, q=q, state=state)
        return templates.TemplateResponse(
            request=request,
            name="applications/_shell.html",
            context={"request": request, **context},
        )
    if result["success"]:
        return RedirectResponse(url="/app/applications?flash=application_deleted", status_code=303)
    return RedirectResponse(url=f"/app/applications?selected={application_id}&flash=application_error", status_code=303)
