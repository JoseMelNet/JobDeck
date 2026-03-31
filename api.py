"""FastAPI endpoint for the Chrome extension."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.application.use_cases.create_vacancy import CreateVacancyUseCase
from app.domain.exceptions import AnalysisError, ValidationError
from app.infrastructure.persistence.connection import test_connection
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository


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
