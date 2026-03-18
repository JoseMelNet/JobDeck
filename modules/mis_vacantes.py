"""
modules/mis_vacantes.py — v2
Pestaña: Mis Vacantes

Novedades v2:
  - Columna Semáforo en la tabla (verde/amarillo/rojo/gris)
  - Filtro por estado: Activas | Archivadas | Todas
  - Botón "🔍 Analizar" en el detalle de cada vacante
  - Botones de decisión: ✅ Aplicar | 📦 Archivar
  - Spinner mientras OpenAI procesa
"""

import streamlit as st
import database
import pandas as pd
import time
from modules.analizar_vacante import analizar_vacante


# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

MOTIVOS_ARCHIVO = [
    'No calificado',
    'Sobre calificado',
    'Empresa no interesa',
    'Salario no acorde',
    'Otro',
]

SEMAFORO_META = {
    'verde':    {'emoji': '🟢', 'label': 'Alta afinidad',   'color': '#10B981'},
    'amarillo': {'emoji': '🟡', 'label': 'Afinidad media',  'color': '#F59E0B'},
    'rojo':     {'emoji': '🔴', 'label': 'Baja afinidad',   'color': '#EF4444'},
    'gris':     {'emoji': '⚪', 'label': 'Sin analizar',    'color': '#9CA3AF'},
}

MODALIDADES_EMOJI = {
    'Remoto':     '🌐 Remoto',
    'Presencial': '🏢 Presencial',
    'Híbrido':    '🔄 Híbrido',
}


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def mostrar_mis_vacantes():
    st.subheader("Todas mis Vacantes")

    vacantes_raw = database.obtener_todas_vacantes()

    if not vacantes_raw:
        st.info("📭 No hay vacantes registradas aún. ¡Comienza agregando una!")
        return

    # Cargar análisis existentes para mostrar semáforos en tabla
    analisis_por_vacante = {}
    for v in vacantes_raw:
        a = database.obtener_analisis_vacante(v['id'])
        if a:
            analisis_por_vacante[v['id']] = a

    # ── Filtro: activas / archivadas / todas ──────────────────
    col_buscar, col_modal, col_estado = st.columns([2, 1, 1])

    with col_buscar:
        buscar = st.text_input(
            "🔍 Buscar", placeholder="Empresa o cargo...",
            key="buscar_vacantes", label_visibility="collapsed"
        )
    with col_modal:
        modalidad_filter = st.multiselect(
            "Modalidad", options=['Remoto', 'Presencial', 'Híbrido'],
            default=['Remoto', 'Presencial', 'Híbrido'],
            label_visibility="collapsed"
        )
    with col_estado:
        estado_filter = st.selectbox(
            "Estado", options=['Activas', 'Archivadas', 'Todas'],
            label_visibility="collapsed"
        )

    # ── Construir DataFrame ───────────────────────────────────
    datos_tabla = []
    for v in vacantes_raw:
        archivada   = bool(v.get('motivo_archivo'))
        analisis    = analisis_por_vacante.get(v['id'])
        semaforo    = analisis['semaforo'] if analisis else 'gris'
        score       = f"{analisis['score_total']:.0f}" if analisis else '—'
        sem_meta    = SEMAFORO_META[semaforo]

        datos_tabla.append({
            'ID':           v['id'],
            'Semáforo':     f"{sem_meta['emoji']} {score}",
            'Fecha':        v['fecha_registro'].strftime("%d/%m/%Y") if v['fecha_registro'] else "N/A",
            'Cargo':        v['cargo'],
            'Empresa':      v['empresa'],
            'Modalidad':    v['modalidad'],
            'Estado':       '📦 Archivada' if archivada else '✅ Activa',
            '_id':          v['id'],
            '_archivada':   archivada,
            '_semaforo':    semaforo,
        })

    df = pd.DataFrame(datos_tabla)

    # Aplicar filtros
    if buscar:
        q = buscar.lower()
        df = df[df['Empresa'].str.lower().str.contains(q, na=False) |
                df['Cargo'].str.lower().str.contains(q, na=False)]

    df = df[df['Modalidad'].isin(modalidad_filter)]

    if estado_filter == 'Activas':
        df = df[~df['_archivada']]
    elif estado_filter == 'Archivadas':
        df = df[df['_archivada']]

    st.write(f"📊 Mostrando **{len(df)}** vacante(s)")

    # ── Tabla ─────────────────────────────────────────────────
    cols_mostrar = ['ID', 'Semáforo', 'Fecha', 'Cargo', 'Empresa', 'Modalidad', 'Estado']
    st.dataframe(df[cols_mostrar], use_container_width=True, hide_index=True, height=380)

    st.divider()

    # ── Selector de vacante ───────────────────────────────────
    if df.empty:
        st.info("No hay vacantes que coincidan con los filtros.")
        return

    vacante_id_sel = st.selectbox(
        "Selecciona una vacante para ver detalles:",
        options=df['_id'].values,
        format_func=lambda x: next(
            (f"#{v['id']} — {v['empresa']} | {v['cargo']}"
             for v in vacantes_raw if v['id'] == x), str(x)
        ),
        label_visibility="collapsed"
    )

    if vacante_id_sel:
        vacante = next((v for v in vacantes_raw if v['id'] == vacante_id_sel), None)
        if vacante:
            _mostrar_detalle_vacante(
                vacante,
                analisis_por_vacante.get(vacante_id_sel)
            )


# ─────────────────────────────────────────────────────────────
# DETALLE DE VACANTE
# ─────────────────────────────────────────────────────────────

def _mostrar_detalle_vacante(vacante: dict, analisis: dict):
    archivada = bool(vacante.get('motivo_archivo'))

    # ── Encabezado ────────────────────────────────────────────
    st.subheader(f"📋 {vacante['empresa']} — {vacante['cargo']}")

    # Fila 1: metadatos
    c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])
    with c1:
        st.write("**🆔 ID**");    st.write(f"`{vacante['id']}`")
    with c2:
        st.write("**🏢 Empresa**"); st.write(vacante['empresa'])
    with c3:
        st.write("**💼 Cargo**");   st.write(vacante['cargo'])
    with c4:
        st.write("**📍 Modalidad**")
        st.write(MODALIDADES_EMOJI.get(vacante['modalidad'], vacante['modalidad']))

    # Fila 2: fecha, link, estado
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    with c1:
        st.write("**📅 Registrada**")
        fecha = vacante['fecha_registro'].strftime("%d/%m/%Y") if vacante['fecha_registro'] else "N/A"
        st.write(fecha)
    with c2:
        st.write("**🔗 Link**")
        if vacante.get('link'):
            st.markdown(f"[Abrir ↗]({vacante['link']})")
        else:
            st.write("—")
    with c3:
        st.write("**📦 Estado**")
        if archivada:
            st.write(f"Archivada: *{vacante['motivo_archivo']}*")
        else:
            st.write("Activa")

    st.divider()

    # ── Panel de análisis (si existe) ─────────────────────────
    if analisis:
        _mostrar_panel_analisis(analisis)
        st.divider()

    # ── Descripción ───────────────────────────────────────────
    with st.expander("📝 Ver descripción completa"):
        st.write(vacante['descripcion'])

    st.divider()

    # ── Botones de acción ─────────────────────────────────────
    _mostrar_botones_accion(vacante, analisis, archivada)


# ─────────────────────────────────────────────────────────────
# PANEL DE ANÁLISIS
# ─────────────────────────────────────────────────────────────

def _mostrar_panel_analisis(analisis: dict):
    """Muestra el resultado del análisis: score, semáforo y breakdown."""
    sem    = analisis['semaforo']
    meta   = SEMAFORO_META[sem]
    score  = analisis['score_total']
    fecha  = analisis['fecha_analisis']
    fecha_str = fecha.strftime("%d/%m/%Y %H:%M") if fecha else "—"

    # Score principal
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:16px;margin-bottom:8px'>"
        f"<span style='font-size:2.2rem'>{meta['emoji']}</span>"
        f"<div>"
        f"<div style='font-size:1.4rem;font-weight:800;color:{meta['color']}'>"
        f"{score:.0f} / 100</div>"
        f"<div style='font-size:0.8rem;color:#6B7280'>{meta['label']} · "
        f"Analizado: {fecha_str}</div>"
        f"</div></div>",
        unsafe_allow_html=True
    )

    # Breakdown por dimensión
    dimensiones = [
        ("🛠️ Skills técnicas",  analisis['score_skills_tecnicas'], 40),
        ("📊 Seniority",         analisis['score_seniority'],       20),
        ("📍 Modalidad",         analisis['score_modalidad'],       15),
        ("🌐 Idiomas",           analisis['score_idiomas'],         10),
        ("🤝 Skills blandas",    analisis['score_skills_blandas'],  15),
    ]

    cols = st.columns(len(dimensiones))
    for i, (label, score_dim, peso) in enumerate(dimensiones):
        with cols[i]:
            color = '#10B981' if score_dim >= 70 else '#F59E0B' if score_dim >= 40 else '#EF4444'
            st.markdown(
                f"<div style='text-align:center'>"
                f"<div style='font-size:1.1rem;font-weight:700;color:{color}'>"
                f"{score_dim:.0f}</div>"
                f"<div style='font-size:0.65rem;color:#6B7280;line-height:1.3'>"
                f"{label}<br>peso {peso}%</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Skills match y gap
    if analisis.get('skills_match') or analisis.get('skills_gap'):
        st.markdown("")
        col_match, col_gap = st.columns(2)
        with col_match:
            if analisis.get('skills_match'):
                st.markdown("**✅ Skills que tienes:**")
                st.markdown(
                    ' '.join([f"`{s}`" for s in analisis['skills_match']])
                )
        with col_gap:
            if analisis.get('skills_gap'):
                st.markdown("**❌ Skills que te faltan:**")
                st.markdown(
                    ' '.join([f"`{s}`" for s in analisis['skills_gap']])
                )

    # Resumen narrativo
    if analisis.get('resumen_analisis'):
        with st.expander("📄 Ver resumen del análisis"):
            st.write(analisis['resumen_analisis'])
            c1, c2 = st.columns(2)
            with c1:
                if analisis.get('seniority_inferido'):
                    st.markdown(
                        f"**Seniority inferido:** {analisis['seniority_inferido']}"
                    )
                if analisis.get('salario_detectado'):
                    st.markdown(
                        f"**Salario en vacante:** {analisis['salario_detectado']}"
                    )
            with c2:
                if analisis.get('aspiracion_salarial_sugerida'):
                    st.markdown(
                        f"**Aspiración sugerida:** "
                        f"{analisis['aspiracion_salarial_sugerida']}"
                    )
                if analisis.get('modalidad_detectada'):
                    st.markdown(
                        f"**Modalidad detectada:** {analisis['modalidad_detectada']}"
                    )


# ─────────────────────────────────────────────────────────────
# BOTONES DE ACCIÓN
# ─────────────────────────────────────────────────────────────

def _mostrar_botones_accion(vacante: dict, analisis: dict, archivada: bool):
    """
    Botones de acción según el estado de la vacante:
    - Sin analizar:  🔍 Analizar | 🗑️ Eliminar
    - Analizada activa: 🔍 Re-analizar | ✅ Aplicar | 📦 Archivar | 🗑️ Eliminar
    - Archivada:     🔍 Re-analizar | ♻️ Reactivar | 🗑️ Eliminar
    """
    vacante_id = vacante['id']

    # ── Sin analizar ──────────────────────────────────────────
    if not analisis and not archivada:
        c1, c2 = st.columns([2, 1])
        with c1:
            if st.button("🔍 Analizar Afinidad", use_container_width=True, type="primary",
                         key=f"btn_analizar_{vacante_id}"):
                _ejecutar_analisis(vacante)
        with c2:
            if st.button("🗑️ Eliminar", use_container_width=True, type="secondary",
                         key=f"btn_del_{vacante_id}"):
                _procesar_eliminacion(vacante_id)
        return

    # ── Analizada activa ──────────────────────────────────────
    if analisis and not archivada:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🔍 Re-analizar", use_container_width=True,
                         key=f"btn_reanalizar_{vacante_id}"):
                _ejecutar_analisis(vacante)
        with c2:
            if st.button("✅ Aplicar", use_container_width=True, type="primary",
                         key=f"btn_aplicar_{vacante_id}"):
                _procesar_aplicar(vacante_id)
        with c3:
            if st.button("📦 Archivar", use_container_width=True,
                         key=f"btn_archivar_{vacante_id}"):
                st.session_state[f'show_archivar_{vacante_id}'] = True
        with c4:
            if st.button("🗑️ Eliminar", use_container_width=True, type="secondary",
                         key=f"btn_del_{vacante_id}"):
                _procesar_eliminacion(vacante_id)

        # Sub-panel archivar
        if st.session_state.get(f'show_archivar_{vacante_id}'):
            _panel_archivar(vacante_id)
        return

    # ── Archivada ─────────────────────────────────────────────
    if archivada:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔍 Re-analizar", use_container_width=True,
                         key=f"btn_reanalizar_{vacante_id}"):
                _ejecutar_analisis(vacante)
        with c2:
            if st.button("♻️ Reactivar", use_container_width=True, type="primary",
                         key=f"btn_reactivar_{vacante_id}"):
                res = database.desarchivar_vacante(vacante_id)
                if res['success']:
                    st.success(res['message'])
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(res['message'])
        with c3:
            if st.button("🗑️ Eliminar", use_container_width=True, type="secondary",
                         key=f"btn_del_{vacante_id}"):
                _procesar_eliminacion(vacante_id)


def _panel_archivar(vacante_id: int):
    """Sub-panel para seleccionar motivo de archivo."""
    st.markdown("**📦 ¿Por qué archivas esta vacante?**")
    motivo = st.selectbox(
        "Motivo", options=MOTIVOS_ARCHIVO,
        key=f"motivo_archivo_{vacante_id}",
        label_visibility="collapsed"
    )
    col_ok, col_cancel = st.columns(2)
    with col_ok:
        if st.button("Confirmar", use_container_width=True, type="primary",
                     key=f"confirm_archivo_{vacante_id}"):
            res = database.archivar_vacante(vacante_id, motivo)
            if res['success']:
                st.success(res['message'])
                st.session_state.pop(f'show_archivar_{vacante_id}', None)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])
    with col_cancel:
        if st.button("Cancelar", use_container_width=True,
                     key=f"cancel_archivo_{vacante_id}"):
            st.session_state.pop(f'show_archivar_{vacante_id}', None)
            st.rerun()


# ─────────────────────────────────────────────────────────────
# ACCIONES
# ─────────────────────────────────────────────────────────────

def _ejecutar_analisis(vacante: dict):
    """Llama al motor de análisis y guarda el resultado."""
    perfil = database.obtener_perfil()
    if not perfil:
        st.error("⚠️ No tienes un perfil creado. Ve a la pestaña **Mi Perfil**.")
        return

    perfil_completo = database.obtener_perfil_completo_para_analisis(perfil['id'])
    if not perfil_completo:
        st.error("⚠️ No se pudo cargar tu perfil completo.")
        return

    with st.spinner("🤖 Analizando vacante con IA... esto puede tomar unos segundos"):
        resultado = analizar_vacante(vacante, perfil_completo)

    if not resultado['success']:
        st.error(f"❌ {resultado['message']}")
        return

    res_db = database.guardar_analisis_vacante(
        vacante_id=vacante['id'],
        perfil_id=perfil['id'],
        analisis=resultado
    )

    if res_db['success']:
        st.success("✅ Análisis completado")
        time.sleep(0.5)
        st.rerun()
    else:
        st.error(f"❌ Error al guardar: {res_db['message']}")


def _procesar_aplicar(vacante_id: int):
    """
    Registra la aplicación a la vacante.
    Redirige al flujo de registrar_aplicacion con la vacante preseleccionada.
    """
    # Verificar que no exista ya una aplicación
    existente = database.obtener_aplicaciones_por_vacante(vacante_id)
    if existente:
        st.warning("⚠️ Ya tienes una aplicación registrada para esta vacante.")
        return

    # Guardar en session state para que registrar_aplicacion la preseleccione
    st.session_state['aplicar_vacante_id'] = vacante_id
    st.success(
        "✅ Ve a la pestaña **✉️ Registrar Aplicación** "
        "para completar los datos de tu aplicación. "
        "La vacante ya estará preseleccionada."
    )


def _procesar_eliminacion(vacante_id: int):
    resultado = database.eliminar_vacante(vacante_id)
    if resultado['success']:
        st.success(resultado['message'])
        time.sleep(1)
        st.rerun()
    else:
        st.error(resultado['message'])