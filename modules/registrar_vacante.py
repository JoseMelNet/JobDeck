"""Streamlit page for creating vacancies."""

from __future__ import annotations

import time

import streamlit as st

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.application.use_cases.create_vacancy import CreateVacancyUseCase
from app.domain.enums.modality import MODALITIES
from app.domain.exceptions import AnalysisError, ValidationError
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository

vacancy_repository = VacancyRepository()
profile_repository = ProfileRepository()
analysis_repository = AnalysisRepository()
create_vacancy_use_case = CreateVacancyUseCase(vacancy_repository)
analyze_vacancy_use_case = AnalyzeVacancyUseCase(
    vacancy_repository=vacancy_repository,
    profile_repository=profile_repository,
    analysis_repository=analysis_repository,
)


def mostrar_registrar_vacante():
    """Render the create vacancy tab."""
    st.subheader("Agregar Nueva Vacante")

    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    with st.form("form_vacante", clear_on_submit=False):
        col_left, col_right = st.columns(2)

        with col_left:
            empresa = st.text_input(
                "🏢 Empresa",
                placeholder="Ej: Google, Microsoft, Skydropx",
                key=f"empresa_{st.session_state.form_key}",
            )
            cargo = st.text_input(
                "💼 Cargo",
                placeholder="Ej: Data Analyst, BI Analyst",
                key=f"cargo_{st.session_state.form_key}",
            )

        with col_right:
            modalidad = st.selectbox(
                "📍 Modalidad",
                options=MODALITIES,
                key=f"modalidad_{st.session_state.form_key}",
            )
            link = st.text_input(
                "🔗 Link de la Vacante",
                placeholder="https://www.ejemplo.com/vacante",
                key=f"link_{st.session_state.form_key}",
            )

        descripcion = st.text_area(
            "📝 Descripción",
            placeholder="Pega aquí la descripción completa de la vacante...",
            height=200,
            key=f"descripcion_{st.session_state.form_key}",
        )

        btn_guardar = st.form_submit_button(
            "💾 Guardar Vacante",
            use_container_width=True,
            type="primary",
        )

    if btn_guardar:
        _procesar_guardado(empresa, cargo, modalidad, link, descripcion)


def _procesar_guardado(
    empresa: str,
    cargo: str,
    modalidad: str,
    link: str,
    descripcion: str,
):
    """Validate and persist a new vacancy."""
    if not empresa or not cargo or not descripcion:
        st.error("⚠️ Por favor completa todos los campos requeridos")
        return

    try:
        resultado = create_vacancy_use_case.execute(
            empresa=empresa,
            cargo=cargo,
            modalidad=modalidad,
            link=link.strip() if link else None,
            descripcion=descripcion,
        )
    except ValidationError as exc:
        st.error(f"⚠️ {exc}")
        return

    if resultado["success"]:
        vacante_id = resultado.get("id")
        if vacante_id:
            try:
                analyze_vacancy_use_case.execute(vacante_id)
            except AnalysisError as exc:
                st.warning(f"⚠️ La vacante se guardó, pero el análisis falló: {exc}")

        st.success(resultado["message"])
        st.balloons()

        st.session_state.form_key += 1
        time.sleep(2)
        st.rerun()
    else:
        st.error(f"❌ {resultado['message']}")
