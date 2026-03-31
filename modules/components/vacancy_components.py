"""Specific UI components for vacancy screens."""

from __future__ import annotations

import streamlit as st

from modules.components.profile_components import render_delete_button


def render_vacancy_detail_summary(vacante: dict, *, archivada: bool, modalidades_emoji: dict[str, str]) -> None:
    fecha = vacante["fecha_registro"].strftime("%d/%m/%Y") if vacante["fecha_registro"] else "N/A"
    estado = f"Archivada: {vacante['motivo_archivo']}" if archivada else "Activa"
    cards = [
        ("ID", str(vacante["id"])),
        ("Empresa", vacante["empresa"]),
        ("Cargo", vacante["cargo"]),
        ("Modalidad", modalidades_emoji.get(vacante["modalidad"], vacante["modalidad"])),
        ("Registrada", fecha),
        ("Estado", estado),
    ]
    html_cards = "".join(
        f"<div class='info-card'><div class='info-label'>{label}</div><div class='info-value'>{value}</div></div>"
        for label, value in cards
    )
    st.markdown(f"<div class='info-grid'>{html_cards}</div>", unsafe_allow_html=True)
    if vacante.get("link"):
        st.markdown(f"**Link:** [Abrir]({vacante['link']})")
    else:
        st.markdown("**Link:** -")


def render_vacancy_analysis_panel(analisis: dict) -> None:
    st.markdown("**Resultado del analisis**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Score", f"{(analisis.get('score_global') or analisis.get('score_total', 0)):.0f}")
    with c2:
        st.metric("Afinidad", analisis.get("afinidad_general", "-"))
    with c3:
        st.metric("Decision", analisis.get("decision_aplicacion", "-"))
    with c4:
        st.metric("Semaforo", analisis.get("semaforo", "gris"))

    if analisis.get("justificacion_decision"):
        st.info(analisis["justificacion_decision"])

    fortalezas = analisis.get("fortalezas_principales", [])
    if fortalezas:
        st.markdown("**Fortalezas**")
        for item in fortalezas:
            st.markdown(f"- {item}")

    riesgos = analisis.get("riesgos_principales", [])
    if riesgos:
        st.markdown("**Riesgos**")
        for item in riesgos:
            st.markdown(f"- {item}")

    ajustes = analisis.get("ajustes_cv_recomendados", [])
    if ajustes:
        st.markdown("**Ajustes recomendados para el CV**")
        for item in ajustes:
            st.markdown(f"- {item}")


def render_vacancy_action_row(vacante_id: int, *, analizada: bool, archivada: bool) -> dict[str, bool]:
    if not analizada and not archivada:
        c1, c2 = st.columns([2, 1])
        with c1:
            analizar = st.button("Analizar Afinidad", use_container_width=True, type="primary", key=f"btn_analizar_{vacante_id}")
        with c2:
            eliminar = render_delete_button(key=f"btn_del_{vacante_id}", use_container_width=True)
        return {"analizar": analizar, "eliminar": eliminar}

    if analizada and not archivada:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            reanalizar = st.button("Re-analizar", use_container_width=True, key=f"btn_reanalizar_{vacante_id}")
        with c2:
            aplicar = st.button("Aplicar", use_container_width=True, type="primary", key=f"btn_aplicar_{vacante_id}")
        with c3:
            archivar = st.button("Archivar", use_container_width=True, key=f"btn_archivar_{vacante_id}")
        with c4:
            eliminar = render_delete_button(key=f"btn_del_{vacante_id}", use_container_width=True)
        return {
            "reanalizar": reanalizar,
            "aplicar": aplicar,
            "archivar": archivar,
            "eliminar": eliminar,
        }

    c1, c2, c3 = st.columns(3)
    with c1:
        reanalizar = st.button("Re-analizar", use_container_width=True, key=f"btn_reanalizar_{vacante_id}")
    with c2:
        reactivar = st.button("Reactivar", use_container_width=True, type="primary", key=f"btn_reactivar_{vacante_id}")
    with c3:
        eliminar = render_delete_button(key=f"btn_del_{vacante_id}", use_container_width=True)
    return {"reanalizar": reanalizar, "reactivar": reactivar, "eliminar": eliminar}
