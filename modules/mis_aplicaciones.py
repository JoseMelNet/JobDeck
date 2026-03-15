"""
modules/mis_aplicaciones.py - Pestaña: Mis Aplicaciones

Funcionalidades:
- Estadísticas rápidas (Total, Pendientes, Entrevistas, Rechazadas, Ofertas)
- Tabla con filtros por estado y búsqueda por empresa/cargo
- Selector para ver tarjeta de detalles al hacer click en una fila
- Tarjeta con opciones: Editar estado, Editar todos los datos, Eliminar
"""

import streamlit as st
import database
import pandas as pd
import time


ESTADO_EMOJIS = {
    'Pending':        '⏳ Pending',
    'Applied':        '📤 Applied',
    'Technical Test': '🧪 Technical Test',
    'In Interview':   '🗓️ In Interview',
    'Done':           '✅ Done',
    'Rejected':       '❌ Rejected',
    'Open Offer':     '🎉 Open Offer',
}

ESTADOS = list(ESTADO_EMOJIS.keys())


def mostrar_mis_aplicaciones():
    """
    Función principal que renderiza la pestaña "Mis Aplicaciones".
    Se llama desde app.py.
    """
    st.subheader("Mis Aplicaciones")

    aplicaciones = database.obtener_todas_aplicaciones()

    # ============================================================
    # SIN APLICACIONES
    # ============================================================
    if not aplicaciones:
        st.info("📭 No has registrado ninguna aplicación aún.")
        return

    # ============================================================
    # ESTADÍSTICAS
    # ============================================================
    _mostrar_estadisticas(aplicaciones)

    st.divider()

    # ============================================================
    # FILTROS
    # ============================================================
    col_buscar, col_estado = st.columns([2, 1])

    with col_buscar:
        buscar = st.text_input(
            "🔍 Buscar por empresa o cargo:",
            placeholder="Ej: Google, Data Analyst",
            key="buscar_aplicaciones"
        )

    with col_estado:
        estados_sel = st.multiselect(
            "Filtrar por estado:",
            options=ESTADOS,
            default=ESTADOS,
            format_func=lambda x: ESTADO_EMOJIS[x],
        )

    # ============================================================
    # CONSTRUIR DATAFRAME
    # ============================================================
    datos = []
    for a in aplicaciones:
        datos.append({
            'ID':          a['id'],
            'Fecha':       a['fecha_aplicacion'].strftime("%d/%m/%Y") if a['fecha_aplicacion'] else "N/A",
            'Empresa':     a['empresa'],
            'Cargo':       a['cargo'],
            'Modalidad':   a['modalidad'],
            'Estado':      ESTADO_EMOJIS.get(a['estado'], a['estado']),
            'Recruiter':   a['nombre_recruiter'] or '-',
            'Notas':       (a['notas'] or '')[:50] + ('...' if a['notas'] and len(a['notas']) > 50 else ''),
            # Columnas internas (para filtro y selección)
            '_id':         a['id'],
            '_estado_raw': a['estado'],
        })

    df = pd.DataFrame(datos)

    # Aplicar filtros
    if buscar:
        mask = (
            df['Empresa'].str.contains(buscar, case=False, na=False) |
            df['Cargo'].str.contains(buscar, case=False, na=False)
        )
        df = df[mask]

    if estados_sel:
        df = df[df['_estado_raw'].isin(estados_sel)]

    # ============================================================
    # TABLA
    # ============================================================
    cols_visible = ['ID', 'Fecha', 'Empresa', 'Cargo', 'Modalidad', 'Estado', 'Recruiter', 'Notas']
    st.write(f"📊 Mostrando **{len(df)} aplicación(es)**  |  *Selecciona una fila para ver detalles:*")

    st.dataframe(
        df[cols_visible],
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    st.divider()

    # ============================================================
    # SELECTOR + TARJETA DE DETALLES
    # ============================================================
    if df.empty:
        st.info("No hay aplicaciones con los filtros seleccionados.")
        return

    # Inicializar session state
    if 'aplicacion_seleccionada' not in st.session_state:
        st.session_state.aplicacion_seleccionada = None
    if 'modo_edicion' not in st.session_state:
        st.session_state.modo_edicion = None  # None | 'estado' | 'datos'

    aplic_id_sel = st.selectbox(
        "ID de aplicación seleccionada:",
        options=df['_id'].values,
        format_func=lambda x: f"ID {x}  —  {df[df['_id']==x]['Empresa'].values[0]}  /  {df[df['_id']==x]['Cargo'].values[0]}",
        key="select_aplicacion",
        label_visibility="collapsed",
    )

    if aplic_id_sel:
        _mostrar_tarjeta_aplicacion(aplic_id_sel, aplicaciones)


# ============================================================
# ESTADÍSTICAS
# ============================================================
def _mostrar_estadisticas(aplicaciones: list):
    """Muestra métricas rápidas de las aplicaciones."""
    total          = len(aplicaciones)
    pending        = sum(1 for a in aplicaciones if a['estado'] == 'Pending')
    applied        = sum(1 for a in aplicaciones if a['estado'] == 'Applied')
    tech_test      = sum(1 for a in aplicaciones if a['estado'] == 'Technical Test')
    in_interview   = sum(1 for a in aplicaciones if a['estado'] == 'In Interview')
    done           = sum(1 for a in aplicaciones if a['estado'] == 'Done')
    rejected       = sum(1 for a in aplicaciones if a['estado'] == 'Rejected')
    open_offer     = sum(1 for a in aplicaciones if a['estado'] == 'Open Offer')

    # Fila 1: totales principales
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total",            total)
    c2.metric("⏳ Pending",          pending)
    c3.metric("📤 Applied",          applied)
    c4.metric("🧪 Technical Test",   tech_test)

    # Fila 2: estados avanzados
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("🗓️ In Interview",     in_interview)
    c6.metric("✅ Done",             done)
    c7.metric("❌ Rejected",         rejected)
    c8.metric("🎉 Open Offer",       open_offer)


# ============================================================
# TARJETA DE DETALLES
# ============================================================
def _mostrar_tarjeta_aplicacion(aplic_id: int, aplicaciones: list):
    """
    Renderiza la tarjeta de detalles de una aplicación seleccionada.
    Incluye botones para editar estado, editar datos completos y eliminar.
    """
    # Buscar la aplicación
    aplic = next((a for a in aplicaciones if a['id'] == aplic_id), None)
    if not aplic:
        st.error("Aplicación no encontrada.")
        return

    st.subheader(f"📋 {aplic['empresa']}  —  {aplic['cargo']}")

    # ---- FILA 1: datos de la vacante ----
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1.5])
    with c1:
        st.write("**🆔 ID**")
        st.write(f"`{aplic['id']}`")
    with c2:
        st.write("**🏢 Empresa**")
        st.write(aplic['empresa'])
    with c3:
        st.write("**💼 Cargo**")
        st.write(aplic['cargo'])
    with c4:
        st.write("**📍 Modalidad**")
        st.write(aplic['modalidad'])

    st.divider()

    # ---- FILA 2: datos de la aplicación ----
    c1, c2, c3 = st.columns([1.5, 1.5, 1.5])
    with c1:
        st.write("**📅 Fecha Aplicación**")
        st.write(aplic['fecha_aplicacion'].strftime("%d/%m/%Y") if aplic['fecha_aplicacion'] else "N/A")
    with c2:
        st.write("**📊 Estado**")
        st.write(ESTADO_EMOJIS.get(aplic['estado'], aplic['estado']))
    with c3:
        st.write("**🔗 Link Vacante**")
        if aplic.get('link'):
            st.markdown(f"[Abrir aquí]({aplic['link']})")
        else:
            st.write("-")

    st.divider()

    # ---- FILA 3: recruiter ----
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**👤 Recruiter**")
        st.write(aplic['nombre_recruiter'] or "—")
    with c2:
        st.write("**📧 Email**")
        st.write(aplic['email_recruiter'] or "—")
    with c3:
        st.write("**📞 Teléfono**")
        st.write(aplic['telefono_recruiter'] or "—")

    st.divider()

    # ---- NOTAS ----
    st.write("**📝 Notas:**")
    st.write(aplic['notas'] or "*(sin notas)*")

    st.divider()

    # ============================================================
    # MODO EDICIÓN
    # ============================================================
    modo = st.session_state.get('modo_edicion')

    # --- BOTONES DE ACCIÓN ---
    col_est, col_datos, col_elim, col_cerrar = st.columns([1.5, 1.5, 1.5, 1.5])

    with col_est:
        if st.button("✏️ Cambiar Estado", use_container_width=True):
            st.session_state.modo_edicion = 'estado' if modo != 'estado' else None
            st.rerun()

    with col_datos:
        if st.button("📝 Editar Datos", use_container_width=True):
            st.session_state.modo_edicion = 'datos' if modo != 'datos' else None
            st.rerun()

    with col_elim:
        if st.button("🗑️ Eliminar", use_container_width=True, type="secondary"):
            st.session_state.modo_edicion = 'confirmar_eliminar' if modo != 'confirmar_eliminar' else None
            st.rerun()

    with col_cerrar:
        if st.button("✖️ Cerrar", use_container_width=True):
            st.session_state.modo_edicion = None
            st.rerun()

    # ---- FORMULARIO: Cambiar Estado ----
    if modo == 'estado':
        st.markdown("#### ✏️ Cambiar Estado")
        with st.form("form_cambiar_estado"):
            nuevo_estado = st.selectbox(
                "Nuevo estado:",
                options=ESTADOS,
                index=ESTADOS.index(aplic['estado']) if aplic['estado'] in ESTADOS else 0,
                format_func=lambda x: ESTADO_EMOJIS[x],
            )
            btn_ok = st.form_submit_button("💾 Guardar Estado", type="primary")

        if btn_ok:
            res = database.actualizar_estado_aplicacion(aplic_id, nuevo_estado)
            if res['success']:
                st.success(res['message'])
                st.session_state.modo_edicion = None
                time.sleep(1)
                st.rerun()
            else:
                st.error(res['message'])

    # ---- FORMULARIO: Editar Datos Completos ----
    elif modo == 'datos':
        st.markdown("#### 📝 Editar Datos de la Aplicación")
        with st.form("form_editar_datos"):
            col_e, col_n = st.columns([1, 2])
            with col_e:
                edit_estado = st.selectbox(
                    "Estado:",
                    options=ESTADOS,
                    index=ESTADOS.index(aplic['estado']) if aplic['estado'] in ESTADOS else 0,
                    format_func=lambda x: ESTADO_EMOJIS[x],
                )
            with col_n:
                edit_nombre = st.text_input("Nombre Recruiter:", value=aplic['nombre_recruiter'] or "")

            col_em, col_tel = st.columns(2)
            with col_em:
                edit_email = st.text_input("Email Recruiter:", value=aplic['email_recruiter'] or "")
            with col_tel:
                edit_tel = st.text_input("Teléfono:", value=aplic['telefono_recruiter'] or "")

            edit_notas = st.text_area("Notas:", value=aplic['notas'] or "", height=120)

            btn_guardar = st.form_submit_button("💾 Guardar Cambios", type="primary")

        if btn_guardar:
            res = database.actualizar_datos_aplicacion(
                aplicacion_id=aplic_id,
                estado=edit_estado,
                nombre_recruiter=edit_nombre or None,
                email_recruiter=edit_email or None,
                telefono_recruiter=edit_tel or None,
                notas=edit_notas or None,
            )
            if res['success']:
                st.success(res['message'])
                st.session_state.modo_edicion = None
                time.sleep(1)
                st.rerun()
            else:
                st.error(res['message'])

    # ---- CONFIRMACIÓN: Eliminar ----
    elif modo == 'confirmar_eliminar':
        st.warning(f"⚠️ ¿Estás seguro de eliminar la aplicación **#{aplic_id}** ({aplic['empresa']} — {aplic['cargo']})?")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ Sí, eliminar", type="primary", use_container_width=True):
                res = database.eliminar_aplicacion(aplic_id)
                if res['success']:
                    st.success(res['message'])
                    st.session_state.modo_edicion = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res['message'])
        with col_no:
            if st.button("🚫 Cancelar", use_container_width=True):
                st.session_state.modo_edicion = None
                st.rerun()
