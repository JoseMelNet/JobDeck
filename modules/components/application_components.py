"""Specific UI components for application screens."""

from __future__ import annotations

import streamlit as st

from modules.components.profile_components import render_delete_button


def render_application_detail_summary(app_item: dict, *, modalidad_meta: dict, fecha_str: str) -> None:
    cards = [
        ("ID", str(app_item["id"])),
        ("Modalidad", f"{modalidad_meta['emoji']} {app_item['modalidad']}"),
        ("Fecha aplicacion", fecha_str),
        ("Link", "Abrir" if app_item.get("link") else "-"),
    ]
    html_cards = "".join(
        f"<div class='info-card'><div class='info-label'>{label}</div><div class='info-value'>{value}</div></div>"
        for label, value in cards
    )
    st.markdown(f"<div class='info-grid cols-4'>{html_cards}</div>", unsafe_allow_html=True)
    if app_item.get("link"):
        st.markdown(f"**Link:** [Abrir]({app_item['link']})")

    st.divider()

    contact_cards = [
        ("Recruiter", app_item["nombre_recruiter"] or "-"),
        ("Email", app_item["email_recruiter"] or "-"),
        ("Telefono", app_item["telefono_recruiter"] or "-"),
    ]
    html_contact = "".join(
        f"<div class='info-card'><div class='info-label'>{label}</div><div class='info-value'>{value}</div></div>"
        for label, value in contact_cards
    )
    st.markdown(f"<div class='info-grid'>{html_contact}</div>", unsafe_allow_html=True)


def render_application_dialog_actions() -> dict[str, bool]:
    b1, b2, b3 = st.columns(3)
    with b1:
        estado = st.button("Cambiar Estado", use_container_width=True, key="dlg_btn_estado")
    with b2:
        datos = st.button("Editar Datos", use_container_width=True, key="dlg_btn_datos")
    with b3:
        eliminar = render_delete_button(key="dlg_btn_eliminar", use_container_width=True)
    return {"estado": estado, "datos": datos, "eliminar": eliminar}


def render_application_column_header(estado: str, meta: dict, count: int) -> None:
    st.markdown(
        f'<div style="background:{meta["bg"]};border:1px solid {meta["color"]}55;'
        f'border-top:3px solid {meta["color"]};border-radius:8px;padding:7px 10px 8px;'
        f'display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        f'<span style="font-weight:700;font-size:0.7rem;color:{meta["color"]};'
        f'letter-spacing:0.06em;text-transform:uppercase;">{meta["emoji"]} {estado}</span>'
        f'<span style="font-size:0.65rem;color:{meta["color"]};background:{meta["bg"]};'
        f'padding:1px 7px;border-radius:99px;border:1px solid {meta["color"]}55;">{count}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_application_card(app_item: dict, *, meta: dict, modalidad_meta: dict, estados_orden: list[str], estado_actual: str) -> tuple[str | None, bool]:
    fecha_str = app_item["fecha_aplicacion"].strftime("%d/%m/%Y") if app_item["fecha_aplicacion"] else "-"
    link_html = f'<span class="kcard-link"><a href="{app_item["link"]}" target="_blank">Abrir</a></span>' if app_item.get("link") else ""

    st.markdown(
        f'<div class="kcard" style="border-left:3px solid {meta["color"]}">'
        f'<div class="kcard-cargo" title="{app_item["cargo"]}">{app_item["cargo"]}</div>'
        f'<div class="kcard-empresa">{app_item["empresa"]}</div>'
        f'<span class="kbadge" style="background:{modalidad_meta["color"]}22;color:{modalidad_meta["color"]};'
        f'border:1px solid {modalidad_meta["color"]}55">{modalidad_meta["emoji"]} {app_item["modalidad"]}</span>'
        f'<div class="kcard-footer"><span class="kcard-fecha">{fecha_str}</span>{link_html}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    otros = [estado for estado in estados_orden if estado != estado_actual]
    opciones = ["Mover a ->"] + otros
    nuevo_estado = st.selectbox("estado", options=opciones, index=0, key=f"mover_{app_item['id']}", label_visibility="collapsed")
    ver = st.button("Ver", key=f"ver_{app_item['id']}", use_container_width=True)
    return (nuevo_estado if nuevo_estado != "Mover a ->" else None, ver)
