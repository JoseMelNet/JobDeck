"""
modules/mis_aplicaciones_v2.py
Tablero Kanban visual para gestión de aplicaciones.

Sin dependencias extras — solo Streamlit nativo.

Interacción principal:
  - Selectbox "Mover a →" en cada tarjeta para cambiar estado al instante
  - Botón "Ver" para abrir panel de detalles con edición completa y eliminar
"""

import streamlit as st
import database
import time

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

ESTADOS_ORDEN = [
    "Pending",
    "Applied",
    "Technical Test",
    "In Interview",
    "Done",
    "Rejected",
    "Open Offer",
]

ESTADO_META = {
    "Pending":        {"emoji": "⏳", "color": "#6B7280", "bg": "#F3F4F6"},
    "Applied":        {"emoji": "📤", "color": "#3B82F6", "bg": "#EFF6FF"},
    "Technical Test": {"emoji": "🧪", "color": "#A855F7", "bg": "#FAF5FF"},
    "In Interview":   {"emoji": "🗓️", "color": "#F59E0B", "bg": "#FFFBEB"},
    "Done":           {"emoji": "✅", "color": "#10B981", "bg": "#ECFDF5"},
    "Rejected":       {"emoji": "❌", "color": "#EF4444", "bg": "#FFF1F2"},
    "Open Offer":     {"emoji": "🎉", "color": "#EC4899", "bg": "#FDF4FF"},
}

MODALIDAD_META = {
    "Remoto":     {"emoji": "🌐", "color": "#3B82F6"},
    "Presencial": {"emoji": "🏢", "color": "#EF4444"},
    "Híbrido":    {"emoji": "🔄", "color": "#A855F7"},
}

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────

KANBAN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

/* ── Columna ─────────────────────────────────────────────── */
.kcol-header {
    background: var(--col-bg);
    border: 1px solid var(--col-color)55;
    border-top: 3px solid var(--col-color);
    border-radius: 8px;
    padding: 7px 10px 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
}
.kcol-title {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 0.7rem;
    color: var(--col-color);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    text-shadow: none;
}
.kcol-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--col-color);
    background: var(--col-bg);
    padding: 1px 7px;
    border-radius: 99px;
    border: 1px solid var(--col-color)55;
}

/* ── Tarjeta ─────────────────────────────────────────────── */
.kcard {
    background: #ffffff;
    border: 1px solid #E5E7EB;
    border-left: 3px solid var(--card-color);
    border-radius: 7px;
    padding: 9px 11px 7px;
    margin-bottom: 5px;
    font-family: 'Sora', sans-serif;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kcard:hover {
    border-color: var(--card-color);
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}
.kcard-cargo {
    font-weight: 600;
    font-size: 0.8rem;
    color: #111827;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kcard-empresa {
    font-size: 0.7rem;
    color: #6B7280;
    margin-bottom: 6px;
}
.kbadge {
    display: inline-block;
    font-size: 0.58rem;
    padding: 1px 6px;
    border-radius: 99px;
    font-weight: 700;
    letter-spacing: 0.03em;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 6px;
}
.kcard-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2px;
}
.kcard-fecha {
    font-size: 0.6rem;
    color: #9CA3AF;
    font-family: 'JetBrains Mono', monospace;
}
.kcard-link a {
    font-size: 0.6rem;
    color: #58A6FF;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
}
.kcard-link a:hover { color: #79C0FF; }

/* ── Panel de detalles ───────────────────────────────────── */
.detail-label {
    font-size: 0.58rem;
    color: #6E7681;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 2px;
}
.detail-value {
    font-size: 0.84rem;
    color: #C9D1D9;
    font-family: 'Sora', sans-serif;
    margin-bottom: 10px;
}
.notas-box {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 0.8rem;
    color: #8B949E;
    line-height: 1.65;
    white-space: pre-wrap;
    font-family: 'Sora', sans-serif;
    margin-top: 4px;
}
</style>
"""


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def mostrar_mis_aplicaciones():
    """
    Función principal del tablero kanban.
    Se llama desde app.py en la pestaña "Mis Aplicaciones".
    """
    st.markdown(KANBAN_CSS, unsafe_allow_html=True)
    st.subheader("Mis Aplicaciones")

    aplicaciones = database.obtener_todas_aplicaciones()

    if not aplicaciones:
        st.info("📭 No has registrado ninguna aplicación aún.")
        return

    # ── Session state ────────────────────────────────────────
    if "k_detail_id"   not in st.session_state:
        st.session_state.k_detail_id   = None   # ID del panel de detalles abierto
    if "k_detail_modo" not in st.session_state:
        st.session_state.k_detail_modo = None   # None | 'datos' | 'eliminar'

    # ── Filtros ──────────────────────────────────────────────
    aplicaciones_filtradas, estados_visibles = _mostrar_filtros(aplicaciones)

    # ── Panel de detalles (encima del kanban cuando está abierto) ──
    if st.session_state.k_detail_id is not None:
        _mostrar_panel_detalles(st.session_state.k_detail_id, aplicaciones)
        st.divider()

    # ── Kanban ───────────────────────────────────────────────
    _mostrar_kanban(aplicaciones_filtradas, estados_visibles)


# ─────────────────────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────────────────────

def _mostrar_filtros(aplicaciones: list) -> tuple:
    """
    Barra de búsqueda (empresa/cargo) + multiselect de columnas visibles.
    Retorna (aplicaciones_filtradas, estados_visibles).
    """
    col_buscar, col_estados = st.columns([2, 3])

    with col_buscar:
        buscar = st.text_input(
            "🔍 Buscar",
            placeholder="Buscar por empresa o cargo...",
            label_visibility="collapsed",
            key="kanban_buscar",
        )

    with col_estados:
        estados_sel = st.multiselect(
            "Columnas:",
            options=ESTADOS_ORDEN,
            default=ESTADOS_ORDEN,
            format_func=lambda x: f"{ESTADO_META[x]['emoji']} {x}",
            label_visibility="collapsed",
            key="kanban_estados_sel",
        )

    # Filtro de búsqueda case-insensitive
    if buscar:
        q = buscar.lower()
        aplicaciones = [
            a for a in aplicaciones
            if q in a["empresa"].lower() or q in a["cargo"].lower()
        ]

    return aplicaciones, estados_sel or ESTADOS_ORDEN


# ─────────────────────────────────────────────────────────────
# KANBAN BOARD
# ─────────────────────────────────────────────────────────────

def _mostrar_kanban(aplicaciones: list, estados_visibles: list):
    """
    Renderiza las columnas del kanban con sus tarjetas.
    Número de columnas = número de estados visibles seleccionados.
    """
    # Agrupar por estado, más recientes primero
    grupos: dict[str, list] = {e: [] for e in ESTADOS_ORDEN}
    for a in sorted(
        aplicaciones,
        key=lambda x: x["fecha_aplicacion"] or "",
        reverse=True,
    ):
        if a["estado"] in grupos:
            grupos[a["estado"]].append(a)

    cols = st.columns(len(estados_visibles))

    for i, estado in enumerate(estados_visibles):
        meta = ESTADO_META[estado]
        apps = grupos[estado]

        with cols[i]:
            # Header con estilos inline directos (CSS vars no funcionan cross-scope en Streamlit)
            st.markdown(
                f'<div style="'
                f'  background:{meta["bg"]};'
                f'  border:1px solid {meta["color"]}55;'
                f'  border-top:3px solid {meta["color"]};'
                f'  border-radius:8px;'
                f'  padding:7px 10px 8px;'
                f'  display:flex;'
                f'  align-items:center;'
                f'  justify-content:space-between;'
                f'  margin-bottom:8px;">'
                f'  <span style="font-family:Sora,sans-serif;font-weight:700;font-size:0.7rem;'
                f'    color:{meta["color"]};letter-spacing:0.06em;text-transform:uppercase;">'
                f'    {meta["emoji"]} {estado}'
                f'  </span>'
                f'  <span style="font-family:monospace;font-size:0.65rem;'
                f'    color:{meta["color"]};background:{meta["bg"]};'
                f'    padding:1px 7px;border-radius:99px;'
                f'    border:1px solid {meta["color"]}55;">'
                f'    {len(apps)}'
                f'  </span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if not apps:
                st.markdown(
                    '<p style="color:#3D444D;font-size:0.7rem;font-style:italic;'
                    'text-align:center;margin:6px 0 2px;">vacío</p>',
                    unsafe_allow_html=True,
                )
            else:
                for a in apps:
                    _renderizar_tarjeta(a, meta, estado)


def _renderizar_tarjeta(a: dict, meta: dict, estado_actual: str):
    """
    Renderiza una tarjeta individual.

    Controles interactivos (fuera del HTML puro):
      - Selectbox "Mover a →"  → cambia estado en BD al instante
      - Botón "🔍 Ver"          → abre/cierra el panel de detalles
    """
    modal_meta = MODALIDAD_META.get(a["modalidad"], {"emoji": "📍", "color": "#6B7280"})
    fecha_str  = a["fecha_aplicacion"].strftime("%d/%m/%Y") if a["fecha_aplicacion"] else "—"
    link_html  = (
        f'<span class="kcard-link"><a href="{a["link"]}" target="_blank">🔗 Abrir</a></span>'
        if a.get("link") else ""
    )

    # HTML visual de la tarjeta — border-left inline para que el color aplique
    st.markdown(
        f'<div class="kcard" style="border-left:3px solid {meta["color"]}">'
        f'  <div class="kcard-cargo" title="{a["cargo"]}">{a["cargo"]}</div>'
        f'  <div class="kcard-empresa">{a["empresa"]}</div>'
        f'  <span class="kbadge" style="'
        f'      background:{modal_meta["color"]}22;'
        f'      color:{modal_meta["color"]};'
        f'      border:1px solid {modal_meta["color"]}55">'
        f'    {modal_meta["emoji"]} {a["modalidad"]}'
        f'  </span>'
        f'  <div class="kcard-footer">'
        f'    <span class="kcard-fecha">📅 {fecha_str}</span>'
        f'    {link_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Selectbox "Mover a →"
    # Las opciones son todos los estados excepto el actual
    otros = [e for e in ESTADOS_ORDEN if e != estado_actual]
    opciones = ["Mover a →"] + [f"{ESTADO_META[e]['emoji']} {e}" for e in otros]

    sel = st.selectbox(
        label="estado",
        options=opciones,
        index=0,
        key=f"mover_{a['id']}",
        label_visibility="collapsed",
    )

    if sel != "Mover a →":
        # "📤 Applied" → "Applied"
        nuevo_estado = sel.split(" ", 1)[1]
        _procesar_cambio_estado(a["id"], nuevo_estado)

    # Botón Ver / Cerrar (toggle)
    es_el_abierto = st.session_state.k_detail_id == a["id"]
    label_btn     = "✖️ Cerrar" if es_el_abierto else "🔍 Ver"

    if st.button(label_btn, key=f"ver_{a['id']}", use_container_width=True):
        if es_el_abierto:
            st.session_state.k_detail_id   = None
            st.session_state.k_detail_modo = None
        else:
            st.session_state.k_detail_id   = a["id"]
            st.session_state.k_detail_modo = None
        st.rerun()


# ─────────────────────────────────────────────────────────────
# PANEL DE DETALLES
# ─────────────────────────────────────────────────────────────

def _mostrar_panel_detalles(app_id: int, aplicaciones: list):
    """
    Panel expandido de una aplicación.
    Aparece encima del kanban. Contiene edición de datos y eliminar.
    """
    a = next((x for x in aplicaciones if x["id"] == app_id), None)
    if not a:
        st.session_state.k_detail_id = None
        return

    meta       = ESTADO_META.get(a["estado"], ESTADO_META["Pending"])
    modal_meta = MODALIDAD_META.get(a["modalidad"], {"emoji": "📍", "color": "#6B7280"})
    fecha_str  = a["fecha_aplicacion"].strftime("%d/%m/%Y") if a["fecha_aplicacion"] else "—"

    with st.container(border=True):

        # Título + cerrar
        col_h, col_x = st.columns([6, 1])
        with col_h:
            st.markdown(
                f"**{a['cargo']}**  \n"
                f"<span style='color:#8B949E;font-size:0.85rem'>{a['empresa']} &nbsp;·&nbsp; "
                f"<span style='color:{meta['color']}'>{meta['emoji']} {a['estado']}</span></span>",
                unsafe_allow_html=True,
            )
        with col_x:
            if st.button("✖️ Cerrar", key="detail_cerrar", use_container_width=True):
                st.session_state.k_detail_id   = None
                st.session_state.k_detail_modo = None
                st.rerun()

        # Datos en grid
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("<div class='detail-label'>🆔 ID</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'><code>{a['id']}</code></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='detail-label'>📍 Modalidad</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='detail-value' style='color:{modal_meta['color']}'>"
                f"{modal_meta['emoji']} {a['modalidad']}</div>",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown("<div class='detail-label'>📅 Fecha</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'>{fecha_str}</div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='detail-label'>🔗 Link</div>", unsafe_allow_html=True)
            if a.get("link"):
                st.markdown(
                    f"<div class='detail-value'>"
                    f"<a href='{a['link']}' target='_blank' style='color:#58A6FF'>Abrir ↗</a>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown("<div class='detail-value' style='color:#6E7681'>—</div>", unsafe_allow_html=True)

        st.divider()

        # Recruiter
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown("<div class='detail-label'>👤 Recruiter</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'>{a['nombre_recruiter'] or '—'}</div>", unsafe_allow_html=True)
        with r2:
            st.markdown("<div class='detail-label'>📧 Email</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'>{a['email_recruiter'] or '—'}</div>", unsafe_allow_html=True)
        with r3:
            st.markdown("<div class='detail-label'>📞 Teléfono</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='detail-value'>{a['telefono_recruiter'] or '—'}</div>", unsafe_allow_html=True)

        # Notas
        st.markdown("<div class='detail-label' style='margin-top:6px'>📝 Notas</div>", unsafe_allow_html=True)
        if a["notas"]:
            st.markdown(f"<div class='notas-box'>{a['notas']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                "<span style='color:#6E7681;font-style:italic;font-size:0.8rem'>Sin notas</span>",
                unsafe_allow_html=True,
            )

        st.divider()

        # Botones de acción
        modo = st.session_state.k_detail_modo
        b1, b2, _ = st.columns([1.4, 1.4, 3])

        with b1:
            if st.button("📝 Editar datos", use_container_width=True, key="detail_btn_editar"):
                st.session_state.k_detail_modo = "datos" if modo != "datos" else None
                st.rerun()
        with b2:
            if st.button("🗑️ Eliminar", use_container_width=True, type="secondary", key="detail_btn_eliminar"):
                st.session_state.k_detail_modo = "eliminar" if modo != "eliminar" else None
                st.rerun()

        # Sub-panel: Editar datos
        if modo == "datos":
            st.markdown("##### 📝 Editar Datos")
            with st.form("form_detail_datos"):
                col_e, col_n = st.columns([1, 2])
                with col_e:
                    edit_estado = st.selectbox(
                        "Estado:",
                        options=ESTADOS_ORDEN,
                        index=ESTADOS_ORDEN.index(a["estado"]) if a["estado"] in ESTADOS_ORDEN else 0,
                        format_func=lambda x: f"{ESTADO_META[x]['emoji']} {x}",
                    )
                with col_n:
                    edit_nombre = st.text_input("Nombre Recruiter:", value=a["nombre_recruiter"] or "")

                col_em, col_tel = st.columns(2)
                with col_em:
                    edit_email = st.text_input("Email:", value=a["email_recruiter"] or "")
                with col_tel:
                    edit_tel = st.text_input("Teléfono:", value=a["telefono_recruiter"] or "")

                edit_notas = st.text_area("Notas:", value=a["notas"] or "", height=110)

                if st.form_submit_button("💾 Guardar cambios", type="primary"):
                    res = database.actualizar_datos_aplicacion(
                        aplicacion_id=a["id"],
                        estado=edit_estado,
                        nombre_recruiter=edit_nombre or None,
                        email_recruiter=edit_email or None,
                        telefono_recruiter=edit_tel or None,
                        notas=edit_notas or None,
                    )
                    if res["success"]:
                        st.success(res["message"])
                        st.session_state.k_detail_modo = None
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(res["message"])

        # Sub-panel: Confirmar eliminar
        elif modo == "eliminar":
            st.warning(
                f"⚠️ ¿Eliminar **#{a['id']} — {a['empresa']} / {a['cargo']}**? "
                f"Esta acción no se puede deshacer."
            )
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("✅ Sí, eliminar", type="primary", use_container_width=True, key="detail_si"):
                    _procesar_eliminacion(a["id"])
            with col_no:
                if st.button("🚫 Cancelar", use_container_width=True, key="detail_no"):
                    st.session_state.k_detail_modo = None
                    st.rerun()


# ─────────────────────────────────────────────────────────────
# HELPERS DE BD
# ─────────────────────────────────────────────────────────────

def _procesar_cambio_estado(app_id: int, nuevo_estado: str):
    """Actualiza el estado en BD, muestra toast y recarga."""
    res = database.actualizar_estado_aplicacion(app_id, nuevo_estado)
    if res["success"]:
        st.toast(f"✅ Movido a {nuevo_estado}", icon="✅")
        time.sleep(0.3)
        st.rerun()
    else:
        st.error(f"❌ {res['message']}")


def _procesar_eliminacion(app_id: int):
    """Elimina la aplicación, cierra el panel de detalles y recarga."""
    res = database.eliminar_aplicacion(app_id)
    if res["success"]:
        st.success(res["message"])
        st.session_state.k_detail_id   = None
        st.session_state.k_detail_modo = None
        time.sleep(0.5)
        st.rerun()
    else:
        st.error(res["message"])