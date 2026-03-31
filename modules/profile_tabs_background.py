"""Secondary profile tabs: experience, projects, and training."""

from __future__ import annotations

import time
from datetime import date

import streamlit as st

from modules.components.profile_components import (
    expandable_item_card,
    fixed_height_list,
    format_date_range,
    render_delete_button,
    render_empty_state,
    render_metadata_grid,
)
from modules.profile_shared import (
    NIVELES_EDUCACION,
    STATUS_CERT,
    STATUS_CURSOS,
    STATUS_EDUCACION,
    database,
    fmt_fecha,
)


def tab_experiencia(perfil_id):
    if not perfil_id:
        st.warning("Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Agregar Experiencia")
    with st.form("form_experiencia", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cargo = st.text_input("Cargo *", placeholder="Ej: Data Analyst")
        with c2:
            empresa = st.text_input("Empresa *", placeholder="Ej: Bancolombia")
        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Medellin")
        with c2:
            desc_empresa = st.text_input("Descripcion empresa", placeholder="Ej: Fintech, 500+ empleados")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today())
        with c2:
            fecha_fin = st.date_input("Fecha fin", value=None)
        with c3:
            es_actual = st.checkbox("Trabajo actual", value=False)
        funciones = st.text_area("Funciones", placeholder="Describe las principales responsabilidades...", height=100)
        logros = st.text_area("Logros", placeholder="Ej: Reduje el tiempo de reportes en 40%...", height=100)
        submitted = st.form_submit_button("Agregar Experiencia", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not cargo.strip():
            errores.append("El cargo es obligatorio.")
        if not empresa.strip():
            errores.append("La empresa es obligatoria.")
        if errores:
            for error in errores:
                st.error(error)
        else:
            res = database.insertar_experiencia(
                perfil_id,
                {
                    "cargo": cargo,
                    "empresa": empresa,
                    "ciudad": ciudad,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "es_trabajo_actual": es_actual,
                    "descripcion_empresa": desc_empresa,
                    "funciones": funciones,
                    "logros": logros,
                },
            )
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res["message"])

    st.markdown("---")
    st.markdown("#### Experiencias registradas")
    experiencias = database.obtener_experiencias(perfil_id)
    if not experiencias:
        render_empty_state("Aun no tienes experiencias registradas.")
        return

    if "exp_editando_id" not in st.session_state:
        st.session_state.exp_editando_id = None

    with fixed_height_list(500):
        for exp in experiencias:
            periodo = format_date_range(
                exp["fecha_inicio"],
                exp["fecha_fin"],
                fmt_fecha,
                is_current=exp["es_trabajo_actual"],
            )
            label = f"{exp['cargo']} - {exp['empresa']} ({periodo})"
            with expandable_item_card(label):
                if st.session_state.exp_editando_id != exp["id"]:
                    render_metadata_grid(
                        [
                            ("Ciudad", exp["ciudad"]),
                            ("Periodo", periodo),
                            ("Empresa", exp["descripcion_empresa"]),
                        ]
                    )
                    if exp["funciones"]:
                        st.markdown("**Funciones:**")
                        st.write(exp["funciones"])
                    if exp["logros"]:
                        st.markdown("**Logros:**")
                        st.write(exp["logros"])

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("Editar", key=f"btn_edit_exp_{exp['id']}", use_container_width=True):
                            st.session_state.exp_editando_id = exp["id"]
                            st.rerun()
                    with col_del:
                        if render_delete_button(key=f"del_exp_{exp['id']}", use_container_width=True):
                            res = database.eliminar_experiencia(exp["id"])
                            if res["success"]:
                                st.toast("Experiencia eliminada")
                                time.sleep(0.3)
                                st.rerun()
                            else:
                                st.error(res["message"])
                else:
                    st.markdown("**Editando experiencia**")
                    with st.form(f"form_edit_exp_{exp['id']}"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_cargo = st.text_input("Cargo *", value=exp["cargo"])
                        with ec2:
                            e_empresa = st.text_input("Empresa *", value=exp["empresa"])
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_ciudad = st.text_input("Ciudad", value=exp["ciudad"] or "")
                        with ec2:
                            e_desc = st.text_input("Descripcion empresa", value=exp["descripcion_empresa"] or "")
                        ec1, ec2, ec3 = st.columns([2, 2, 1])
                        with ec1:
                            e_fi = st.date_input("Fecha inicio *", value=exp["fecha_inicio"] if exp["fecha_inicio"] else date.today(), key=f"efi_{exp['id']}")
                        with ec2:
                            e_ff = st.date_input("Fecha fin", value=exp["fecha_fin"] if exp["fecha_fin"] else None, key=f"eff_{exp['id']}")
                        with ec3:
                            e_actual = st.checkbox("Actual", value=exp["es_trabajo_actual"], key=f"eact_{exp['id']}")
                        e_funciones = st.text_area("Funciones", value=exp["funciones"] or "", height=100, key=f"efunc_{exp['id']}")
                        e_logros = st.text_area("Logros", value=exp["logros"] or "", height=100, key=f"elogr_{exp['id']}")
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save = st.form_submit_button("Guardar cambios", use_container_width=True, type="primary")
                        with col_cancel:
                            cancel = st.form_submit_button("Cancelar", use_container_width=True)

                    if save:
                        errores = []
                        if not e_cargo.strip():
                            errores.append("El cargo es obligatorio.")
                        if not e_empresa.strip():
                            errores.append("La empresa es obligatoria.")
                        if errores:
                            for error in errores:
                                st.error(error)
                        else:
                            res = database.actualizar_experiencia(
                                exp["id"],
                                {
                                    "cargo": e_cargo,
                                    "empresa": e_empresa,
                                    "ciudad": e_ciudad,
                                    "descripcion_empresa": e_desc,
                                    "fecha_inicio": e_fi,
                                    "fecha_fin": e_ff,
                                    "es_trabajo_actual": e_actual,
                                    "funciones": e_funciones,
                                    "logros": e_logros,
                                },
                            )
                            if res["success"]:
                                st.success(res["message"])
                                st.session_state.exp_editando_id = None
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(res["message"])

                    if cancel:
                        st.session_state.exp_editando_id = None
                        st.rerun()


def tab_proyectos(perfil_id):
    if not perfil_id:
        st.warning("Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Agregar Proyecto")
    with st.form("form_proyecto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre del proyecto *", placeholder="Ej: Dashboard de Ventas")
        with c2:
            empresa = st.text_input("Empresa", placeholder="Dejar vacio si es personal")
        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Bogota")
        with c2:
            stack = st.text_input("Stack tecnologico", placeholder="Ej: Python, SQL, Power BI, Azure")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today(), key="proy_fi")
        with c2:
            fecha_fin = st.date_input("Fecha fin", value=None, key="proy_ff")
        with c3:
            es_actual = st.checkbox("En curso", value=False)
        url_repo = st.text_input("URL Repositorio", placeholder="https://github.com/...")
        funciones = st.text_area("Descripcion", placeholder="Que hiciste en este proyecto?", height=90)
        logros = st.text_area("Logros / Impacto", placeholder="Ej: Automatice X, reduciendo Y en Z%", height=90)
        submitted = st.form_submit_button("Agregar Proyecto", use_container_width=True, type="primary")

    if submitted:
        if not nombre.strip():
            st.error("El nombre del proyecto es obligatorio.")
        else:
            res = database.insertar_proyecto(
                perfil_id,
                {
                    "nombre": nombre,
                    "empresa": empresa,
                    "ciudad": ciudad,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "es_proyecto_actual": es_actual,
                    "stack": stack,
                    "funciones": funciones,
                    "logros": logros,
                    "url_repositorio": url_repo,
                },
            )
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res["message"])

    st.markdown("---")
    st.markdown("#### Proyectos registrados")
    proyectos = database.obtener_proyectos(perfil_id)
    if not proyectos:
        render_empty_state("Aun no tienes proyectos registrados.")
        return

    with fixed_height_list(450):
        for proyecto in proyectos:
            periodo = format_date_range(
                proyecto["fecha_inicio"],
                proyecto["fecha_fin"],
                fmt_fecha,
                is_current=proyecto["es_proyecto_actual"],
                current_label="En curso",
            )
            with expandable_item_card(f"{proyecto['nombre']} ({periodo})"):
                render_metadata_grid(
                    [
                        ("Empresa", proyecto["empresa"] or "Personal"),
                        ("Ciudad", proyecto["ciudad"]),
                        ("Stack", proyecto["stack"]),
                    ]
                )
                if proyecto["url_repositorio"]:
                    st.markdown(f"**Repo:** [{proyecto['url_repositorio']}]({proyecto['url_repositorio']})")
                if proyecto["funciones"]:
                    st.markdown("**Descripcion:**")
                    st.write(proyecto["funciones"])
                if proyecto["logros"]:
                    st.markdown("**Logros / Impacto:**")
                    st.write(proyecto["logros"])
                if render_delete_button(key=f"del_proy_{proyecto['id']}"):
                    res = database.eliminar_proyecto(proyecto["id"])
                    if res["success"]:
                        st.toast("Proyecto eliminado")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res["message"])


def tab_educacion(perfil_id):
    if not perfil_id:
        st.warning("Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Agregar Educacion")
    with st.form("form_educacion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Titulo *", placeholder="Ej: Ingenieria de Sistemas")
        with c2:
            institucion = st.text_input("Institucion *", placeholder="Ej: Universidad Nacional")
        c1, c2, c3 = st.columns(3)
        with c1:
            nivel = st.selectbox("Nivel *", options=NIVELES_EDUCACION)
        with c2:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Bogota")
        with c3:
            status = st.selectbox("Status *", options=STATUS_EDUCACION, index=1)
        c1, c2 = st.columns(2)
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today(), key="edu_fi")
        with c2:
            fecha_fin = st.date_input("Fecha fin", value=None, key="edu_ff")
        submitted = st.form_submit_button("Agregar Educacion", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not titulo.strip():
            errores.append("El titulo es obligatorio.")
        if not institucion.strip():
            errores.append("La institucion es obligatoria.")
        if errores:
            for error in errores:
                st.error(error)
        else:
            res = database.insertar_educacion(
                perfil_id,
                {
                    "titulo": titulo,
                    "institucion": institucion,
                    "ciudad": ciudad,
                    "nivel": nivel,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "status": status,
                },
            )
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res["message"])

    st.markdown("---")
    st.markdown("#### Educacion registrada")
    educacion = database.obtener_educacion(perfil_id)
    if not educacion:
        render_empty_state("Aun no tienes formacion registrada.")
        return

    with fixed_height_list(350):
        for item in educacion:
            periodo = format_date_range(item["fecha_inicio"], item["fecha_fin"], fmt_fecha, current_label=item["status"])
            with expandable_item_card(f"{item['titulo']} - {item['institucion']} ({periodo}) [{item['status']}]"):
                render_metadata_grid([("Nivel", item["nivel"]), ("Ciudad", item["ciudad"]), ("Status", item["status"])])
                if render_delete_button(key=f"del_edu_{item['id']}"):
                    res = database.eliminar_educacion(item["id"])
                    if res["success"]:
                        st.toast("Educacion eliminada")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res["message"])


def tab_cursos(perfil_id):
    if not perfil_id:
        st.warning("Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Agregar Curso")
    with st.form("form_curso", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Titulo del curso *", placeholder="Ej: SQL para Analisis de Datos")
        with c2:
            institucion = st.text_input("Plataforma / Institucion *", placeholder="Ej: Udemy, Coursera, Platzi")
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_inicio = st.date_input("Fecha inicio", value=None, key="cur_fi")
        with c2:
            fecha_fin = st.date_input("Fecha fin", value=None, key="cur_ff")
        with c3:
            status = st.selectbox("Status *", options=STATUS_CURSOS, index=1)
        url_cert = st.text_input("URL Certificado", placeholder="https://udemy.com/certificate/...")
        submitted = st.form_submit_button("Agregar Curso", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not titulo.strip():
            errores.append("El titulo es obligatorio.")
        if not institucion.strip():
            errores.append("La institucion es obligatoria.")
        if errores:
            for error in errores:
                st.error(error)
        else:
            res = database.insertar_curso(
                perfil_id,
                {
                    "titulo": titulo,
                    "institucion": institucion,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "status": status,
                    "url_certificado": url_cert,
                },
            )
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res["message"])

    st.markdown("---")
    st.markdown("#### Cursos registrados")
    cursos = database.obtener_cursos(perfil_id)
    if not cursos:
        render_empty_state("Aun no tienes cursos registrados.")
        return

    with fixed_height_list(350):
        for curso in cursos:
            periodo = format_date_range(curso["fecha_inicio"], curso["fecha_fin"], fmt_fecha)
            with expandable_item_card(f"{curso['titulo']} - {curso['institucion']} [{curso['status']}]"):
                render_metadata_grid([("Periodo", periodo), ("Status", curso["status"])])
                if curso["url_certificado"]:
                    st.markdown(f"**Certificado:** [Ver]({curso['url_certificado']})")
                if render_delete_button(key=f"del_cur_{curso['id']}"):
                    res = database.eliminar_curso(curso["id"])
                    if res["success"]:
                        st.toast("Curso eliminado")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res["message"])


def tab_certificaciones(perfil_id):
    if not perfil_id:
        st.warning("Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Agregar Certificacion")
    with st.form("form_cert", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Titulo *", placeholder="Ej: AWS Certified Data Analytics")
        with c2:
            institucion = st.text_input("Institucion emisora *", placeholder="Ej: Amazon Web Services")
        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_obt = st.date_input("Fecha obtencion *", value=date.today(), key="cert_fo")
        with c2:
            fecha_venc = st.date_input("Fecha vencimiento", value=None, key="cert_fv", help="Dejar vacio si no vence")
        with c3:
            status = st.selectbox("Status *", options=STATUS_CERT)
        url_cert = st.text_input("URL Certificado / Credly", placeholder="https://credly.com/...")
        submitted = st.form_submit_button("Agregar Certificacion", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not titulo.strip():
            errores.append("El titulo es obligatorio.")
        if not institucion.strip():
            errores.append("La institucion es obligatoria.")
        if errores:
            for error in errores:
                st.error(error)
        else:
            res = database.insertar_certificacion(
                perfil_id,
                {
                    "titulo": titulo,
                    "institucion": institucion,
                    "fecha_obtencion": fecha_obt,
                    "fecha_vencimiento": fecha_venc,
                    "status": status,
                    "url_certificado": url_cert,
                },
            )
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res["message"])

    st.markdown("---")
    st.markdown("#### Certificaciones registradas")
    certs = database.obtener_certificaciones(perfil_id)
    if not certs:
        render_empty_state("Aun no tienes certificaciones registradas.")
        return

    with fixed_height_list(350):
        for cert in certs:
            vence_str = fmt_fecha(cert["fecha_vencimiento"]) if cert["fecha_vencimiento"] else "No vence"
            with expandable_item_card(f"{cert['titulo']} - {cert['institucion']} [{cert['status']}]"):
                render_metadata_grid(
                    [
                        ("Obtenida", fmt_fecha(cert["fecha_obtencion"])),
                        ("Vence", vence_str),
                        ("Status", cert["status"]),
                    ]
                )
                if cert["url_certificado"]:
                    st.markdown(f"**Certificado:** [Ver]({cert['url_certificado']})")
                if render_delete_button(key=f"del_cert_{cert['id']}"):
                    res = database.eliminar_certificacion(cert["id"])
                    if res["success"]:
                        st.toast("Certificacion eliminada")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res["message"])
