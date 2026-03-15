"""
app.py - MVP: Sistema de Almacenamiento de Vacantes
Archivo principal: estructura base y composición de pestañas

Este archivo importa y organiza el contenido de cada pestaña
"""

import streamlit as st
import database
from modules.registrar_vacante import mostrar_registrar_vacante
from modules.mis_vacantes import mostrar_mis_vacantes

# ============================================================
# CONFIGURACIÓN STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Vacantes MVP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
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
""", unsafe_allow_html=True)

# ============================================================
# VERIFICAR CONEXIÓN A BD
# ============================================================
if not database.test_connection():
    st.error("""
    ❌ **No hay conexión a SQL Server**

    Por favor:
    1. Verifica que SQL Server esté corriendo
    2. Verifica credenciales en .env
    3. Ejecuta diagnostico_sql_server.py
    4. Recarga la aplicación (F5)
    """)
    st.stop()

# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================
st.markdown("<h1 class='header-main'>📋 Gestor de Vacantes</h1>", unsafe_allow_html=True)

# Contar vacantes DINÁMICAMENTE
total_vacantes = database.contar_vacantes()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Total Vacantes", total_vacantes)

# ============================================================
# PESTAÑAS: COMPOSICIÓN DE MÓDULOS
# ============================================================
tab1, tab2 = st.tabs(["➕ Registrar Vacante", "📰 Mis Vacantes"])

with tab1:
    mostrar_registrar_vacante()

with tab2:
    mostrar_mis_vacantes()

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray; font-size: 12px;'>"
    "MVP: Sistema de Almacenamiento de Vacantes | MSSQLSERVER2025"
    "</p>",
    unsafe_allow_html=True
)