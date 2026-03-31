"""Kanban board for application management."""

from __future__ import annotations

import time

import streamlit as st

from app.domain.enums.application_status import APPLICATION_STATUSES
from app.infrastructure.persistence.repositories.application_repository import (
    ApplicationRepository,
)
from modules.components.application_components import (
    render_application_card,
    render_application_column_header,
    render_application_detail_summary,
    render_application_dialog_actions,
)
from modules.components.ui_labels import (
    APPLICATION_MODALITY_META,
    APPLICATION_STATUS_META,
    normalize_modality_label,
)
from modules.components.profile_components import render_empty_state
from modules.components.ui_styles import inject_management_styles

application_repository = ApplicationRepository()

ESTADOS_ORDEN = list(APPLICATION_STATUSES)
ESTADO_META = APPLICATION_STATUS_META
MODALIDAD_META = APPLICATION_MODALITY_META


@st.dialog("Detalle de Aplicacion", width="large")
def _dialog_detalle(app_id: int):
    app_item = application_repository.get_by_id(app_id)
    if not app_item:
        st.error("No se encontro la aplicacion.")
        return

    meta = ESTADO_META.get(app_item["estado"], ESTADO_META["Pending"])
    modalidad = normalize_modality_label(app_item["modalidad"])
    modal_meta = MODALIDAD_META.get(modalidad, {"emoji": "otro", "color": "#6B7280"})
    fecha_str = app_item["fecha_aplicacion"].strftime("%d/%m/%Y") if app_item["fecha_aplicacion"] else "-"

    st.markdown(
        f"### {app_item['cargo']}\n"
        f"<span style='color:#6B7280;font-size:0.9rem'>{app_item['empresa']}</span>"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"<span style='color:{meta['color']};font-size:0.9rem'>{meta['emoji']} {app_item['estado']}</span>",
        unsafe_allow_html=True,
    )
    st.divider()

    app_item = {**app_item, "modalidad": modalidad}
    render_application_detail_summary(app_item, modalidad_meta=modal_meta, fecha_str=fecha_str)

    st.markdown("**Notas**")
    if app_item["notas"]:
        st.markdown(f"<div class='detail-note'>{app_item['notas']}</div>", unsafe_allow_html=True)
    else:
        st.caption("Sin notas")

    st.divider()

    if "dlg_modo" not in st.session_state:
        st.session_state.dlg_modo = None

    modo = st.session_state.dlg_modo
    acciones = render_application_dialog_actions()
    if acciones["estado"]:
        st.session_state.dlg_modo = "estado" if modo != "estado" else None
        st.rerun()
    if acciones["datos"]:
        st.session_state.dlg_modo = "datos" if modo != "datos" else None
        st.rerun()
    if acciones["eliminar"]:
        st.session_state.dlg_modo = "eliminar" if modo != "eliminar" else None
        st.rerun()

    if modo == "estado":
        st.markdown("---")
        st.markdown("**Cambiar Estado**")
        with st.form("dlg_form_estado"):
            nuevo_estado = st.selectbox(
                "Nuevo estado:",
                options=ESTADOS_ORDEN,
                index=ESTADOS_ORDEN.index(app_item["estado"]) if app_item["estado"] in ESTADOS_ORDEN else 0,
            )
            if st.form_submit_button("Guardar", type="primary", use_container_width=True):
                res = application_repository.update_status(app_item["id"], nuevo_estado)
                if res["success"]:
                    st.success(res["message"])
                    st.session_state.dlg_modo = None
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error(res["message"])
    elif modo == "datos":
        st.markdown("---")
        st.markdown("**Editar Datos**")
        with st.form("dlg_form_datos"):
            col_e, col_n = st.columns([1, 2])
            with col_e:
                edit_estado = st.selectbox(
                    "Estado:",
                    options=ESTADOS_ORDEN,
                    index=ESTADOS_ORDEN.index(app_item["estado"]) if app_item["estado"] in ESTADOS_ORDEN else 0,
                )
            with col_n:
                edit_nombre = st.text_input("Nombre Recruiter:", value=app_item["nombre_recruiter"] or "")

            col_em, col_tel = st.columns(2)
            with col_em:
                edit_email = st.text_input("Email:", value=app_item["email_recruiter"] or "")
            with col_tel:
                edit_tel = st.text_input("Telefono:", value=app_item["telefono_recruiter"] or "")

            edit_notas = st.text_area("Notas:", value=app_item["notas"] or "", height=110)
            if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
                res = application_repository.update(
                    app_item["id"],
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
    elif modo == "eliminar":
        st.markdown("---")
        st.warning(f"Eliminar **#{app_item['id']} - {app_item['empresa']} / {app_item['cargo']}**? Esta accion no se puede deshacer.")
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Si, eliminar", type="primary", use_container_width=True, key="dlg_si"):
                res = application_repository.delete(app_item["id"])
                if res["success"]:
                    st.success(res["message"])
                    st.session_state.dlg_modo = None
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(res["message"])
        with col_no:
            if st.button("Cancelar", use_container_width=True, key="dlg_no"):
                st.session_state.dlg_modo = None
                st.rerun()


def mostrar_mis_aplicaciones():
    inject_management_styles()
    st.subheader("Mis Aplicaciones")

    aplicaciones = application_repository.list_all()
    if not aplicaciones:
        render_empty_state("No has registrado ninguna aplicacion aun.")
        return

    if "k_dialog_id" not in st.session_state:
        st.session_state.k_dialog_id = None
    if "dlg_modo" not in st.session_state:
        st.session_state.dlg_modo = None

    if st.session_state.k_dialog_id is not None:
        _dialog_detalle(st.session_state.k_dialog_id)
        st.session_state.k_dialog_id = None

    aplicaciones_filtradas, estados_visibles = _mostrar_filtros(aplicaciones)
    _mostrar_kanban(aplicaciones_filtradas, estados_visibles)


def _mostrar_filtros(aplicaciones: list) -> tuple:
    col_buscar, col_estados = st.columns([2, 3])
    with col_buscar:
        buscar = st.text_input("Buscar", placeholder="Buscar por empresa o cargo...", label_visibility="collapsed", key="kanban_buscar")
    with col_estados:
        estados_sel = st.multiselect("Columnas:", options=ESTADOS_ORDEN, default=ESTADOS_ORDEN, label_visibility="collapsed", key="kanban_estados_sel")

    if buscar:
        q = buscar.lower()
        aplicaciones = [item for item in aplicaciones if q in item["empresa"].lower() or q in item["cargo"].lower()]

    return aplicaciones, estados_sel or ESTADOS_ORDEN


def _mostrar_kanban(aplicaciones: list, estados_visibles: list):
    grupos: dict[str, list] = {estado: [] for estado in ESTADOS_ORDEN}
    for item in sorted(aplicaciones, key=lambda x: x["fecha_aplicacion"] or "", reverse=True):
        if item["estado"] in grupos:
            grupos[item["estado"]].append(item)

    cols = st.columns(len(estados_visibles))
    for i, estado in enumerate(estados_visibles):
        meta = ESTADO_META[estado]
        apps = grupos[estado]
        with cols[i]:
            render_application_column_header(estado, meta, len(apps))
            if not apps:
                st.markdown(
                    '<p style="color:#9CA3AF;font-size:0.7rem;font-style:italic;text-align:center;margin:6px 0 2px;">vacio</p>',
                    unsafe_allow_html=True,
                )
            else:
                for item in apps:
                    _renderizar_tarjeta(item, meta, estado)


def _renderizar_tarjeta(app_item: dict, meta: dict, estado_actual: str):
    modalidad = normalize_modality_label(app_item["modalidad"])
    modal_meta = MODALIDAD_META.get(modalidad, {"emoji": "otro", "color": "#6B7280"})
    nuevo_estado, ver = render_application_card(
        {**app_item, "modalidad": modalidad},
        meta=meta,
        modalidad_meta=modal_meta,
        estados_orden=ESTADOS_ORDEN,
        estado_actual=estado_actual,
    )

    if nuevo_estado:
        res = application_repository.update_status(app_item["id"], nuevo_estado)
        if res["success"]:
            st.toast(f"Movido a {nuevo_estado}")
            time.sleep(0.3)
            st.rerun()
        else:
            st.error(res["message"])

    if ver:
        st.session_state.k_dialog_id = app_item["id"]
        st.session_state.dlg_modo = None
        st.rerun()
