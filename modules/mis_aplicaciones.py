"""
modules/mis_aplicaciones.py
Tablero Kanban visual para gestión de aplicaciones.

Requiere Streamlit >= 1.36 para @st.dialog (pop-up nativo).

Interacción:
  - Selectbox "Mover a →" en cada tarjeta para cambiar estado al instante
  - Botón "🔍 Ver" abre un pop-up modal con detalles, edición y eliminar
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

/* ── Tarjeta ─────────────────────────────────────────────── */
.kcard {
    background: #ffffff;
    border: 1px solid #E5E7EB;
    border-radius: 7px;
    padding: 9px 11px 7px;
    margin-bottom: 5px;
    font-family: 'Sora', sans-serif;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    transition: box-shadow 0.15s ease;
}
.kcard:hover {
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
    color: #3B82F6;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
}
.kcard-link a:hover { text-decoration: underline; }

/* ── Contenido del dialog ────────────────────────────────── */
.dlg-label {
    font-size: 0.6rem;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 2px;
}
.dlg-value {
    font-size: 0.88rem;
    color: #111827;
    font-family: 'Sora', sans-serif;
    margin-bottom: 12px;
}
.dlg-notas {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 0.82rem;
    color: #374151;
    line-height: 1.65;
    white-space: pre-wrap;
    font-family: 'Sora', sans-serif;
    margin-top: 4px;
}
</style>
"""


# ─────────────────────────────────────────────────────────────
# DIALOG — pop-up nativo (requiere Streamlit >= 1.36)
# ─────────────────────────────────────────────────────────────

@st.dialog("📋 Detalle de Aplicación", width="large")
def _dialog_detalle(app_id: int):
    """
    Pop-up modal con detalles completos de una aplicación.
    Se cierra con ESC, click fuera del modal, o tras guardar/eliminar.
    """
    # Datos frescos desde BD (no depende de la lista cacheada del kanban)
    a = database.obtener_aplicacion_por_id(app_id)
    if not a:
        st.error("No se encontró la aplicación.")
        return

    meta       = ESTADO_META.get(a["estado"], ESTADO_META["Pending"])
    modal_meta = MODALIDAD_META.get(a["modalidad"], {"emoji": "📍", "color": "#6B7280"})
    fecha_str  = a["fecha_aplicacion"].strftime("%d/%m/%Y") if a["fecha_aplicacion"] else "—"

    # ── Encabezado ───────────────────────────────────────────
    st.markdown(
        f"### {a['cargo']}\n"
        f"<span style='color:#6B7280;font-size:0.9rem'>{a['empresa']}</span>"
        f"&nbsp;&nbsp;·&nbsp;&nbsp;"
        f"<span style='color:{meta['color']};font-size:0.9rem'>"
        f"{meta['emoji']} {a['estado']}</span>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Datos principales ────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='dlg-label'>🆔 ID</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dlg-value'><code>{a['id']}</code></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='dlg-label'>📍 Modalidad</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='dlg-value' style='color:{modal_meta['color']}'>"
            f"{modal_meta['emoji']} {a['modalidad']}</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown("<div class='dlg-label'>📅 Fecha Aplicación</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dlg-value'>{fecha_str}</div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='dlg-label'>🔗 Link</div>", unsafe_allow_html=True)
        if a.get("link"):
            st.markdown(
                f"<div class='dlg-value'>"
                f"<a href='{a['link']}' target='_blank' style='color:#3B82F6'>Abrir ↗</a>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='dlg-value' style='color:#9CA3AF'>—</div>", unsafe_allow_html=True)

    st.divider()

    # ── Recruiter ────────────────────────────────────────────
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("<div class='dlg-label'>👤 Recruiter</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dlg-value'>{a['nombre_recruiter'] or '—'}</div>", unsafe_allow_html=True)
    with r2:
        st.markdown("<div class='dlg-label'>📧 Email</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dlg-value'>{a['email_recruiter'] or '—'}</div>", unsafe_allow_html=True)
    with r3:
        st.markdown("<div class='dlg-label'>📞 Teléfono</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='dlg-value'>{a['telefono_recruiter'] or '—'}</div>", unsafe_allow_html=True)

    # ── Notas ────────────────────────────────────────────────
    st.markdown("<div class='dlg-label' style='margin-top:4px'>📝 Notas</div>", unsafe_allow_html=True)
    if a["notas"]:
        st.markdown(f"<div class='dlg-notas'>{a['notas']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<span style='color:#9CA3AF;font-style:italic;font-size:0.82rem'>Sin notas</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Botones de acción ─────────────────────────────────────
    if "dlg_modo" not in st.session_state:
        st.session_state.dlg_modo = None

    modo = st.session_state.dlg_modo
    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("✏️ Cambiar Estado", use_container_width=True, key="dlg_btn_estado"):
            st.session_state.dlg_modo = "estado" if modo != "estado" else None
            st.rerun()
    with b2:
        if st.button("📝 Editar Datos", use_container_width=True, key="dlg_btn_datos"):
            st.session_state.dlg_modo = "datos" if modo != "datos" else None
            st.rerun()
    with b3:
        if st.button("🗑️ Eliminar", use_container_width=True, type="secondary", key="dlg_btn_eliminar"):
            st.session_state.dlg_modo = "eliminar" if modo != "eliminar" else None
            st.rerun()

    # ── Sub-formulario: Cambiar Estado ───────────────────────
    if modo == "estado":
        st.markdown("---")
        st.markdown("**✏️ Cambiar Estado**")
        with st.form("dlg_form_estado"):
            nuevo_estado = st.selectbox(
                "Nuevo estado:",
                options=ESTADOS_ORDEN,
                index=ESTADOS_ORDEN.index(a["estado"]) if a["estado"] in ESTADOS_ORDEN else 0,
                format_func=lambda x: f"{ESTADO_META[x]['emoji']} {x}",
            )
            if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
                res = database.actualizar_estado_aplicacion(a["id"], nuevo_estado)
                if res["success"]:
                    st.success(res["message"])
                    st.session_state.dlg_modo = None
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error(res["message"])

    # ── Sub-formulario: Editar Datos ─────────────────────────
    elif modo == "datos":
        st.markdown("---")
        st.markdown("**📝 Editar Datos**")
        with st.form("dlg_form_datos"):
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

            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
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
                    st.session_state.dlg_modo = None
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error(res["message"])

    # ── Confirmar Eliminar ────────────────────────────────────
    elif modo == "eliminar":
        st.markdown("---")
        st.warning(
            f"⚠️ ¿Eliminar **#{a['id']} — {a['empresa']} / {a['cargo']}**? "
            f"Esta acción no se puede deshacer."
        )
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ Sí, eliminar", type="primary", use_container_width=True, key="dlg_si"):
                res = database.eliminar_aplicacion(a["id"])
                if res["success"]:
                    st.success(res["message"])
                    st.session_state.dlg_modo = None
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(res["message"])
        with col_no:
            if st.button("🚫 Cancelar", use_container_width=True, key="dlg_no"):
                st.session_state.dlg_modo = None
                st.rerun()


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
    if "k_dialog_id" not in st.session_state:
        st.session_state.k_dialog_id = None
    if "dlg_modo" not in st.session_state:
        st.session_state.dlg_modo = None

    # ── Disparar dialog si hay ID pendiente ──────────────────
    # Debe ejecutarse ANTES del kanban para que el pop-up
    # aparezca correctamente sobre el contenido
    if st.session_state.k_dialog_id is not None:
        _dialog_detalle(st.session_state.k_dialog_id)
        st.session_state.k_dialog_id = None

    # ── Filtros ──────────────────────────────────────────────
    aplicaciones_filtradas, estados_visibles = _mostrar_filtros(aplicaciones)

    # ── Kanban ───────────────────────────────────────────────
    _mostrar_kanban(aplicaciones_filtradas, estados_visibles)


# ─────────────────────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────────────────────

def _mostrar_filtros(aplicaciones: list) -> tuple:
    """
    Barra de búsqueda + multiselect de columnas visibles.
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
    """Renderiza las columnas del kanban con sus tarjetas."""
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
            # Header con estilos inline (CSS vars no funcionan cross-scope en Streamlit)
            st.markdown(
                f'<div style="'
                f'background:{meta["bg"]};'
                f'border:1px solid {meta["color"]}55;'
                f'border-top:3px solid {meta["color"]};'
                f'border-radius:8px;'
                f'padding:7px 10px 8px;'
                f'display:flex;align-items:center;justify-content:space-between;'
                f'margin-bottom:8px;">'
                f'<span style="font-family:Sora,sans-serif;font-weight:700;font-size:0.7rem;'
                f'color:{meta["color"]};letter-spacing:0.06em;text-transform:uppercase;">'
                f'{meta["emoji"]} {estado}</span>'
                f'<span style="font-family:monospace;font-size:0.65rem;'
                f'color:{meta["color"]};background:{meta["bg"]};'
                f'padding:1px 7px;border-radius:99px;border:1px solid {meta["color"]}55;">'
                f'{len(apps)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if not apps:
                st.markdown(
                    '<p style="color:#9CA3AF;font-size:0.7rem;font-style:italic;'
                    'text-align:center;margin:6px 0 2px;">vacío</p>',
                    unsafe_allow_html=True,
                )
            else:
                for a in apps:
                    _renderizar_tarjeta(a, meta, estado)


def _renderizar_tarjeta(a: dict, meta: dict, estado_actual: str):
    """
    Tarjeta individual del kanban.
    - Selectbox "Mover a →" para cambio de estado inmediato
    - Botón "🔍 Ver" para abrir el dialog de detalles
    """
    modal_meta = MODALIDAD_META.get(a["modalidad"], {"emoji": "📍", "color": "#6B7280"})
    fecha_str  = a["fecha_aplicacion"].strftime("%d/%m/%Y") if a["fecha_aplicacion"] else "—"
    link_html  = (
        f'<span class="kcard-link"><a href="{a["link"]}" target="_blank">🔗 Abrir</a></span>'
        if a.get("link") else ""
    )

    st.markdown(
        f'<div class="kcard" style="border-left:3px solid {meta["color"]}">'
        f'  <div class="kcard-cargo" title="{a["cargo"]}">{a["cargo"]}</div>'
        f'  <div class="kcard-empresa">{a["empresa"]}</div>'
        f'  <span class="kbadge" style="'
        f'    background:{modal_meta["color"]}22;'
        f'    color:{modal_meta["color"]};'
        f'    border:1px solid {modal_meta["color"]}55">'
        f'  {modal_meta["emoji"]} {a["modalidad"]}'
        f'  </span>'
        f'  <div class="kcard-footer">'
        f'    <span class="kcard-fecha">📅 {fecha_str}</span>'
        f'    {link_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Selectbox "Mover a →" — cambia estado en 1 click
    otros    = [e for e in ESTADOS_ORDEN if e != estado_actual]
    opciones = ["Mover a →"] + [f"{ESTADO_META[e]['emoji']} {e}" for e in otros]

    sel = st.selectbox(
        label="estado",
        options=opciones,
        index=0,
        key=f"mover_{a['id']}",
        label_visibility="collapsed",
    )

    if sel != "Mover a →":
        nuevo_estado = sel.split(" ", 1)[1]   # "📤 Applied" → "Applied"
        res = database.actualizar_estado_aplicacion(a["id"], nuevo_estado)
        if res["success"]:
            st.toast(f"✅ Movido a {nuevo_estado}", icon="✅")
            time.sleep(0.3)
            st.rerun()
        else:
            st.error(f"❌ {res['message']}")

    # Botón "🔍 Ver" — guarda el ID y dispara el dialog en el próximo render
    if st.button("🔍 Ver", key=f"ver_{a['id']}", use_container_width=True):
        st.session_state.k_dialog_id = a["id"]
        st.session_state.dlg_modo    = None
        st.rerun()