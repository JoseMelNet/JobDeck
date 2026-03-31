"""Main Streamlit entrypoint for the profile page."""

from __future__ import annotations

import streamlit as st

from modules.profile_cv import render_profile_cv_tab
from modules.profile_shared import database, fmt_fecha
from modules.profile_tabs_background import (
    tab_certificaciones,
    tab_cursos,
    tab_educacion,
    tab_experiencia,
    tab_proyectos,
)
from modules.profile_tabs_primary import tab_datos_personales, tab_skills


def mostrar_mi_perfil():
    st.subheader("Mi Perfil Profesional")
    perfil = database.obtener_perfil()

    if not perfil:
        st.info("Aun no tienes un perfil creado. Completa la pestaña **Datos Personales** para comenzar.")

    tabs = st.tabs(
        [
            "Datos Personales",
            "Skills",
            "Experiencia",
            "Proyectos",
            "Educacion",
            "Cursos",
            "Certificaciones",
            "Vista CV",
        ]
    )
    perfil_id = perfil["id"] if perfil else None

    with tabs[0]:
        tab_datos_personales(perfil)
    with tabs[1]:
        tab_skills(perfil_id)
    with tabs[2]:
        tab_experiencia(perfil_id)
    with tabs[3]:
        tab_proyectos(perfil_id)
    with tabs[4]:
        tab_educacion(perfil_id)
    with tabs[5]:
        tab_cursos(perfil_id)
    with tabs[6]:
        tab_certificaciones(perfil_id)
    with tabs[7]:
        render_profile_cv_tab(perfil, perfil_id, database, fmt_fecha)
