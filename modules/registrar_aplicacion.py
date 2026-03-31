"""Streamlit page for registering a new application."""

from __future__ import annotations

import time
from datetime import date

import streamlit as st

from app.application.use_cases.register_application import RegisterApplicationUseCase
from app.domain.enums.application_status import APPLICATION_STATUSES
from app.domain.exceptions import ValidationError
from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository

application_repository = ApplicationRepository()
vacancy_repository = VacancyRepository()
register_application_use_case = RegisterApplicationUseCase(application_repository)

ESTADOS = list(APPLICATION_STATUSES)
ESTADO_EMOJIS = {
    "Pending": "⏳ Pending",
    "Applied": "📤 Applied",
    "Technical Test": "🧪 Technical Test",
    "In Interview": "🗓️ In Interview",
    "Done": "✅ Done",
    "Rejected": "❌ Rejected",
    "Open Offer": "🎉 Open Offer",
}


def mostrar_registrar_aplicacion():
    """Render the application registration tab."""
    st.subheader("Registrar Nueva Aplicación")

    if "aplic_form_key" not in st.session_state:
        st.session_state.aplic_form_key = 0

    vacantes_disponibles = vacancy_repository.list_without_application()
    if not vacantes_disponibles:
        st.info(
            "📭 No hay vacantes disponibles para aplicar. Todas tus vacantes ya "
            "tienen una aplicación registrada, o aún no has registrado ninguna vacante."
        )
        st.page_link("app.py", label="➕ Ir a Registrar Vacante", icon="📋")
        return

    default_vacante_id = st.session_state.get("aplicar_vacante_id")
    vacante_ids = [vacante["id"] for vacante in vacantes_disponibles]
    default_index = vacante_ids.index(default_vacante_id) if default_vacante_id in vacante_ids else 0

    with st.form(f"form_aplicacion_{st.session_state.aplic_form_key}", clear_on_submit=False):
        col_vacante, col_fecha = st.columns([3, 1])

        with col_vacante:
            opciones_vacantes = {
                vacante["id"]: f"{vacante['empresa']}  —  {vacante['cargo']}  [{vacante['modalidad']}]"
                for vacante in vacantes_disponibles
            }
            vacante_id = st.selectbox(
                "💼 Vacante a la que apliqué",
                options=vacante_ids,
                index=default_index,
                format_func=lambda x: opciones_vacantes[x],
                key=f"aplic_vacante_{st.session_state.aplic_form_key}",
            )

        with col_fecha:
            fecha_aplicacion = st.date_input(
                "📅 Fecha de aplicación",
                value=date.today(),
                key=f"aplic_fecha_{st.session_state.aplic_form_key}",
            )

        estado = st.selectbox(
            "📊 Estado actual",
            options=ESTADOS,
            format_func=lambda x: ESTADO_EMOJIS[x],
            key=f"aplic_estado_{st.session_state.aplic_form_key}",
        )

        st.markdown("---")
        st.markdown("**👤 Datos del Recruiter** *(opcionales)*")

        col_nombre, col_email, col_tel = st.columns(3)
        with col_nombre:
            nombre_recruiter = st.text_input(
                "Nombre",
                placeholder="Ej: Ana Garcia",
                key=f"aplic_recruiter_nombre_{st.session_state.aplic_form_key}",
            )
        with col_email:
            email_recruiter = st.text_input(
                "Email",
                placeholder="Ej: ana@empresa.com",
                key=f"aplic_recruiter_email_{st.session_state.aplic_form_key}",
            )
        with col_tel:
            telefono_recruiter = st.text_input(
                "Telefono",
                placeholder="Ej: +52 55 1234 5678",
                key=f"aplic_recruiter_tel_{st.session_state.aplic_form_key}",
            )

        st.markdown("---")
        notas = st.text_area(
            "📝 Notas personales",
            placeholder="Ej: Aplique por referido de Juan. Me pidieron portafolio.",
            height=130,
            key=f"aplic_notas_{st.session_state.aplic_form_key}",
        )

        btn_guardar = st.form_submit_button(
            "💾 Guardar Aplicación",
            use_container_width=True,
            type="primary",
        )

    if btn_guardar:
        _procesar_guardado(
            vacante_id=vacante_id,
            fecha_aplicacion=fecha_aplicacion,
            estado=estado,
            nombre_recruiter=nombre_recruiter,
            email_recruiter=email_recruiter,
            telefono_recruiter=telefono_recruiter,
            notas=notas,
        )


def _procesar_guardado(
    vacante_id: int,
    fecha_aplicacion,
    estado: str,
    nombre_recruiter: str,
    email_recruiter: str,
    telefono_recruiter: str,
    notas: str,
):
    """Validate and persist a new application."""
    if not vacante_id:
        st.error("⚠️ Debes seleccionar una vacante.")
        return

    try:
        resultado = register_application_use_case.execute(
            vacante_id=vacante_id,
            fecha_aplicacion=fecha_aplicacion,
            estado=estado,
            nombre_recruiter=nombre_recruiter or None,
            email_recruiter=email_recruiter or None,
            telefono_recruiter=telefono_recruiter or None,
            notas=notas or None,
        )
    except ValidationError as exc:
        st.error(f"⚠️ {exc}")
        return

    if resultado["success"]:
        st.success(resultado["message"])
        st.balloons()
        st.session_state.aplic_form_key += 1
        st.session_state.pop("aplicar_vacante_id", None)
        time.sleep(2)
        st.rerun()
    else:
        st.error(f"❌ {resultado['message']}")
