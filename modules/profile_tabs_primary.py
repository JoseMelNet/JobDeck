"""Primary profile tabs: personal data and skills."""

from __future__ import annotations

import time

import streamlit as st

from modules.components.profile_components import (
    fixed_height_list,
    render_delete_button,
    render_empty_state,
)
from modules.profile_shared import (
    CATEGORIAS_SKILL_DEFAULT,
    MODALIDADES,
    MONEDAS,
    NIVELES_IDIOMA,
    NIVELES_SENIORITY,
    NIVELES_SKILL_TECNICO,
    database,
    get_categorias,
)


def tab_datos_personales(perfil):
    st.markdown("#### Informacion Personal y Profesional")
    p = perfil or {}

    with st.form("form_datos_personales"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre completo *", value=p.get("nombre", ""), placeholder="Ej: Juan Perez Garcia")
        with c2:
            titulo = st.text_input("Titulo profesional *", value=p.get("titulo_profesional", ""), placeholder="Ej: Data Analyst | BI Developer")

        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("Ciudad", value=p.get("ciudad", ""), placeholder="Ej: Bogota, Colombia")
        with c2:
            direccion = st.text_input("Direccion", value=p.get("direccion", ""), placeholder="Ej: Cra 7 # 45-20")

        c1, c2, c3 = st.columns(3)
        with c1:
            celular = st.text_input("Celular", value=p.get("celular", ""), placeholder="Ej: +57 310 123 4567")
        with c2:
            correo = st.text_input("Correo", value=p.get("correo", ""), placeholder="Ej: juan@email.com")
        with c3:
            nivel = st.selectbox(
                "Nivel actual *",
                options=NIVELES_SENIORITY,
                index=NIVELES_SENIORITY.index(p["nivel_actual"]) if p.get("nivel_actual") in NIVELES_SENIORITY else 1,
            )

        c1, c2 = st.columns(2)
        with c1:
            linkedin = st.text_input("LinkedIn", value=p.get("perfil_linkedin", ""), placeholder="https://linkedin.com/in/tu-perfil")
        with c2:
            github = st.text_input("GitHub", value=p.get("perfil_github", ""), placeholder="https://github.com/tu-usuario")

        st.divider()
        st.markdown("**Aspiracion Salarial y Modalidad**")

        c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
        with c1:
            salario_min = st.number_input("Salario minimo", min_value=0.0, value=float(p["salario_min"]) if p.get("salario_min") else 0.0, step=100000.0, format="%.0f")
        with c2:
            salario_max = st.number_input("Salario maximo", min_value=0.0, value=float(p["salario_max"]) if p.get("salario_max") else 0.0, step=100000.0, format="%.0f")
        with c3:
            moneda = st.selectbox("Moneda", options=MONEDAS, index=MONEDAS.index(p["moneda"]) if p.get("moneda") in MONEDAS else 0)
        with c4:
            anos_exp = st.number_input("Anios de experiencia", min_value=0, max_value=50, value=int(p.get("anos_experiencia", 0)))

        modalidades_actuales = p.get("modalidades_aceptadas", "Remoto,Hibrido,Presencial")
        modalidades_lista = [m.strip() for m in modalidades_actuales.split(",") if m.strip()]
        modalidades_sel = st.multiselect("Modalidades aceptadas *", options=MODALIDADES, default=[m for m in modalidades_lista if m in MODALIDADES])
        submitted = st.form_submit_button("Guardar Datos Personales", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not titulo.strip():
            errores.append("El titulo profesional es obligatorio.")
        if not modalidades_sel:
            errores.append("Selecciona al menos una modalidad.")
        if salario_max > 0 and salario_min > salario_max:
            errores.append("El salario minimo no puede ser mayor al maximo.")

        if errores:
            for error in errores:
                st.error(error)
        else:
            res = database.guardar_perfil(
                {
                    "nombre": nombre,
                    "titulo_profesional": titulo,
                    "ciudad": ciudad,
                    "direccion": direccion,
                    "celular": celular,
                    "correo": correo,
                    "perfil_linkedin": linkedin,
                    "perfil_github": github,
                    "nivel_actual": nivel,
                    "anos_experiencia": anos_exp,
                    "salario_min": salario_min if salario_min > 0 else None,
                    "salario_max": salario_max if salario_max > 0 else None,
                    "moneda": moneda,
                    "modalidades_aceptadas": ",".join(modalidades_sel),
                }
            )
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.8)
                st.rerun()
            else:
                st.error(res["message"])


def tab_skills(perfil_id):
    if not perfil_id:
        st.warning("Primero completa tus **Datos Personales**.")
        return

    if "skills_categorias_custom" not in st.session_state:
        st.session_state.skills_categorias_custom = []
    if "skill_ultima_categoria" not in st.session_state:
        st.session_state.skill_ultima_categoria = CATEGORIAS_SKILL_DEFAULT[0]

    st.markdown("#### Agregar Skill")
    with st.expander("Crear nueva categoria personalizada"):
        col_nc, col_btn = st.columns([3, 1])
        with col_nc:
            nueva_cat = st.text_input("Nombre", placeholder="Ej: Machine Learning", key="nueva_categoria_input", label_visibility="collapsed")
        with col_btn:
            if st.button("Crear", key="btn_nueva_cat", use_container_width=True):
                nc = nueva_cat.strip()
                categorias_actuales = get_categorias()
                if not nc:
                    st.error("Escribe un nombre.")
                elif nc in categorias_actuales:
                    st.warning(f"'{nc}' ya existe.")
                else:
                    st.session_state.skills_categorias_custom.append(nc)
                    st.session_state.skill_ultima_categoria = nc
                    st.success(f"Categoria '{nc}' creada.")
                    time.sleep(0.4)
                    st.rerun()

    categorias = get_categorias()
    idx_cat = categorias.index(st.session_state.skill_ultima_categoria) if st.session_state.skill_ultima_categoria in categorias else 0
    with st.form("form_skill", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            categoria = st.selectbox("Categoria *", options=categorias, index=idx_cat)
        with c2:
            skill_nombre = st.text_input("Skill *", placeholder="Ej: SQL, Python, Power BI, Ingles")
        with c3:
            es_idioma = st.session_state.skill_ultima_categoria == "Idiomas"
            nivel_ops = NIVELES_IDIOMA if es_idioma else NIVELES_SKILL_TECNICO
            nivel = st.selectbox("Nivel *", options=nivel_ops)
        submitted = st.form_submit_button("Agregar Skill", use_container_width=True, type="primary")

    if submitted:
        if not skill_nombre.strip():
            st.error("El nombre de la skill es obligatorio.")
        else:
            st.session_state.skill_ultima_categoria = categoria
            res = database.insertar_skill(perfil_id, categoria, skill_nombre, nivel)
            if res["success"]:
                st.success(res["message"])
                time.sleep(0.4)
                st.rerun()
            else:
                st.error(res["message"])

    st.markdown("---")
    st.markdown("#### Skills registradas")
    skills = database.obtener_skills(perfil_id)
    if not skills:
        render_empty_state("Aun no tienes skills registradas.")
        return

    cats_en_bd = {}
    for skill in skills:
        cats_en_bd.setdefault(skill["categoria"], []).append(skill)

    with fixed_height_list(350):
        for cat, items in cats_en_bd.items():
            st.markdown(f"**{cat}**")
            for skill in items:
                col_skill, col_nivel, col_del = st.columns([3, 2, 1])
                with col_skill:
                    st.write(skill["skill"])
                with col_nivel:
                    st.write(f"`{skill['nivel']}`")
                with col_del:
                    if render_delete_button(key=f"del_skill_{skill['id']}", label="Borrar"):
                        res = database.eliminar_skill(skill["id"])
                        if res["success"]:
                            st.toast("Skill eliminada")
                            time.sleep(0.3)
                            st.rerun()
                        else:
                            st.error(res["message"])
            st.divider()
