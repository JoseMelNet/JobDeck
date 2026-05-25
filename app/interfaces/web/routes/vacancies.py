"""HTML routes for vacancy-related pages."""

from __future__ import annotations

from datetime import date
import unicodedata

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
DEFAULT_INBOX_VIEW = "Pendientes"

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
    "Sin analizar": {"tone": "gray", "label": "Sin analizar"},
}
INBOX_VIEWS = [DEFAULT_INBOX_VIEW, "Todas", "Recientes", "Analizadas", "Sin analizar", "En seguimiento"]
ANALYSIS_TONE_DEFAULT = {"tone": "gray", "label": "Sin analisis"}
DECISION_TONE_MAP = {
    "apply_strong": "green",
    "apply_later": "amber",
    "discard": "red",
    "unknown": "gray",
}
COHERENCE_LABELS = {
    "aligned": "Coherente",
    "cautious_high_score": "Score alto con decision cauta",
    "cautious_discard": "Score competitivo con descarte",
    "optimistic_low_score": "Decision optimista con score bajo",
    "missing_score": "Decision sin score",
    "missing_decision": "Score sin decision",
    "unknown_decision": "Decision desconocida",
}


def _safe_score(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""

    collapsed = " ".join(str(value).strip().split())
    normalized = unicodedata.normalize("NFKD", collapsed)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _score_band(score: float | None) -> str:
    if score is None:
        return "unknown"
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def _score_tone(score_band: str) -> str:
    return {
        "high": "green",
        "medium": "amber",
        "low": "red",
        "unknown": "gray",
    }.get(score_band, "gray")


def _normalize_decision(decision: str | None) -> tuple[str | None, str]:
    cleaned = _clean_display_value(decision)
    normalized = _normalize_text(cleaned)
    if not cleaned:
        return None, "unknown"
    if "aplicar si sobra tiempo" in normalized:
        return cleaned, "apply_later"
    if "aplicar si o si" in normalized:
        return cleaned, "apply_strong"
    if any(keyword in normalized for keyword in ("no aplicar", "descartar", "rechazar")):
        return cleaned, "discard"
    if any(keyword in normalized for keyword in ("revis", "evalu", "consider")):
        return cleaned, "apply_later"
    if any(keyword in normalized for keyword in ("aplicar", "prior", "avanz")):
        return cleaned, "apply_strong"
    return cleaned, "unknown"


def _coherence_status(score_band: str, decision_normalized: str, *, has_decision: bool) -> str:
    if not has_decision and score_band != "unknown":
        return "missing_decision"
    if has_decision and score_band == "unknown":
        return "missing_score"
    if decision_normalized == "unknown":
        return "unknown_decision"
    if decision_normalized == "apply_later" and score_band == "high":
        return "cautious_high_score"
    if decision_normalized == "discard" and score_band in {"high", "medium"}:
        return "cautious_discard"
    if decision_normalized == "apply_strong" and score_band == "low":
        return "optimistic_low_score"
    return "aligned"


def _build_decision_signal(analysis: dict | None) -> dict:
    score = _safe_score(analysis.get("score_total")) if analysis else None
    score_value = round(score) if score is not None else None
    score_band = _score_band(score)
    score_tone = _score_tone(score_band)
    score_label = f"{score_value:.0f}" if score_value is not None else "-"
    decision_raw, decision_normalized = _normalize_decision(
        analysis.get("decision_aplicacion") if analysis else None
    )

    if decision_normalized == "apply_strong":
        decision_label = decision_raw or "Aplicar si o si"
        decision_compact_label = "Si"
    elif decision_normalized == "apply_later":
        decision_label = decision_raw or "Aplicar si sobra tiempo"
        decision_compact_label = "Si hay tiempo"
    elif decision_normalized == "discard":
        decision_label = decision_raw or "Descartar"
        decision_compact_label = "No"
    else:
        if decision_raw:
            decision_label = decision_raw
            decision_compact_label = "Sin decision"
        else:
            decision_label = "Pendiente de analisis" if not analysis else "Sin decision"
            decision_compact_label = "Pendiente"

    decision_tone = DECISION_TONE_MAP[decision_normalized]
    coherence_status = _coherence_status(
        score_band,
        decision_normalized,
        has_decision=bool(decision_raw),
    )
    score_title = f"Score {score_label}" if score_value is not None else "Score pendiente"
    title_parts = [decision_label]
    if score_value is not None:
        title_parts.append(f"Score {score_label}")

    return {
        "score": score_value,
        "score_label": score_label,
        "score_band": score_band,
        "score_tone": score_tone,
        "decision_raw": decision_raw,
        "decision_normalized": decision_normalized,
        "decision_label": decision_label,
        "decision_compact_label": decision_compact_label,
        "decision_tone": decision_tone,
        "display_tone": decision_tone,
        "coherence_status": coherence_status,
        "coherence_label": COHERENCE_LABELS[coherence_status],
        "title": " · ".join(title_parts),
        "aria_label": " · ".join(title_parts),
        "score_title": score_title,
    }


def _score_meta(analysis: dict | None) -> dict:
    signal = _build_decision_signal(analysis)
    if signal["score"] is None:
        return {**ANALYSIS_TONE_DEFAULT, "value": None, "band": "unknown"}
    return {
        "tone": signal["score_tone"],
        "label": "Score",
        "value": signal["score"],
        "band": signal["score_band"],
    }


def _keyword_tone(value: str | None, mapping: dict[str, str], default_label: str) -> dict:
    if not value:
        return {"tone": "gray", "label": "-", "raw": None}

    normalized = value.strip()
    lowered = normalized.lower()
    for keyword, tone in mapping.items():
        if keyword in lowered:
            return {"tone": tone, "label": normalized, "raw": normalized}
    return {"tone": "gray", "label": normalized or default_label, "raw": normalized}


def _clean_display_value(value, *, max_length: int | None = None) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text or text.lower() in {"null", "none", "n/a", "na", "-"}:
        return None
    if max_length is not None and len(text) > max_length:
        return None
    return text


def _affinity_meta(analysis: dict | None) -> dict:
    if not analysis:
        return {"tone": "gray", "label": "-", "raw": None}
    return _keyword_tone(
        analysis.get("afinidad_general"),
        {
            "alta": "green",
            "media": "amber",
            "baja": "red",
        },
        "-",
    )


def _decision_meta(analysis: dict | None) -> dict:
    signal = _build_decision_signal(analysis)
    return {
        "tone": signal["decision_tone"],
        "label": signal["decision_label"],
        "raw": signal["decision_raw"],
        "normalized": signal["decision_normalized"],
    }


def _decision_visual_tone(score_meta: dict, decision_meta: dict) -> str:
    return decision_meta["tone"]


def _application_tracking_lookup() -> dict[int, int]:
    return {
        item["vacante_id"]: item["id"]
        for item in application_repository.list_all()
        if item.get("vacante_id") and item.get("id")
    }


def _compact_decision_label(analysis: dict | None) -> str:
    return _build_decision_signal(analysis)["decision_compact_label"]


def _build_context_bar(summary: dict, metrics: list[dict]) -> list[dict]:
    metric_lookup = {item["label"]: item["value"] for item in metrics}
    return [
        {"label": "Vacantes visibles", "value": summary["total"]},
        {"label": "Analizadas", "value": summary["analizadas"]},
        {"label": "En seguimiento", "value": summary["seguimiento"]},
        {"label": "Aplicaciones", "value": metric_lookup.get("Aplicaciones", 0)},
        {"label": "Rechazadas", "value": metric_lookup.get("Rechazadas", 0)},
    ]


def _detail_meta_items(vacancy: dict, analysis: dict | None) -> list[str]:
    values: list[str | None] = [
        vacancy.get("fecha_registro").strftime("%d/%m/%Y") if vacancy.get("fecha_registro") else None,
        _clean_display_value(vacancy.get("modalidad"), max_length=30),
    ]
    if analysis:
        values.extend(
            [
                _clean_display_value(analysis.get("seniority_inferido"), max_length=40),
                _clean_display_value(analysis.get("salario_detectado"), max_length=50),
                _clean_display_value(analysis.get("aspiracion_salarial_sugerida"), max_length=50),
            ]
        )
    return [value for value in values if value]


def _build_vacancy_items(limit: int | None = None) -> list[dict]:
    vacancies = vacancy_repository.list_all()
    vacancies = [item for item in vacancies if not item.get("motivo_archivo")]
    vacancies = sorted(vacancies, key=lambda item: item.get("fecha_registro") or "", reverse=True)
    visible_vacancies = vacancies[:limit] if limit else vacancies
    vacancy_ids = [item["id"] for item in visible_vacancies]
    analyses_by_vacancy = analysis_repository.get_by_vacancy_ids(vacancy_ids)
    tracking_lookup = _application_tracking_lookup()
    tracked_vacancy_ids = set(tracking_lookup)
    items = []
    for vacancy in visible_vacancies:
        analysis = analyses_by_vacancy.get(vacancy["id"])
        has_application = vacancy["id"] in tracked_vacancy_ids
        status_label = "En seguimiento" if has_application else ("Analizada" if analysis else "Sin analizar")
        decision_signal = _build_decision_signal(analysis)
        score_meta = _score_meta(analysis)
        affinity_meta = _affinity_meta(analysis)
        decision_meta = _decision_meta(analysis)
        items.append(
            {
                **vacancy,
                "analisis": analysis,
                "detail_meta_items": _detail_meta_items(vacancy, analysis),
                "modalidad_display": _clean_display_value(vacancy.get("modalidad"), max_length=30),
                "status_label": status_label,
                "status_meta": STATUS_META[status_label],
                "score_label": f"{score_meta['value']:.0f}" if score_meta["value"] is not None else "Sin analisis",
                "score_meta": score_meta,
                "affinity_meta": affinity_meta,
                "decision_meta": decision_meta,
                "decision_signal": decision_signal,
                "decision_visual_tone": decision_signal["display_tone"],
                "decision_compact_label": decision_signal["decision_compact_label"],
                "has_application": has_application,
                "tracking_application_id": tracking_lookup.get(vacancy["id"]),
            }
        )
    return items


def _is_pending_inbox_item(item: dict) -> bool:
    return not item["has_application"]


def _filter_vacancy_items(items: list[dict], *, q: str | None, view: str) -> list[dict]:
    if q:
        needle = q.strip().lower()
        items = [
            item
            for item in items
            if needle in item["empresa"].lower() or needle in item["cargo"].lower()
        ]

    if view == "Todas":
        return items
    if view == "En seguimiento":
        items = [item for item in items if item["has_application"]]
    else:
        items = [item for item in items if _is_pending_inbox_item(item)]
        if view == "Recientes":
            items = items[:10]
        elif view == "Analizadas":
            items = [item for item in items if item["analisis"]]
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


def _next_visible_vacancy_id(current_id: int, *, q: str | None, view: str) -> int | None:
    items = _filter_vacancy_items(_build_vacancy_items(limit=None), q=q, view=view)
    if not items:
        return None
    for item in items:
        if item["id"] != current_id:
            return item["id"]
    return None


def _build_inbox_url(
    *,
    selected: int | None = None,
    flash: str | None = None,
    q: str | None = None,
    view: str = DEFAULT_INBOX_VIEW,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> str:
    params: list[str] = []
    if selected is not None:
        params.append(f"selected={selected}")
    if flash:
        params.append(f"flash={flash}")
    if q:
        params.append(f"q={q}")
    if view and view != DEFAULT_INBOX_VIEW:
        params.append(f"view={view}")
    if page != 1:
        params.append(f"page={page}")
    if page_size != DEFAULT_PAGE_SIZE:
        params.append(f"page_size={page_size}")
    return "/app/vacancies" + (f"?{'&'.join(params)}" if params else "")


def _flash_message(flash: str | None) -> tuple[str, str] | None:
    if flash == "vacancy_created":
        return ("success", "Vacante registrada y analizada. Revisa el resultado en Inbox.")
    if flash == "vacancy_created_without_analysis":
        return ("info", "Vacante registrada. El analisis se omitio porque no hay perfil activo.")
    if flash == "vacancy_analysis_failed":
        return ("warning", "Vacante registrada, pero el analisis no pudo completarse.")
    if flash == "interest_error":
        return ("warning", "No se pudo enviar la vacante a Seguimiento.")
    if flash == "vacancy_discarded":
        return ("info", "Vacante descartada y removida del Inbox.")
    if flash == "vacancy_discard_error":
        return ("warning", "No se pudo descartar la vacante.")
    return None


def _build_inbox_context(
    selected: int | None,
    flash: str | None,
    q: str | None,
    view: str,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
    metrics: list[dict] | None = None,
) -> dict:
    normalized_view = view if view in INBOX_VIEWS else DEFAULT_INBOX_VIEW
    normalized_page_size = _normalize_page_size(page_size)
    all_items = _build_vacancy_items(limit=None)
    filtered_items = _filter_vacancy_items(all_items, q=q, view=normalized_view)
    resolved_page = _resolve_page_for_selected(filtered_items, selected, normalized_page_size, page)
    items, pagination = _paginate_items(filtered_items, resolved_page, normalized_page_size)
    selected_vacancy = None
    if items:
        if selected is None:
            selected_vacancy = items[0]
        else:
            selected_vacancy = next((item for item in items if item["id"] == selected), items[0])
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
            "seguimiento": sum(1 for item in all_items if item["has_application"]),
        },
        "context_bar": _build_context_bar(
            {
                "total": len(filtered_items),
                "analizadas": sum(1 for item in filtered_items if item["analisis"]),
                "seguimiento": sum(1 for item in all_items if item["has_application"]),
            },
            metrics or [],
        ),
    }


@router.get("/app/vacancies")
def vacancies_index(
    request: Request,
    selected: int | None = None,
    flash: str | None = None,
    q: str | None = None,
    view: str = DEFAULT_INBOX_VIEW,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    metrics = _build_metrics()
    context = _build_inbox_context(
        selected=selected,
        flash=flash,
        q=q,
        view=view,
        page=page,
        page_size=page_size,
        metrics=metrics,
    )
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            request=request,
            name="vacancies/_shell.html",
            context={"request": request, **context},
        )
    return templates.TemplateResponse(
        request=request,
        name="vacancies/index.html",
        context={
            "page_title": "Inbox de Vacantes",
            "active_nav": "vacancies",
            "nav_items": _build_nav("vacancies"),
            "metrics": metrics,
            "hide_global_metrics": True,
            **context,
        },
    )


@router.get("/app/vacancies/shell", response_class=HTMLResponse)
def vacancy_shell_partial(
    request: Request,
    selected: int | None = None,
    flash: str | None = None,
    q: str | None = None,
    view: str = DEFAULT_INBOX_VIEW,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
):
    context = _build_inbox_context(
        selected=selected,
        flash=flash,
        q=q,
        view=view,
        page=page,
        page_size=page_size,
        metrics=_build_metrics(),
    )
    return templates.TemplateResponse(
        request=request,
        name="vacancies/_shell.html",
        context={"request": request, **context},
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
        context={
            "request": request,
            "selected_vacancy": vacancy,
            "query": request.query_params.get("q", ""),
            "current_view": request.query_params.get("view", DEFAULT_INBOX_VIEW),
            "pagination": {
                "page": int(request.query_params.get("page", "1")),
                "page_size": int(request.query_params.get("page_size", str(DEFAULT_PAGE_SIZE))),
            },
        },
    )


@router.get("/app/vacancies/list", response_class=HTMLResponse)
def vacancy_list_partial(
    request: Request,
    selected: int | None = None,
    q: str | None = None,
    view: str = DEFAULT_INBOX_VIEW,
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


@router.post("/app/vacancies/{vacancy_id}/discard")
def discard_vacancy(
    vacancy_id: int,
    q: str | None = Form(default=None),
    view: str = Form(default=DEFAULT_INBOX_VIEW),
    page: int = Form(default=1),
    page_size: int = Form(default=DEFAULT_PAGE_SIZE),
):
    result = vacancy_repository.archive(vacancy_id, "Otro")
    if not result["success"]:
        return RedirectResponse(
            url=_build_inbox_url(
                selected=vacancy_id,
                flash="vacancy_discard_error",
                q=q,
                view=view,
                page=page,
                page_size=page_size,
            ),
            status_code=303,
        )

    next_selected = _next_visible_vacancy_id(vacancy_id, q=q, view=view)
    return RedirectResponse(
        url=_build_inbox_url(
            selected=next_selected,
            flash="vacancy_discarded",
            q=q,
            view=view,
            page=page,
            page_size=page_size,
        ),
        status_code=303,
    )
