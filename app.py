"""Main Streamlit entrypoint."""

from __future__ import annotations

import streamlit as st

from app.infrastructure.persistence.connection import test_connection
from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from app.infrastructure.persistence.repositories.vacancy_repository import VacancyRepository
from modules.mis_aplicaciones import mostrar_mis_aplicaciones
from modules.mis_vacantes import mostrar_mis_vacantes
from modules.mi_perfil import mostrar_mi_perfil
from modules.registrar_aplicacion import mostrar_registrar_aplicacion
from modules.registrar_vacante import mostrar_registrar_vacante

vacancy_repository = VacancyRepository()
application_repository = ApplicationRepository()

st.set_page_config(
    page_title="Vacantes MVP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .header-main {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

if not test_connection():
    st.error(
        """
    ❌ **No hay conexión a SQL Server**

    Por favor:
    1. Verifica que SQL Server esté corriendo
    2. Verifica credenciales en .env
    3. Ejecuta diagnostico_sql_server.py
    4. Recarga la aplicación (F5)
    """
    )
    st.stop()

st.markdown("<h1 class='header-main'>📋 Gestor de Vacantes</h1>", unsafe_allow_html=True)

total_vacantes = vacancy_repository.count()
stats_aplicaciones = application_repository.count_by_status()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📊 Total Vacantes", total_vacantes)
with col2:
    st.metric("📋 Total Aplicaciones", stats_aplicaciones["Total"])
with col3:
    st.metric("🗓️ In Interview", stats_aplicaciones["In Interview"])
with col4:
    st.metric("🎉 Open Offer", stats_aplicaciones["Open Offer"])
with col5:
    st.metric("❌ Rejected", stats_aplicaciones["Rejected"])

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "➕ Registrar Vacante",
        "📰 Mis Vacantes",
        "✉️ Registrar Aplicación",
        "📂 Mis Aplicaciones",
        "👤 Mi Perfil",
    ]
)

with tab1:
    mostrar_registrar_vacante()

with tab2:
    mostrar_mis_vacantes()

with tab3:
    mostrar_registrar_aplicacion()

with tab4:
    mostrar_mis_aplicaciones()

with tab5:
    mostrar_mi_perfil()

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>"
    "MVP: Sistema de Almacenamiento de Vacantes | MSSQLSERVER2025"
    "</p>",
    unsafe_allow_html=True,
)
