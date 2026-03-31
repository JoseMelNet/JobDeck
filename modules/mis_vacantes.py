"""Streamlit page for managing vacancies."""

from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from app.application.use_cases.analyze_vacancy import AnalyzeVacancyUseCase
from app.domain.enums.archive_reason import ARCHIVE_REASONS
from app.infrastructure.persistence.repositories.analysis_repository import AnalysisRepository
from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from app.infrastructure.persistence.repositories.profile_repository import ProfileRepository
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository
from modules.components.ui_labels import (
    VACANCY_FILTER_STATES,
    VACANCY_MODALITY_OPTIONS,
    VACANCY_SEMAPHORE_META,
    normalize_modality_label,
)
from modules.components.profile_components import render_empty_state
from modules.components.ui_styles import inject_management_styles
from modules.components.vacancy_components import (
    render_vacancy_action_row,
    render_vacancy_analysis_panel,
    render_vacancy_detail_summary,
)

vacancy_repository = VacancyRepository()
application_repository = ApplicationRepository()
profile_repository = ProfileRepository()
analysis_repository = AnalysisRepository()
analyze_vacancy_use_case = AnalyzeVacancyUseCase(
    vacancy_repository=vacancy_repository,
    profile_repository=profile_repository,
    analysis_repository=analysis_repository,
)

def mostrar_mis_vacantes():
    inject_management_styles()
    st.subheader("Todas mis Vacantes")

    vacantes_raw = vacancy_repository.list_all()
    if not vacantes_raw:
        render_empty_state("No hay vacantes registradas aun. Comienza agregando una.")
        return

    analisis_por_vacante = {}
    for vacante in vacantes_raw:
        analisis = analysis_repository.get_by_vacancy_id(vacante["id"])
        if analisis:
            analisis_por_vacante[vacante["id"]] = analisis

    col_buscar, col_modal, col_estado = st.columns([2, 1, 1])
    with col_buscar:
        buscar = st.text_input("Buscar", placeholder="Empresa o cargo...", key="buscar_vacantes", label_visibility="collapsed")
    with col_modal:
        modalidad_filter = st.multiselect(
            "Modalidad",
            options=VACANCY_MODALITY_OPTIONS,
            default=VACANCY_MODALITY_OPTIONS,
            label_visibility="collapsed",
        )
    with col_estado:
        estado_filter = st.selectbox("Estado", options=VACANCY_FILTER_STATES, label_visibility="collapsed")

    datos_tabla = []
    for vacante in vacantes_raw:
        archivada = bool(vacante.get("motivo_archivo"))
        analisis = analisis_por_vacante.get(vacante["id"])
        semaforo = analisis["semaforo"] if analisis else "gris"
        score = f"{analisis['score_total']:.0f}" if analisis else "-"
        sem_meta = VACANCY_SEMAPHORE_META[semaforo]

        datos_tabla.append(
            {
                "ID": vacante["id"],
                "Semaforo": f"{sem_meta['emoji']} {score}",
                "Fecha": vacante["fecha_registro"].strftime("%d/%m/%Y") if vacante["fecha_registro"] else "N/A",
                "Cargo": vacante["cargo"],
                "Empresa": vacante["empresa"],
                "Modalidad": normalize_modality_label(vacante["modalidad"]),
                "Estado": "Archivada" if archivada else "Activa",
                "_id": vacante["id"],
                "_archivada": archivada,
            }
        )

    df = pd.DataFrame(datos_tabla)
    if buscar:
        q = buscar.lower()
        df = df[df["Empresa"].str.lower().str.contains(q, na=False) | df["Cargo"].str.lower().str.contains(q, na=False)]

    df = df[df["Modalidad"].isin(modalidad_filter)]
    if estado_filter == "Activas":
        df = df[~df["_archivada"]]
    elif estado_filter == "Archivadas":
        df = df[df["_archivada"]]

    st.write(f"Mostrando **{len(df)}** vacante(s)")
    cols_mostrar = ["ID", "Semaforo", "Fecha", "Cargo", "Empresa", "Modalidad", "Estado"]
    st.dataframe(df[cols_mostrar], use_container_width=True, hide_index=True, height=380)

    st.divider()
    if df.empty:
        render_empty_state("No hay vacantes que coincidan con los filtros.")
        return

    vacante_id_sel = st.selectbox(
        "Selecciona una vacante para ver detalles:",
        options=df["_id"].values,
        format_func=lambda x: next(
            (f"#{vacante['id']} - {vacante['empresa']} | {vacante['cargo']}" for vacante in vacantes_raw if vacante["id"] == x),
            str(x),
        ),
        label_visibility="collapsed",
    )

    if vacante_id_sel:
        vacante = next((item for item in vacantes_raw if item["id"] == vacante_id_sel), None)
        if vacante:
            _mostrar_detalle_vacante(vacante, analisis_por_vacante.get(vacante_id_sel))


def _mostrar_detalle_vacante(vacante: dict, analisis: dict | None):
    archivada = bool(vacante.get("motivo_archivo"))
    vacante_normalizada = {**vacante, "modalidad": normalize_modality_label(vacante.get("modalidad"))}

    st.subheader(f"{vacante_normalizada['empresa']} - {vacante_normalizada['cargo']}")
    render_vacancy_detail_summary(
        vacante_normalizada,
        archivada=archivada,
        modalidades_emoji={key: key for key in VACANCY_MODALITY_OPTIONS},
    )

    st.divider()
    if analisis:
        render_vacancy_analysis_panel(analisis)
        st.divider()

    with st.expander("Ver descripcion completa"):
        st.write(vacante_normalizada["descripcion"])

    st.divider()
    _mostrar_botones_accion(vacante, analisis, archivada)


def _mostrar_botones_accion(vacante: dict, analisis: dict | None, archivada: bool):
    vacante_id = vacante["id"]
    acciones = render_vacancy_action_row(vacante_id, analizada=bool(analisis), archivada=archivada)

    if acciones.get("analizar") or acciones.get("reanalizar"):
        _ejecutar_analisis(vacante)
    if acciones.get("aplicar"):
        _procesar_aplicar(vacante_id)
    if acciones.get("archivar"):
        st.session_state[f"show_archivar_{vacante_id}"] = True
    if acciones.get("reactivar"):
        res = vacancy_repository.unarchive(vacante_id)
        if res["success"]:
            st.success(res["message"])
            time.sleep(0.5)
            st.rerun()
        else:
            st.error(res["message"])
    if acciones.get("eliminar"):
        _procesar_eliminacion(vacante_id)

    if st.session_state.get(f"show_archivar_{vacante_id}"):
        _panel_archivar(vacante_id)


def _panel_archivar(vacante_id: int):
    st.markdown("**Por que archivas esta vacante?**")
    motivo = st.selectbox("Motivo", options=ARCHIVE_REASONS, key=f"motivo_archivo_{vacante_id}", label_visibility="collapsed")
    col_ok, col_cancel = st.columns(2)
    with col_ok:
        if st.button("Confirmar", use_container_width=True, type="primary", key=f"confirm_archivo_{vacante_id}"):
            res = vacancy_repository.archive(vacante_id, motivo)
            if res["success"]:
                st.success(res["message"])
                st.session_state.pop(f"show_archivar_{vacante_id}", None)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res["message"])
    with col_cancel:
        if st.button("Cancelar", use_container_width=True, key=f"cancel_archivo_{vacante_id}"):
            st.session_state.pop(f"show_archivar_{vacante_id}", None)
            st.rerun()


def _ejecutar_analisis(vacante: dict):
    try:
        resultado = analyze_vacancy_use_case.execute(vacante["id"])
    except Exception as exc:
        st.error(str(exc))
        return

    if resultado["success"] and resultado["analizado"]:
        st.success("Analisis completado")
        time.sleep(0.5)
        st.rerun()


def _procesar_aplicar(vacante_id: int):
    existente = application_repository.list_by_vacancy(vacante_id)
    if existente:
        st.warning("Ya tienes una aplicacion registrada para esta vacante.")
        return

    st.session_state["aplicar_vacante_id"] = vacante_id
    st.success("Ve a la pestana **Registrar Aplicacion** para completar los datos de tu aplicacion.")


def _procesar_eliminacion(vacante_id: int):
    resultado = vacancy_repository.delete(vacante_id)
    if resultado["success"]:
        st.success(resultado["message"])
        time.sleep(1)
        st.rerun()
    else:
        st.error(resultado["message"])
