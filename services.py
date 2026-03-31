"""Legacy service helpers kept for compatibility during the refactor."""

from __future__ import annotations

import logging
from contextlib import nullcontext

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.domain.exceptions import AnalysisError
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


logger = logging.getLogger(__name__)

_analyze_vacancy_use_case = AnalyzeVacancyUseCase(
    vacancy_repository=VacancyRepository(),
    profile_repository=ProfileRepository(),
    analysis_repository=AnalysisRepository(),
)


def _mostrar_error_ui(mostrar_ui: bool, mensaje: str) -> None:
    if mostrar_ui and st is not None:
        st.error(mensaje)


def _spinner_context(mostrar_ui: bool, mensaje: str):
    if mostrar_ui and st is not None:
        return st.spinner(mensaje)
    return nullcontext()


def ejecutar_analisis_vacante(vacante_id: int, mostrar_ui: bool = True) -> dict:
    """Execute vacancy analysis while preserving the legacy UI behavior."""
    try:
        with _spinner_context(
            mostrar_ui,
            "Analizando vacante con IA... esto puede tomar unos segundos",
        ):
            resultado = _analyze_vacancy_use_case.execute(vacante_id)
    except AnalysisError as exc:
        _mostrar_error_ui(mostrar_ui, f"❌ {exc}")
        return {
            "success": False,
            "analizado": False,
            "omitido": False,
            "message": str(exc),
        }

    if mostrar_ui and st is not None and resultado["success"] and resultado["analizado"]:
        st.success("✅ Análisis completado")

    if resultado["omitido"]:
        logger.warning(resultado["message"])

    return resultado
