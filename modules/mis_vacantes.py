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
from services import ejecutar_analisis_vacante


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
    """
    Panel de resultados del análisis v2.
    Muestra: decisión, afinidad, score, breakdown, fortalezas,
    riesgos, skills match/gap, encaje estratégico y ajustes CV.
    """

    # ── Metadatos del análisis ─────────────────────────────────
    AFINIDAD_META = {
        'Alta':  {'emoji': '🟢', 'color': '#10B981'},
        'Media': {'emoji': '🟡', 'color': '#F59E0B'},
        'Baja':  {'emoji': '🔴', 'color': '#EF4444'},
    }
    DECISION_META = {
        'Aplicar sí o sí':       {'emoji': '✅', 'color': '#10B981'},
        'Aplicar si sobra tiempo': {'emoji': '⏳', 'color': '#F59E0B'},
        'Descartar':              {'emoji': '❌', 'color': '#EF4444'},
    }
    ENCAJE_META = {
        'Alineado':                {'emoji': '🎯', 'color': '#10B981'},
        'Parcialmente alineado':   {'emoji': '↗️', 'color': '#F59E0B'},
        'Desvía del objetivo':     {'emoji': '↙️', 'color': '#EF4444'},
    }

    afinidad       = analisis.get('afinidad_general', '—')
    decision       = analisis.get('decision_aplicacion', '—')
    encaje         = analisis.get('encaje_estrategico', '—')
    score          = analisis.get('score_global') or analisis.get('score_total', 0)
    tipo_rol       = analisis.get('tipo_real_de_rol', '—')
    fecha          = analisis.get('fecha_analisis')
    fecha_str      = fecha.strftime("%d/%m/%Y %H:%M") if fecha else "—"

    af_meta  = AFINIDAD_META.get(afinidad,  {'emoji': '⚪', 'color': '#9CA3AF'})
    dec_meta = DECISION_META.get(decision,  {'emoji': '⚪', 'color': '#9CA3AF'})
    enc_meta = ENCAJE_META.get(encaje,      {'emoji': '⚪', 'color': '#9CA3AF'})

    # ── Fila principal: Decisión + Afinidad + Score ────────────
    st.markdown(
        f"""
        <div style='display:flex;gap:16px;align-items:stretch;margin-bottom:12px;flex-wrap:wrap'>

          <div style='flex:1;min-width:180px;background:#F9FAFB;border:1px solid #E5E7EB;
                      border-left:4px solid {dec_meta["color"]};border-radius:8px;padding:12px 16px'>
            <div style='font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:4px'>Decisión</div>
            <div style='font-size:1.1rem;font-weight:800;color:{dec_meta["color"]}'>
              {dec_meta["emoji"]} {decision}
            </div>
          </div>

          <div style='flex:1;min-width:140px;background:#F9FAFB;border:1px solid #E5E7EB;
                      border-left:4px solid {af_meta["color"]};border-radius:8px;padding:12px 16px'>
            <div style='font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:4px'>Afinidad</div>
            <div style='font-size:1.1rem;font-weight:800;color:{af_meta["color"]}'>
              {af_meta["emoji"]} {afinidad}
            </div>
          </div>

          <div style='flex:1;min-width:140px;background:#F9FAFB;border:1px solid #E5E7EB;
                      border-left:4px solid {enc_meta["color"]};border-radius:8px;padding:12px 16px'>
            <div style='font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:4px'>Encaje estratégico</div>
            <div style='font-size:1.0rem;font-weight:700;color:{enc_meta["color"]}'>
              {enc_meta["emoji"]} {encaje}
            </div>
          </div>

          <div style='flex:1;min-width:120px;background:#F9FAFB;border:1px solid #E5E7EB;
                      border-radius:8px;padding:12px 16px'>
            <div style='font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:4px'>Score global</div>
            <div style='font-size:1.3rem;font-weight:800;color:#111'>
              {score:.0f}<span style='font-size:0.8rem;color:#9CA3AF'>/100</span>
            </div>
            <div style='font-size:0.62rem;color:#9CA3AF'>{fecha_str}</div>
          </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Tipo de rol + seniority ────────────────────────────────
    seniority = analisis.get('seniority_inferido', '—')
    st.markdown(
        f"<div style='font-size:0.8rem;color:#555;margin-bottom:12px'>"
        f"🎭 <b>Tipo de rol:</b> {tipo_rol} &nbsp;·&nbsp; "
        f"📊 <b>Seniority inferido:</b> {seniority}</div>",
        unsafe_allow_html=True
    )

    # ── Justificación de la decisión ──────────────────────────
    if analisis.get('justificacion_decision'):
        st.info(f"💬 {analisis['justificacion_decision']}")

    # ── Breakdown de scores ───────────────────────────────────
    dimensiones = [
        ("🛠️ Skills",    analisis.get('score_skills_tecnicas', 0), "35%"),
        ("📊 Seniority", analisis.get('score_seniority', 0),       "25%"),
        ("🎯 Encaje",    analisis.get('score_skills_blandas', 0),  "20%"),
        ("🌐 Idiomas",   analisis.get('score_idiomas', 0),         "10%"),
        ("📍 Modalidad", analisis.get('score_modalidad', 0),       "10%"),
    ]
    cols = st.columns(len(dimensiones))
    for i, (label, val, peso) in enumerate(dimensiones):
        with cols[i]:
            color = '#10B981' if val >= 70 else '#F59E0B' if val >= 40 else '#EF4444'
            st.markdown(
                f"<div style='text-align:center'>"
                f"<div style='font-size:1.1rem;font-weight:700;color:{color}'>{val:.0f}</div>"
                f"<div style='font-size:0.62rem;color:#6B7280;line-height:1.4'>"
                f"{label}<br>peso {peso}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("")

    # ── Fortalezas y Riesgos ──────────────────────────────────
    col_fort, col_riesgo = st.columns(2)
    with col_fort:
        fortalezas = analisis.get('fortalezas_principales', [])
        if fortalezas:
            st.markdown("**✅ Fortalezas**")
            for f in fortalezas:
                st.markdown(f"- {f}")

    with col_riesgo:
        riesgos = analisis.get('riesgos_principales', [])
        if riesgos:
            st.markdown("**⚠️ Riesgos**")
            for r in riesgos:
                st.markdown(f"- {r}")

    # ── Skills Match y Gap ────────────────────────────────────
    col_match, col_gap = st.columns(2)
    with col_match:
        match = analisis.get('skills_match', [])
        if match:
            st.markdown("**🟢 Skills que tienes**")
            st.markdown(' '.join([f"`{s}`" for s in match]))

    with col_gap:
        gap = analisis.get('skills_gap', [])
        if gap:
            st.markdown("**🔴 Skills que te faltan**")
            st.markdown(' '.join([f"`{s}`" for s in gap]))

    # ── Ajustes de CV ─────────────────────────────────────────
    ajustes = analisis.get('ajustes_cv_recomendados', [])
    if ajustes:
        st.markdown("**📝 Ajustes recomendados para el CV**")
        for a in ajustes:
            st.markdown(f"- {a}")

    # ── Resumen narrativo y detalles ──────────────────────────
    with st.expander("📄 Ver análisis completo"):
        if analisis.get('resumen_analisis'):
            st.markdown("**Análisis del reclutador:**")
            st.write(analisis['resumen_analisis'])

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            if analisis.get('justificacion_seniority'):
                st.markdown(f"**Justificación seniority:** {analisis['justificacion_seniority']}")
            if analisis.get('justificacion_afinidad'):
                st.markdown(f"**Justificación afinidad:** {analisis['justificacion_afinidad']}")
            if analisis.get('salario_detectado'):
                st.markdown(f"**Salario en vacante:** {analisis['salario_detectado']}")
        with c2:
            if analisis.get('aspiracion_salarial_sugerida'):
                st.markdown(f"**Aspiración sugerida:** {analisis['aspiracion_salarial_sugerida']}")
            if analisis.get('modalidad_detectada'):
                st.markdown(f"**Modalidad detectada:** {analisis['modalidad_detectada']}")
            if analisis.get('encaje_estrategico'):
                st.markdown(f"**Encaje estratégico:** {analisis['encaje_estrategico']}")

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
    """Ejecuta el analisis reutilizando el servicio compartido."""
    resultado = ejecutar_analisis_vacante(vacante['id'], mostrar_ui=True)
    if resultado['success'] and resultado['analizado']:
        time.sleep(0.5)
        st.rerun()


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
