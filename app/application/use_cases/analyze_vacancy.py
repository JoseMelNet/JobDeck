"""Use case for vacancy analysis."""

from __future__ import annotations

from app.domain.exceptions import AnalysisError
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.application.services.analysis_service import AnalysisService
from modules.analizar_vacante import analizar_vacante


class AnalyzeVacancyUseCase:
    """Execute the vacancy analysis workflow without UI concerns."""

    def __init__(
        self,
        vacancy_repository: VacancyRepository,
        profile_repository: ProfileRepository,
        analysis_repository: AnalysisRepository,
    ) -> None:
        self.vacancy_repository = vacancy_repository
        self.profile_repository = profile_repository
        self.analysis_repository = analysis_repository
        self.analysis_service = AnalysisService(profile_repository)

    def execute(self, vacante_id: int) -> dict:
        vacante = self.vacancy_repository.get_by_id(vacante_id)
        if not vacante:
            raise AnalysisError(f"No se encontró la vacante con ID {vacante_id}.")

        perfil = self.profile_repository.get_active_profile()
        if not perfil:
            return {
                "success": True,
                "analizado": False,
                "omitido": True,
                "message": f"Análisis omitido para vacante {vacante_id}: no existe un perfil activo.",
            }

        perfil_payload = self.analysis_service.build_profile_payload(perfil["id"])
        if not perfil_payload:
            raise AnalysisError("No se pudo cargar el perfil completo para análisis.")

        resultado = analizar_vacante(vacante, perfil_payload)
        if not resultado["success"]:
            raise AnalysisError(resultado["message"])

        persistencia = self.analysis_repository.save(vacante["id"], perfil["id"], resultado)
        if not persistencia["success"]:
            raise AnalysisError(persistencia["message"])

        return {
            "success": True,
            "analizado": True,
            "omitido": False,
            "message": persistencia["message"],
            "analisis": resultado,
        }
