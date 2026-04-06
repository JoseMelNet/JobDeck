"""FastAPI endpoint for the Chrome extension."""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.application.use_cases.create_vacancy import CreateVacancyUseCase
from app.domain.exceptions import AnalysisError, ValidationError
from app.infrastructure.persistence.connection import test_connection
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository
from app.interfaces.web.routes.applications import router as web_applications_router
from app.interfaces.web.routes.dashboard import router as web_dashboard_router
from app.interfaces.web.routes.profile import router as web_profile_router
from app.interfaces.web.routes.vacancies import router as web_vacancies_router


logger = logging.getLogger(__name__)

vacancy_repository = VacancyRepository()
profile_repository = ProfileRepository()
analysis_repository = AnalysisRepository()
create_vacancy_use_case = CreateVacancyUseCase(vacancy_repository)
analyze_vacancy_use_case = AnalyzeVacancyUseCase(
    vacancy_repository=vacancy_repository,
    profile_repository=profile_repository,
    analysis_repository=analysis_repository,
)
analysis_tasks: dict[str, dict] = {}
analysis_tasks_lock = threading.Lock()


app = FastAPI(
    title="CVs-Optimizador API",
    description="Endpoint local para la extension de Chrome",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent / "app" / "interfaces" / "web" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.include_router(web_dashboard_router)
app.include_router(web_vacancies_router)
app.include_router(web_applications_router)
app.include_router(web_profile_router)


class VacantePayload(BaseModel):
    empresa: str
    cargo: str
    modalidad: str
    link: Optional[str] = None
    descripcion: str


class VacanteResponse(BaseModel):
    success: bool
    message: str
    id: Optional[int] = None


class AsyncVacanteResponse(VacanteResponse):
    task_id: str
    status: str


class AnalysisTaskResponse(BaseModel):
    task_id: str
    vacancy_id: int
    status: str
    step: str
    message: str
    error: Optional[str] = None
    created_at: str
    updated_at: str


class VacancyAnalysisResponse(BaseModel):
    vacancy_id: int
    analysis: dict


class VacancyByLinkResponse(BaseModel):
    found: bool
    vacancy: Optional[dict] = None
    analysis: Optional[dict] = None


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _set_task_state(task_id: str, **updates) -> dict:
    with analysis_tasks_lock:
        current = analysis_tasks.get(task_id, {}).copy()
        current.update(updates)
        current["updated_at"] = _utc_now()
        analysis_tasks[task_id] = current
        return current.copy()


def _create_analysis_task(vacancy_id: int) -> dict:
    task_id = str(uuid4())
    now = _utc_now()
    task = {
        "task_id": task_id,
        "vacancy_id": vacancy_id,
        "status": "queued",
        "step": "saved",
        "message": "Vacante guardada. Analisis en cola.",
        "error": None,
        "created_at": now,
        "updated_at": now,
    }
    with analysis_tasks_lock:
        analysis_tasks[task_id] = task
    return task.copy()


def _run_analysis_task(task_id: str, vacancy_id: int) -> None:
    _set_task_state(
        task_id,
        status="running",
        step="analyzing",
        message="Analizando vacante contra el perfil activo.",
        error=None,
    )
    try:
        result = analyze_vacancy_use_case.execute(vacancy_id)
        if result["omitido"]:
            _set_task_state(
                task_id,
                status="completed",
                step="completed",
                message="Vacante guardada. Analisis omitido porque no hay perfil activo.",
                error=None,
            )
            return
        _set_task_state(
            task_id,
            status="completed",
            step="completed",
            message="Vacante guardada y analizada correctamente.",
            error=None,
        )
    except AnalysisError as exc:
        logger.warning("La vacante %s se guardo, pero el analisis automatico fallo: %s", vacancy_id, exc)
        _set_task_state(
            task_id,
            status="failed",
            step="failed",
            message="La vacante se guardo, pero el analisis fallo.",
            error=str(exc),
        )


@app.get("/health")
def health_check():
    """Used by the extension to verify that the local API is available."""
    db_ok = test_connection()
    return {
        "status": "ok" if db_ok else "db_error",
        "db_connected": db_ok,
        "message": "API activa" if db_ok else "API activa pero sin conexion a BD",
    }


@app.post("/vacantes", response_model=VacanteResponse)
def crear_vacante(payload: VacantePayload):
    """Create a vacancy and trigger the automatic analysis workflow."""
    modalidad_map = {
        "remote": "Remoto",
        "remoto": "Remoto",
        "on-site": "Presencial",
        "presencial": "Presencial",
        "on site": "Presencial",
        "hybrid": "Hibrido",
        "hibrido": "Hibrido",
        "hibrido ": "Hibrido",
    }
    modalidad_norm = modalidad_map.get(payload.modalidad.lower().strip(), "Remoto")
    if modalidad_norm == "Hibrido":
        modalidad_norm = "Híbrido"

    try:
        resultado = create_vacancy_use_case.execute(
            empresa=payload.empresa,
            cargo=payload.cargo,
            modalidad=modalidad_norm,
            link=payload.link,
            descripcion=payload.descripcion,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not resultado["success"]:
        raise HTTPException(status_code=500, detail=resultado["message"])

    vacante_id = resultado.get("id")
    if vacante_id:
        try:
            analyze_vacancy_use_case.execute(vacante_id)
        except AnalysisError as exc:
            logger.warning(
                "La vacante %s se guardo, pero el analisis automatico fallo: %s",
                vacante_id,
                exc,
            )

    return VacanteResponse(
        success=True,
        message=resultado["message"],
        id=resultado["id"],
    )


@app.post("/vacantes/async", response_model=AsyncVacanteResponse, status_code=202)
def crear_vacante_async(payload: VacantePayload, background_tasks: BackgroundTasks):
    """Create a vacancy quickly and continue the analysis in the background."""
    modalidad_map = {
        "remote": "Remoto",
        "remoto": "Remoto",
        "on-site": "Presencial",
        "presencial": "Presencial",
        "on site": "Presencial",
        "hybrid": "Hibrido",
        "hibrido": "Hibrido",
        "hibrido ": "Hibrido",
    }
    modalidad_norm = modalidad_map.get(payload.modalidad.lower().strip(), "Remoto")
    if modalidad_norm == "Hibrido":
        modalidad_norm = "Híbrido"

    try:
        resultado = create_vacancy_use_case.execute(
            empresa=payload.empresa,
            cargo=payload.cargo,
            modalidad=modalidad_norm,
            link=payload.link,
            descripcion=payload.descripcion,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not resultado["success"] or not resultado.get("id"):
        raise HTTPException(status_code=500, detail=resultado["message"])

    task = _create_analysis_task(resultado["id"])
    background_tasks.add_task(_run_analysis_task, task["task_id"], resultado["id"])

    return AsyncVacanteResponse(
        success=True,
        message="Vacante guardada. Analisis en segundo plano iniciado.",
        id=resultado["id"],
        task_id=task["task_id"],
        status=task["status"],
    )


@app.get("/vacantes/tasks/{task_id}", response_model=AnalysisTaskResponse)
def get_analysis_task(task_id: str):
    with analysis_tasks_lock:
        task = analysis_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return AnalysisTaskResponse(**task)


@app.get("/vacantes/jobs/{task_id}", response_model=AnalysisTaskResponse)
def get_analysis_job_legacy(task_id: str):
    return get_analysis_task(task_id)


@app.get("/vacantes/{vacancy_id}/analysis", response_model=VacancyAnalysisResponse)
def get_vacancy_analysis(vacancy_id: int):
    analysis = analysis_repository.get_by_vacancy_id(vacancy_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    return VacancyAnalysisResponse(vacancy_id=vacancy_id, analysis=analysis)


@app.get("/vacantes/by-link", response_model=VacancyByLinkResponse)
def get_vacancy_by_link(link: str = Query(..., min_length=1)):
    vacancy = vacancy_repository.get_by_link(link)
    if not vacancy:
        return VacancyByLinkResponse(found=False, vacancy=None, analysis=None)

    analysis = analysis_repository.get_by_vacancy_id(vacancy["id"])
    return VacancyByLinkResponse(found=True, vacancy=vacancy, analysis=analysis)
