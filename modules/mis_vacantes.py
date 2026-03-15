"""
pages/mis_vacantes_v2.py - Pestaña: Mis Vacantes (Versión Tabular)

Esta es una versión mejorada que muestra las vacantes en una tabla
con columnas: ID, Fecha, Cargo, Empresa, Modalidad, Link, Descripción

Características:
- Vista tabular clara
- Descripción expandible
- Todas las columnas visibles
- Más fácil de leer y buscar
"""

import streamlit as st
import database
import pandas as pd
import time


def mostrar_mis_vacantes():
    """
    Función principal que renderiza la versión tabular de "Mis Vacantes"
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
    # CON VACANTES: MOSTRAR EN TABLA
    # ============================================================
    st.write(f"📊 Total: **{len(vacantes)} vacante(s)**")
    st.divider()

    # Crear datos para la tabla
    datos_tabla = []
    for vacante in vacantes:
        datos_tabla.append({
            'ID': vacante['id'],
            'Fecha': vacante['fecha_registro'].strftime("%d/%m/%Y %H:%M") if vacante['fecha_registro'] else "N/A",
            'Cargo': vacante['cargo'],
            'Empresa': vacante['empresa'],
            'Modalidad': _obtener_emoji_modalidad(vacante['modalidad']),
            'Link': vacante['link'],
            'Descripción': vacante['descripcion'],
            'ID_BD': vacante['id']  # Para el botón eliminar
        })

    # Crear DataFrame
    df = pd.DataFrame(datos_tabla)

    # ============================================================
    # MOSTRAR TABLA INTERACTIVA
    # ============================================================
    _mostrar_tabla_vacantes(df, vacantes)


def _mostrar_tabla_vacantes(df: pd.DataFrame, vacantes: list):
    """
    Renderiza la tabla de vacantes con filas expandibles

    Parámetro:
    - df: DataFrame con datos formateados
    - vacantes: Lista original de vacantes (con todos los datos)
    """
    # Crear columnas para la tabla
    col_id, col_fecha, col_cargo, col_empresa, col_modal, col_link, col_desc, col_acciones = st.columns(
        [1, 2, 2.5, 2.5, 1.5, 1.5, 3, 1.2]
    )

    # HEADER DE LA TABLA
    with col_id:
        st.write("**🆔 ID**")
    with col_fecha:
        st.write("**📅 Fecha**")
    with col_cargo:
        st.write("**💼 Cargo**")
    with col_empresa:
        st.write("**🏢 Empresa**")
    with col_modal:
        st.write("**📍 Modalidad**")
    with col_link:
        st.write("**🔗 Link**")
    with col_desc:
        st.write("**📝 Descripción**")
    with col_acciones:
        st.write("**Acciones**")

    st.divider()

    # FILAS DE LA TABLA
    for idx, (_, row) in enumerate(df.iterrows()):
        vacante = vacantes[idx]

        col_id, col_fecha, col_cargo, col_empresa, col_modal, col_link, col_desc, col_acciones = st.columns(
            [1, 2, 2.5, 2.5, 1.5, 1.5, 3, 1.2]
        )

        # ID
        with col_id:
            st.write(f"`{row['ID']}`")

        # FECHA
        with col_fecha:
            st.write(row['Fecha'])

        # CARGO
        with col_cargo:
            st.write(row['Cargo'])

        # EMPRESA
        with col_empresa:
            st.write(row['Empresa'])

        # MODALIDAD
        with col_modal:
            st.write(row['Modalidad'])

        # LINK
        with col_link:
            if row['Link']:
                st.markdown(f"[🔗 Ir]({row['Link']})")
            else:
                st.write("-")

        # DESCRIPCIÓN (EXPANDIBLE)
        with col_desc:
            desc = row['Descripción']
            # Mostrar primeros 50 caracteres
            preview = desc[:50] + "..." if len(desc) > 50 else desc
            with st.expander(preview):
                st.write(desc)

        # ACCIONES (BOTÓN ELIMINAR)
        with col_acciones:
            if st.button("🗑️", key=f"del_{row['ID_BD']}", help="Eliminar vacante"):
                _procesar_eliminacion(row['ID_BD'])

        st.divider()


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