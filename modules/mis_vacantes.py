"""
modules/mis_vacantes.py - Pestaña: Mis Vacantes (Click en tabla = Tarjeta)

Cambios:
- ✅ Eliminada sección "Acciones"
- ✅ Click en fila de tabla muestra tarjeta automáticamente
- ✅ Botón eliminar integrado en la tarjeta
"""

import streamlit as st
import database
import pandas as pd
import time


def mostrar_mis_vacantes():
    """
    Función principal que renderiza "Mis Vacantes"
    Se llama desde app.py
    """
    st.subheader("Todas mis Vacantes")

    # Obtener vacantes
    vacantes = database.obtener_todas_vacantes()

    # ============================================================
    # SIN VACANTES
    # ============================================================
    if not vacantes:
        st.info("📭 No hay vacantes registradas aún. ¡Comienza agregando una!")
        return

    # ============================================================
    # CON VACANTES: MOSTRAR CON DATAFRAME
    # ============================================================
    st.write(f"📊 Total: **{len(vacantes)} vacante(s)**")

    # Crear datos para la tabla
    datos_tabla = []
    for vacante in vacantes:
        datos_tabla.append({
            'ID': vacante['id'],
            'Fecha': vacante['fecha_registro'].strftime("%d/%m/%Y %H:%M") if vacante['fecha_registro'] else "N/A",
            'Cargo': vacante['cargo'],
            'Empresa': vacante['empresa'],
            'Modalidad': vacante['modalidad'],
            'Link': vacante['link'] if vacante['link'] else '-',
            'Descripción': vacante['descripcion'][:60] + "..." if len(vacante['descripcion']) > 60 else vacante[
                'descripcion'],
            '_id_interno': vacante['id'],
            '_desc_completa': vacante['descripcion']
        })

    df = pd.DataFrame(datos_tabla)

    # ============================================================
    # FILTROS
    # ============================================================
    col_buscar, col_modal = st.columns([2, 1])

    with col_buscar:
        buscar = st.text_input(
            "🔍 Buscar por empresa o cargo:",
            placeholder="Ej: Google, Data Analyst",
            key="buscar_vacantes"
        )

    with col_modal:
        modalidad_filter = st.multiselect(
            "Filtrar por modalidad:",
            options=['Remoto', 'Presencial', 'Híbrido'],
            default=['Remoto', 'Presencial', 'Híbrido']
        )

    # Aplicar filtros
    if buscar:
        df = df[
            (df['Empresa'].str.contains(buscar, case=False, na=False)) |
            (df['Cargo'].str.contains(buscar, case=False, na=False))
            ]

    df = df[df['Modalidad'].isin(modalidad_filter)]

    st.divider()

    # ============================================================
    # MOSTRAR TABLA (Clickeable)
    # ============================================================
    st.write("**Haz clic en una fila para ver detalles completos:**")

    cols_mostrar = ['ID', 'Fecha', 'Cargo', 'Empresa', 'Modalidad', 'Link', 'Descripción']
    st.dataframe(
        df[cols_mostrar],
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # ============================================================
    # SELECTOR OCULTO (funcional pero invisible)
    # ============================================================
    st.divider()

    # Inicializar session state si no existe
    if 'vacante_seleccionada' not in st.session_state:
        st.session_state.vacante_seleccionada = None

    # Selector oculto para detectar clicks
    vacante_id_actual = st.selectbox(
        "ID de vacante seleccionada:",
        options=df['_id_interno'].values,
        format_func=lambda x: f"ID {x}",
        key="select_vacante_oculto",
        label_visibility="collapsed"  # Oculta la etiqueta
    )

    # ============================================================
    # MOSTRAR TARJETA CON DETALLES
    # ============================================================
    if vacante_id_actual:
        _mostrar_detalles_vacante(vacante_id_actual, vacantes)


def _mostrar_detalles_vacante(vacante_id: int, vacantes: list):
    """
    Muestra los detalles de una vacante en tarjeta horizontal

    Parámetros:
    - vacante_id: ID de la vacante a mostrar
    - vacantes: Lista original de vacantes
    """
    # Encontrar la vacante
    vacante = None
    for v in vacantes:
        if v['id'] == vacante_id:
            vacante = v
            break

    if not vacante:
        st.error("Vacante no encontrada")
        return

    # ============================================================
    # TÍTULO DE LA TARJETA
    # ============================================================
    st.subheader(f"📋 {vacante['empresa']} - {vacante['cargo']}")

    # ============================================================
    # FILA 1: ID, Empresa, Cargo, Modalidad
    # ============================================================
    col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])

    with col1:
        st.write("**🆔 ID**")
        st.write(f"`{vacante['id']}`")

    with col2:
        st.write("**🏢 Empresa**")
        st.write(vacante['empresa'])

    with col3:
        st.write("**💼 Cargo**")
        st.write(vacante['cargo'])

    with col4:
        st.write("**📍 Modalidad**")
        st.write(_obtener_emoji_modalidad(vacante['modalidad']))

    st.divider()

    # ============================================================
    # FILA 2: Fecha, Link, Caracteres
    # ============================================================
    col1, col2, col3 = st.columns([1.5, 1.5, 2])

    with col1:
        st.write("**📅 Fecha Registro**")
        fecha = vacante['fecha_registro'].strftime("%d/%m/%Y %H:%M") if vacante['fecha_registro'] else "N/A"
        st.write(fecha)

    with col2:
        st.write("**🔗 Link**")
        if vacante['link']:
            st.markdown(f"[Abierto aquí]({vacante['link']})")
        else:
            st.write("-")

    with col3:
        st.write("**📊 Caracteres**")
        st.write(len(vacante['descripcion']))

    st.divider()

    # ============================================================
    # DESCRIPCIÓN COMPLETA (ANCHO COMPLETO)
    # ============================================================
    st.write("**📝 Descripción Completa:**")
    st.write(vacante['descripcion'])

    st.divider()

    # ============================================================
    # BOTONES: Eliminar + Cerrar
    # ============================================================
    col_eliminar, col_cerrar, col_espacio = st.columns([1.5, 1.5, 2])

    with col_eliminar:
        if st.button("🗑️ Eliminar esta Vacante", use_container_width=True, type="secondary"):
            _procesar_eliminacion(vacante_id)

    with col_cerrar:
        if st.button("✖️ Cerrar Detalles", use_container_width=True):
            st.session_state.vacante_seleccionada = None
            st.rerun()


def _obtener_emoji_modalidad(modalidad: str) -> str:
    """
    Devuelve el emoji y texto formateado según la modalidad

    Parámetro:
    - modalidad: String con la modalidad (Remoto, Presencial, Híbrido)

    Retorna:
    - String con emoji y texto
    """
    modalidades = {
        'Remoto': '🌐 Remoto',
        'Presencial': '🏢 Presencial',
        'Híbrido': '🔄 Híbrido'
    }
    return modalidades.get(modalidad, modalidad)


def _procesar_eliminacion(vacante_id: int):
    """
    Procesa la eliminación de una vacante

    Parámetro:
    - vacante_id: ID de la vacante a eliminar
    """
    resultado = database.eliminar_vacante(vacante_id)

    if resultado['success']:
        st.success(resultado['message'])
        time.sleep(1)
        st.rerun()
    else:
        st.error(resultado['message'])