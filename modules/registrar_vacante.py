"""
pages/registrar_vacante.py - Pestaña: Registrar Nueva Vacante

Este módulo contiene toda la lógica para:
- Formulario de entrada
- Validación de datos
- Inserción en BD
- Limpieza de campos
"""

import streamlit as st
import database
from config import MODALIDADES
import time
from services import ejecutar_analisis_vacante


def mostrar_registrar_vacante():
    """
    Función principal que renderiza toda la pestaña de "Registrar Vacante"
    Se llama desde app.py
    """
    st.subheader("Agregar Nueva Vacante")

    # Inicializar session state para limpiar formulario
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0

    # ============================================================
    # FORMULARIO
    # ============================================================
    with st.form("form_vacante", clear_on_submit=False):
        col_left, col_right = st.columns(2)

        with col_left:
            empresa = st.text_input(
                "🏢 Empresa",
                placeholder="Ej: Google, Microsoft, Skydropx",
                key=f"empresa_{st.session_state.form_key}"
            )
            cargo = st.text_input(
                "💼 Cargo",
                placeholder="Ej: Data Analyst, BI Analyst",
                key=f"cargo_{st.session_state.form_key}"
            )

        with col_right:
            modalidad = st.selectbox(
                "📍 Modalidad",
                options=MODALIDADES,
                key=f"modalidad_{st.session_state.form_key}"
            )
            link = st.text_input(
                "🔗 Link de la Vacante",
                placeholder="https://www.ejemplo.com/vacante",
                key=f"link_{st.session_state.form_key}"
            )

        # Área de descripción
        descripcion = st.text_area(
            "📝 Descripción",
            placeholder="Pega aquí la descripción completa de la vacante...",
            height=200,
            key=f"descripcion_{st.session_state.form_key}"
        )

        # Botón de guardar
        btn_guardar = st.form_submit_button(
            "💾 Guardar Vacante",
            use_container_width=True,
            type="primary"
        )

    # ============================================================
    # PROCESAR GUARDADO
    # ============================================================
    if btn_guardar:
        _procesar_guardado(empresa, cargo, modalidad, link, descripcion)


def _procesar_guardado(empresa: str, cargo: str, modalidad: str, link: str, descripcion: str):
    """
    Valida datos y guarda la vacante en BD

    Parámetros:
    - empresa: Nombre de la empresa
    - cargo: Posición laboral
    - modalidad: Remoto/Presencial/Híbrido
    - link: URL de la vacante (opcional)
    - descripcion: Descripción completa
    """
    # Validar campos
    if not empresa or not cargo or not descripcion:
        st.error("⚠️ Por favor completa todos los campos requeridos")
        return

    # Guardar en BD
    resultado = database.insertar_vacante(
        empresa=empresa.strip(),
        cargo=cargo.strip(),
        modalidad=modalidad,
        link=link.strip() if link else None,
        descripcion=descripcion.strip()
    )

    if resultado['success']:
        vacante_id = resultado.get('id')
        if vacante_id:
            ejecutar_analisis_vacante(vacante_id, mostrar_ui=False)

        st.success(resultado['message'])
        st.balloons()

        # LIMPIAR FORMULARIO: Cambiar form_key para recrear widgets
        st.session_state.form_key += 1

        time.sleep(2)
        st.rerun()
    else:
        st.error(f"❌ {resultado['message']}")
