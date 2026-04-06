"""FastAPI endpoint for the Chrome extension."""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
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
analysis_jobs: dict[str, dict] = {}
analysis_jobs_lock = threading.Lock()


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
    job_id: str
    status: str


class AnalysisJobResponse(BaseModel):
    job_id: str
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


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _set_job_state(job_id: str, **updates) -> dict:
    with analysis_jobs_lock:
        current = analysis_jobs.get(job_id, {}).copy()
        current.update(updates)
        current["updated_at"] = _utc_now()
        analysis_jobs[job_id] = current
        return current.copy()


def _create_analysis_job(vacancy_id: int) -> dict:
    job_id = str(uuid4())
    now = _utc_now()
    job = {
        "job_id": job_id,
        "vacancy_id": vacancy_id,
        "status": "queued",
        "step": "saved",
        "message": "Vacante guardada. Analisis en cola.",
        "error": None,
        "created_at": now,
        "updated_at": now,
    }
    with analysis_jobs_lock:
        analysis_jobs[job_id] = job
    return job.copy()


def _run_analysis_job(job_id: str, vacancy_id: int) -> None:
    _set_job_state(
        job_id,
        status="running",
        step="analyzing",
        message="Analizando vacante contra el perfil activo.",
        error=None,
    )
    try:
        result = analyze_vacancy_use_case.execute(vacancy_id)
        if result["omitido"]:
            _set_job_state(
                job_id,
                status="completed",
                step="completed",
                message="Vacante guardada. Analisis omitido porque no hay perfil activo.",
                error=None,
            )
            return
        _set_job_state(
            job_id,
            status="completed",
            step="completed",
            message="Vacante guardada y analizada correctamente.",
            error=None,
        )
    except AnalysisError as exc:
        logger.warning("La vacante %s se guardo, pero el analisis automatico fallo: %s", vacancy_id, exc)
        _set_job_state(
            job_id,
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

    job = _create_analysis_job(resultado["id"])
    background_tasks.add_task(_run_analysis_job, job["job_id"], resultado["id"])

    return AsyncVacanteResponse(
        success=True,
        message="Vacante guardada. Analisis en segundo plano iniciado.",
        id=resultado["id"],
        job_id=job["job_id"],
        status=job["status"],
    )


@app.get("/vacantes/jobs/{job_id}", response_model=AnalysisJobResponse)
def get_analysis_job(job_id: str):
    with analysis_jobs_lock:
        job = analysis_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return AnalysisJobResponse(**job)


@app.get("/vacantes/{vacancy_id}/analysis", response_model=VacancyAnalysisResponse)
def get_vacancy_analysis(vacancy_id: int):
    analysis = analysis_repository.get_by_vacancy_id(vacancy_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    return VacancyAnalysisResponse(vacancy_id=vacancy_id, analysis=analysis)
