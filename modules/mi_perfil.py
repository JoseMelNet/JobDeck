"""
modules/mi_perfil.py  — v2
Pestaña: Mi Perfil — gestión completa del perfil profesional.

Cambios v2:
  1. Forms fijos arriba, registros en contenedor scrolleable debajo
  2. Categorías de skill dinámicas (usuario puede crear nuevas)
  3. Última categoría seleccionada persiste en session state
  4. Tab "Vista CV" con estructura visual del CV real
  5. Editar experiencia laboral (inline dentro del expander)
"""

import streamlit as st
import database
from datetime import date, datetime
import time


# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

NIVELES_SENIORITY = ['Junior', 'Mid', 'Senior']

CATEGORIAS_SKILL_DEFAULT = [
    'Bases de Datos',
    'Lenguajes de Programación',
    'Visualización',
    'Cloud',
    'ETL / Integración',
    'Herramientas',
    'Metodologías',
    'Blandas',
    'Idiomas',
    'Otra',
]

NIVELES_SKILL_TECNICO = ['Básico', 'Intermedio', 'Avanzado', 'Experto']
NIVELES_IDIOMA        = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Nativo']

NIVELES_EDUCACION = [
    'Bachillerato', 'Técnico', 'Tecnólogo', 'Pregrado',
    'Especialización', 'Maestría', 'Doctorado', 'Otro',
]

STATUS_EDUCACION = ['En curso', 'Completado', 'Pausado', 'Abandonado']
STATUS_CURSOS    = ['En curso', 'Completado', 'Pausado']
STATUS_CERT      = ['Vigente', 'Vencido', 'En proceso']
MODALIDADES      = ['Remoto', 'Presencial', 'Híbrido']
MONEDAS          = ['COP', 'USD', 'EUR', 'MXN', 'ARS']


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _fmt_fecha(fecha) -> str:
    if not fecha:
        return '—'
    if isinstance(fecha, (datetime, date)):
        return fecha.strftime('%m/%Y')
    return str(fecha)


def _get_categorias() -> list:
    """
    Retorna las categorías de skills combinando defaults
    con las personalizadas guardadas en session state.
    """
    if 'skills_categorias_custom' not in st.session_state:
        st.session_state.skills_categorias_custom = []
    return CATEGORIAS_SKILL_DEFAULT + [
        c for c in st.session_state.skills_categorias_custom
        if c not in CATEGORIAS_SKILL_DEFAULT
    ]


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def mostrar_mi_perfil():
    st.subheader("Mi Perfil Profesional")

    perfil = database.obtener_perfil()

    if not perfil:
        st.info(
            "👋 Aún no tienes un perfil creado. "
            "Completa la pestaña **Datos Personales** para comenzar."
        )

    tabs = st.tabs([
        "👤 Datos Personales",
        "🛠️ Skills",
        "💼 Experiencia",
        "🚀 Proyectos",
        "🎓 Educación",
        "📚 Cursos",
        "🏆 Certificaciones",
        "📄 Vista CV",
    ])

    perfil_id = perfil['id'] if perfil else None

    with tabs[0]: _tab_datos_personales(perfil)
    with tabs[1]: _tab_skills(perfil_id)
    with tabs[2]: _tab_experiencia(perfil_id)
    with tabs[3]: _tab_proyectos(perfil_id)
    with tabs[4]: _tab_educacion(perfil_id)
    with tabs[5]: _tab_cursos(perfil_id)
    with tabs[6]: _tab_certificaciones(perfil_id)
    with tabs[7]: _tab_vista_cv(perfil, perfil_id)


# ─────────────────────────────────────────────────────────────
# TAB 1 — Datos Personales
# ─────────────────────────────────────────────────────────────

def _tab_datos_personales(perfil):
    st.markdown("#### Información Personal y Profesional")
    p = perfil or {}

    with st.form("form_datos_personales"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("👤 Nombre completo *", value=p.get('nombre', ''),
                                   placeholder="Ej: Juan Pérez García")
        with c2:
            titulo = st.text_input("💼 Título profesional *", value=p.get('titulo_profesional', ''),
                                   placeholder="Ej: Data Analyst | BI Developer")

        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("🌆 Ciudad", value=p.get('ciudad', ''),
                                   placeholder="Ej: Bogotá, Colombia")
        with c2:
            direccion = st.text_input("📍 Dirección", value=p.get('direccion', ''),
                                      placeholder="Ej: Cra 7 # 45-20")

        c1, c2, c3 = st.columns(3)
        with c1:
            celular = st.text_input("📱 Celular", value=p.get('celular', ''),
                                    placeholder="Ej: +57 310 123 4567")
        with c2:
            correo = st.text_input("📧 Correo", value=p.get('correo', ''),
                                   placeholder="Ej: juan@email.com")
        with c3:
            nivel = st.selectbox(
                "📊 Nivel actual *", options=NIVELES_SENIORITY,
                index=NIVELES_SENIORITY.index(p['nivel_actual'])
                if p.get('nivel_actual') in NIVELES_SENIORITY else 1
            )

        c1, c2 = st.columns(2)
        with c1:
            linkedin = st.text_input("🔗 LinkedIn", value=p.get('perfil_linkedin', ''),
                                     placeholder="https://linkedin.com/in/tu-perfil")
        with c2:
            github = st.text_input("🐙 GitHub", value=p.get('perfil_github', ''),
                                   placeholder="https://github.com/tu-usuario")

        st.divider()
        st.markdown("**💰 Aspiración Salarial y Modalidad**")

        c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
        with c1:
            salario_min = st.number_input(
                "Salario mínimo", min_value=0.0,
                value=float(p['salario_min']) if p.get('salario_min') else 0.0,
                step=100000.0, format="%.0f"
            )
        with c2:
            salario_max = st.number_input(
                "Salario máximo", min_value=0.0,
                value=float(p['salario_max']) if p.get('salario_max') else 0.0,
                step=100000.0, format="%.0f"
            )
        with c3:
            moneda = st.selectbox(
                "Moneda", options=MONEDAS,
                index=MONEDAS.index(p['moneda']) if p.get('moneda') in MONEDAS else 0
            )
        with c4:
            anos_exp = st.number_input(
                "Años de experiencia", min_value=0, max_value=50,
                value=int(p.get('anos_experiencia', 0))
            )

        modalidades_actuales = p.get('modalidades_aceptadas', 'Remoto,Híbrido,Presencial')
        modalidades_lista    = [m.strip() for m in modalidades_actuales.split(',') if m.strip()]
        modalidades_sel = st.multiselect(
            "📍 Modalidades aceptadas *", options=MODALIDADES,
            default=[m for m in modalidades_lista if m in MODALIDADES]
        )

        submitted = st.form_submit_button(
            "💾 Guardar Datos Personales", use_container_width=True, type="primary"
        )

    if submitted:
        errores = []
        if not nombre.strip():  errores.append("El nombre es obligatorio.")
        if not titulo.strip():  errores.append("El título profesional es obligatorio.")
        if not modalidades_sel: errores.append("Selecciona al menos una modalidad.")
        if salario_max > 0 and salario_min > salario_max:
            errores.append("El salario mínimo no puede ser mayor al máximo.")

        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            res = database.guardar_perfil({
                'nombre': nombre, 'titulo_profesional': titulo,
                'ciudad': ciudad, 'direccion': direccion,
                'celular': celular, 'correo': correo,
                'perfil_linkedin': linkedin, 'perfil_github': github,
                'nivel_actual': nivel, 'anos_experiencia': anos_exp,
                'salario_min': salario_min if salario_min > 0 else None,
                'salario_max': salario_max if salario_max > 0 else None,
                'moneda': moneda,
                'modalidades_aceptadas': ','.join(modalidades_sel),
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.8)
                st.rerun()
            else:
                st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 2 — Skills
# ─────────────────────────────────────────────────────────────

def _tab_skills(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    if 'skills_categorias_custom' not in st.session_state:
        st.session_state.skills_categorias_custom = []
    if 'skill_ultima_categoria' not in st.session_state:
        st.session_state.skill_ultima_categoria = CATEGORIAS_SKILL_DEFAULT[0]

    # ── FORM ARRIBA ───────────────────────────────────────────
    st.markdown("#### ➕ Agregar Skill")

    with st.expander("🏷️ Crear nueva categoría personalizada"):
        col_nc, col_btn = st.columns([3, 1])
        with col_nc:
            nueva_cat = st.text_input(
                "Nombre", placeholder="Ej: Machine Learning",
                key="nueva_categoria_input", label_visibility="collapsed"
            )
        with col_btn:
            if st.button("➕ Crear", key="btn_nueva_cat", use_container_width=True):
                nc = nueva_cat.strip()
                categorias_actuales = _get_categorias()
                if not nc:
                    st.error("⚠️ Escribe un nombre.")
                elif nc in categorias_actuales:
                    st.warning(f"'{nc}' ya existe.")
                else:
                    st.session_state.skills_categorias_custom.append(nc)
                    st.session_state.skill_ultima_categoria = nc
                    st.success(f"✓ Categoría '{nc}' creada.")
                    time.sleep(0.4)
                    st.rerun()

    categorias = _get_categorias()
    idx_cat = categorias.index(st.session_state.skill_ultima_categoria) \
              if st.session_state.skill_ultima_categoria in categorias else 0

    with st.form("form_skill", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            categoria = st.selectbox("Categoría *", options=categorias, index=idx_cat)
        with c2:
            skill_nombre = st.text_input(
                "Skill *", placeholder="Ej: SQL, Python, Power BI, Inglés"
            )
        with c3:
            es_idioma = (st.session_state.skill_ultima_categoria == 'Idiomas')
            nivel_ops = NIVELES_IDIOMA if es_idioma else NIVELES_SKILL_TECNICO
            nivel     = st.selectbox("Nivel *", options=nivel_ops)

        submitted = st.form_submit_button(
            "➕ Agregar Skill", use_container_width=True, type="primary"
        )

    if submitted:
        if not skill_nombre.strip():
            st.error("⚠️ El nombre de la skill es obligatorio.")
        else:
            st.session_state.skill_ultima_categoria = categoria
            res = database.insertar_skill(perfil_id, categoria, skill_nombre, nivel)
            if res['success']:
                st.success(res['message'])
                time.sleep(0.4)
                st.rerun()
            else:
                st.error(res['message'])

    # ── REGISTROS DEBAJO con scroll ───────────────────────────
    st.markdown("---")
    st.markdown("#### Skills registradas")

    skills = database.obtener_skills(perfil_id)
    if not skills:
        st.info("📭 Aún no tienes skills registradas.")
        return

    cats_en_bd: dict = {}
    for s in skills:
        cats_en_bd.setdefault(s['categoria'], []).append(s)

    with st.container(height=350):
        for cat, items in cats_en_bd.items():
            st.markdown(f"**{cat}**")
            for s in items:
                col_skill, col_nivel, col_del = st.columns([3, 2, 1])
                with col_skill:  st.write(s['skill'])
                with col_nivel:  st.write(f"`{s['nivel']}`")
                with col_del:
                    if st.button("🗑️", key=f"del_skill_{s['id']}", help="Eliminar"):
                        res = database.eliminar_skill(s['id'])
                        if res['success']:
                            st.toast("✅ Skill eliminada")
                            time.sleep(0.3)
                            st.rerun()
                        else:
                            st.error(res['message'])
            st.divider()


# ─────────────────────────────────────────────────────────────
# TAB 3 — Experiencia Laboral
# ─────────────────────────────────────────────────────────────

def _tab_experiencia(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    # ── FORM ARRIBA ───────────────────────────────────────────
    st.markdown("#### ➕ Agregar Experiencia")

    with st.form("form_experiencia", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cargo   = st.text_input("Cargo *", placeholder="Ej: Data Analyst")
        with c2:
            empresa = st.text_input("Empresa *", placeholder="Ej: Bancolombia")

        c1, c2 = st.columns(2)
        with c1:
            ciudad       = st.text_input("Ciudad", placeholder="Ej: Medellín")
        with c2:
            desc_empresa = st.text_input(
                "Descripción empresa", placeholder="Ej: Fintech, 500+ empleados"
            )

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today())
        with c2:
            fecha_fin    = st.date_input("Fecha fin", value=None)
        with c3:
            es_actual = st.checkbox("Trabajo actual", value=False)

        funciones = st.text_area(
            "Funciones", placeholder="Describe las principales responsabilidades...",
            height=100
        )
        logros = st.text_area(
            "Logros", placeholder="Ej: Reduje el tiempo de reportes en 40%...",
            height=100
        )

        submitted = st.form_submit_button(
            "➕ Agregar Experiencia", use_container_width=True, type="primary"
        )

    if submitted:
        errores = []
        if not cargo.strip():   errores.append("El cargo es obligatorio.")
        if not empresa.strip(): errores.append("La empresa es obligatoria.")
        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            res = database.insertar_experiencia(perfil_id, {
                'cargo': cargo, 'empresa': empresa, 'ciudad': ciudad,
                'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                'es_trabajo_actual': es_actual,
                'descripcion_empresa': desc_empresa,
                'funciones': funciones, 'logros': logros,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])

    # ── REGISTROS DEBAJO con scroll ───────────────────────────
    st.markdown("---")
    st.markdown("#### Experiencias registradas")

    experiencias = database.obtener_experiencias(perfil_id)
    if not experiencias:
        st.info("📭 Aún no tienes experiencias registradas.")
        return

    if 'exp_editando_id' not in st.session_state:
        st.session_state.exp_editando_id = None

    with st.container(height=500):
        for exp in experiencias:
            fecha_fin_str = "Actualidad" if exp['es_trabajo_actual'] \
                            else _fmt_fecha(exp['fecha_fin'])
            label = (f"💼 {exp['cargo']} — {exp['empresa']}  "
                     f"({_fmt_fecha(exp['fecha_inicio'])} → {fecha_fin_str})")

            with st.expander(label):

                # ── MODO VISTA ────────────────────────────────
                if st.session_state.exp_editando_id != exp['id']:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Ciudad:** {exp['ciudad'] or '—'}")
                        if exp['descripcion_empresa']:
                            st.markdown(f"**Empresa:** {exp['descripcion_empresa']}")
                    with c2:
                        st.markdown(
                            f"**Período:** {_fmt_fecha(exp['fecha_inicio'])} → {fecha_fin_str}"
                        )
                    if exp['funciones']:
                        st.markdown("**Funciones:**")
                        st.write(exp['funciones'])
                    if exp['logros']:
                        st.markdown("**Logros:**")
                        st.write(exp['logros'])

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("✏️ Editar", key=f"btn_edit_exp_{exp['id']}",
                                     use_container_width=True):
                            st.session_state.exp_editando_id = exp['id']
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Eliminar", key=f"del_exp_{exp['id']}",
                                     type="secondary", use_container_width=True):
                            res = database.eliminar_experiencia(exp['id'])
                            if res['success']:
                                st.toast("✅ Experiencia eliminada")
                                time.sleep(0.3)
                                st.rerun()
                            else:
                                st.error(res['message'])

                # ── MODO EDICIÓN ──────────────────────────────
                else:
                    st.markdown("**✏️ Editando experiencia**")

                    with st.form(f"form_edit_exp_{exp['id']}"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_cargo   = st.text_input("Cargo *", value=exp['cargo'])
                        with ec2:
                            e_empresa = st.text_input("Empresa *", value=exp['empresa'])

                        ec1, ec2 = st.columns(2)
                        with ec1:
                            e_ciudad = st.text_input("Ciudad", value=exp['ciudad'] or '')
                        with ec2:
                            e_desc   = st.text_input(
                                "Descripción empresa",
                                value=exp['descripcion_empresa'] or ''
                            )

                        ec1, ec2, ec3 = st.columns([2, 2, 1])
                        with ec1:
                            e_fi = st.date_input(
                                "Fecha inicio *",
                                value=exp['fecha_inicio'] if exp['fecha_inicio'] else date.today(),
                                key=f"efi_{exp['id']}"
                            )
                        with ec2:
                            e_ff = st.date_input(
                                "Fecha fin",
                                value=exp['fecha_fin'] if exp['fecha_fin'] else None,
                                key=f"eff_{exp['id']}"
                            )
                        with ec3:
                            e_actual = st.checkbox(
                                "Actual", value=exp['es_trabajo_actual'],
                                key=f"eact_{exp['id']}"
                            )

                        e_funciones = st.text_area(
                            "Funciones", value=exp['funciones'] or '',
                            height=100, key=f"efunc_{exp['id']}"
                        )
                        e_logros = st.text_area(
                            "Logros", value=exp['logros'] or '',
                            height=100, key=f"elogr_{exp['id']}"
                        )

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            save = st.form_submit_button(
                                "💾 Guardar cambios",
                                use_container_width=True, type="primary"
                            )
                        with col_cancel:
                            cancel = st.form_submit_button(
                                "✖️ Cancelar", use_container_width=True
                            )

                    if save:
                        errores = []
                        if not e_cargo.strip():   errores.append("El cargo es obligatorio.")
                        if not e_empresa.strip(): errores.append("La empresa es obligatoria.")
                        if errores:
                            for e in errores: st.error(f"⚠️ {e}")
                        else:
                            res = database.actualizar_experiencia(exp['id'], {
                                'cargo': e_cargo, 'empresa': e_empresa,
                                'ciudad': e_ciudad, 'descripcion_empresa': e_desc,
                                'fecha_inicio': e_fi, 'fecha_fin': e_ff,
                                'es_trabajo_actual': e_actual,
                                'funciones': e_funciones, 'logros': e_logros,
                            })
                            if res['success']:
                                st.success(res['message'])
                                st.session_state.exp_editando_id = None
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(res['message'])

                    if cancel:
                        st.session_state.exp_editando_id = None
                        st.rerun()


# ─────────────────────────────────────────────────────────────
# TAB 4 — Proyectos
# ─────────────────────────────────────────────────────────────

def _tab_proyectos(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### ➕ Agregar Proyecto")

    with st.form("form_proyecto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre  = st.text_input("Nombre del proyecto *",
                                    placeholder="Ej: Dashboard de Ventas")
        with c2:
            empresa = st.text_input("Empresa",
                                    placeholder="Dejar vacío si es personal")

        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Bogotá")
        with c2:
            stack  = st.text_input("Stack tecnológico",
                                   placeholder="Ej: Python, SQL, Power BI, Azure")

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today(), key="proy_fi")
        with c2:
            fecha_fin    = st.date_input("Fecha fin", value=None, key="proy_ff")
        with c3:
            es_actual = st.checkbox("En curso", value=False)

        url_repo  = st.text_input("URL Repositorio",
                                   placeholder="https://github.com/...")
        funciones = st.text_area("Descripción",
                                  placeholder="¿Qué hiciste en este proyecto?", height=90)
        logros    = st.text_area("Logros / Impacto",
                                  placeholder="Ej: Automaticé X, reduciendo Y en Z%",
                                  height=90)

        submitted = st.form_submit_button(
            "➕ Agregar Proyecto", use_container_width=True, type="primary"
        )

    if submitted:
        if not nombre.strip():
            st.error("⚠️ El nombre del proyecto es obligatorio.")
        else:
            res = database.insertar_proyecto(perfil_id, {
                'nombre': nombre, 'empresa': empresa, 'ciudad': ciudad,
                'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                'es_proyecto_actual': es_actual, 'stack': stack,
                'funciones': funciones, 'logros': logros,
                'url_repositorio': url_repo,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])

    st.markdown("---")
    st.markdown("#### Proyectos registrados")

    proyectos = database.obtener_proyectos(perfil_id)
    if not proyectos:
        st.info("📭 Aún no tienes proyectos registrados.")
        return

    with st.container(height=450):
        for p in proyectos:
            fecha_fin_str = "En curso" if p['es_proyecto_actual'] \
                            else _fmt_fecha(p['fecha_fin'])
            with st.expander(
                f"🚀 {p['nombre']}  "
                f"({_fmt_fecha(p['fecha_inicio'])} → {fecha_fin_str})"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Empresa:** {p['empresa'] or 'Personal'}")
                    st.markdown(f"**Ciudad:** {p['ciudad'] or '—'}")
                with c2:
                    st.markdown(f"**Stack:** {p['stack'] or '—'}")
                    if p['url_repositorio']:
                        st.markdown(
                            f"**Repo:** [{p['url_repositorio']}]({p['url_repositorio']})"
                        )
                if p['funciones']:
                    st.markdown("**Descripción:**")
                    st.write(p['funciones'])
                if p['logros']:
                    st.markdown("**Logros / Impacto:**")
                    st.write(p['logros'])

                if st.button("🗑️ Eliminar", key=f"del_proy_{p['id']}", type="secondary"):
                    res = database.eliminar_proyecto(p['id'])
                    if res['success']:
                        st.toast("✅ Proyecto eliminado")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 5 — Educación
# ─────────────────────────────────────────────────────────────

def _tab_educacion(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### ➕ Agregar Educación")

    with st.form("form_educacion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo      = st.text_input("Título *",
                                        placeholder="Ej: Ingeniería de Sistemas")
        with c2:
            institucion = st.text_input("Institución *",
                                        placeholder="Ej: Universidad Nacional")

        c1, c2, c3 = st.columns(3)
        with c1:
            nivel  = st.selectbox("Nivel *", options=NIVELES_EDUCACION)
        with c2:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Bogotá")
        with c3:
            status = st.selectbox("Status *", options=STATUS_EDUCACION, index=1)

        c1, c2 = st.columns(2)
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today(), key="edu_fi")
        with c2:
            fecha_fin    = st.date_input("Fecha fin", value=None, key="edu_ff")

        submitted = st.form_submit_button(
            "➕ Agregar Educación", use_container_width=True, type="primary"
        )

    if submitted:
        errores = []
        if not titulo.strip():      errores.append("El título es obligatorio.")
        if not institucion.strip(): errores.append("La institución es obligatoria.")
        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            res = database.insertar_educacion(perfil_id, {
                'titulo': titulo, 'institucion': institucion, 'ciudad': ciudad,
                'nivel': nivel, 'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin, 'status': status,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])

    st.markdown("---")
    st.markdown("#### Educación registrada")

    educacion = database.obtener_educacion(perfil_id)
    if not educacion:
        st.info("📭 Aún no tienes formación registrada.")
        return

    with st.container(height=350):
        for e in educacion:
            with st.expander(
                f"🎓 {e['titulo']} — {e['institucion']}  "
                f"({_fmt_fecha(e['fecha_inicio'])} → {_fmt_fecha(e['fecha_fin'])})  "
                f"[{e['status']}]"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Nivel:** {e['nivel']}")
                    st.markdown(f"**Ciudad:** {e['ciudad'] or '—'}")
                with c2:
                    st.markdown(f"**Status:** `{e['status']}`")

                if st.button("🗑️ Eliminar", key=f"del_edu_{e['id']}", type="secondary"):
                    res = database.eliminar_educacion(e['id'])
                    if res['success']:
                        st.toast("✅ Educación eliminada")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 6 — Cursos
# ─────────────────────────────────────────────────────────────

def _tab_cursos(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### ➕ Agregar Curso")

    with st.form("form_curso", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo      = st.text_input("Título del curso *",
                                        placeholder="Ej: SQL para Análisis de Datos")
        with c2:
            institucion = st.text_input("Plataforma / Institución *",
                                        placeholder="Ej: Udemy, Coursera, Platzi")

        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_inicio = st.date_input("Fecha inicio", value=None, key="cur_fi")
        with c2:
            fecha_fin    = st.date_input("Fecha fin", value=None, key="cur_ff")
        with c3:
            status = st.selectbox("Status *", options=STATUS_CURSOS, index=1)

        url_cert = st.text_input("URL Certificado",
                                  placeholder="https://udemy.com/certificate/...")

        submitted = st.form_submit_button(
            "➕ Agregar Curso", use_container_width=True, type="primary"
        )

    if submitted:
        errores = []
        if not titulo.strip():      errores.append("El título es obligatorio.")
        if not institucion.strip(): errores.append("La institución es obligatoria.")
        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            res = database.insertar_curso(perfil_id, {
                'titulo': titulo, 'institucion': institucion,
                'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                'status': status, 'url_certificado': url_cert,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])

    st.markdown("---")
    st.markdown("#### Cursos registrados")

    cursos = database.obtener_cursos(perfil_id)
    if not cursos:
        st.info("📭 Aún no tienes cursos registrados.")
        return

    with st.container(height=350):
        for c in cursos:
            with st.expander(
                f"📚 {c['titulo']} — {c['institucion']}  [{c['status']}]"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"**Período:** {_fmt_fecha(c['fecha_inicio'])} → "
                        f"{_fmt_fecha(c['fecha_fin'])}"
                    )
                with col2:
                    if c['url_certificado']:
                        st.markdown(
                            f"**Certificado:** [Ver ↗]({c['url_certificado']})"
                        )

                if st.button("🗑️ Eliminar", key=f"del_cur_{c['id']}", type="secondary"):
                    res = database.eliminar_curso(c['id'])
                    if res['success']:
                        st.toast("✅ Curso eliminado")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 7 — Certificaciones
# ─────────────────────────────────────────────────────────────

def _tab_certificaciones(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### ➕ Agregar Certificación")

    with st.form("form_cert", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo      = st.text_input("Título *",
                                        placeholder="Ej: AWS Certified Data Analytics")
        with c2:
            institucion = st.text_input("Institución emisora *",
                                        placeholder="Ej: Amazon Web Services")

        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_obt  = st.date_input("Fecha obtención *", value=date.today(),
                                       key="cert_fo")
        with c2:
            fecha_venc = st.date_input("Fecha vencimiento", value=None,
                                       key="cert_fv", help="Dejar vacío si no vence")
        with c3:
            status = st.selectbox("Status *", options=STATUS_CERT)

        url_cert = st.text_input("URL Certificado / Credly",
                                  placeholder="https://credly.com/...")

        submitted = st.form_submit_button(
            "➕ Agregar Certificación", use_container_width=True, type="primary"
        )

    if submitted:
        errores = []
        if not titulo.strip():      errores.append("El título es obligatorio.")
        if not institucion.strip(): errores.append("La institución es obligatoria.")
        if errores:
            for e in errores: st.error(f"⚠️ {e}")
        else:
            res = database.insertar_certificacion(perfil_id, {
                'titulo': titulo, 'institucion': institucion,
                'fecha_obtencion': fecha_obt,
                'fecha_vencimiento': fecha_venc,
                'status': status, 'url_certificado': url_cert,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])

    st.markdown("---")
    st.markdown("#### Certificaciones registradas")

    certs = database.obtener_certificaciones(perfil_id)
    if not certs:
        st.info("📭 Aún no tienes certificaciones registradas.")
        return

    with st.container(height=350):
        for cert in certs:
            vence_str = _fmt_fecha(cert['fecha_vencimiento']) \
                        if cert['fecha_vencimiento'] else 'No vence'
            with st.expander(
                f"🏆 {cert['titulo']} — {cert['institucion']}  [{cert['status']}]"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Obtenida:** {_fmt_fecha(cert['fecha_obtencion'])}")
                    st.markdown(f"**Vence:** {vence_str}")
                with c2:
                    st.markdown(f"**Status:** `{cert['status']}`")
                    if cert['url_certificado']:
                        st.markdown(
                            f"**Certificado:** [Ver ↗]({cert['url_certificado']})"
                        )

                if st.button("🗑️ Eliminar", key=f"del_cert_{cert['id']}", type="secondary"):
                    res = database.eliminar_certificacion(cert['id'])
                    if res['success']:
                        st.toast("✅ Certificación eliminada")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 8 — Vista CV
# ─────────────────────────────────────────────────────────────

def _tab_vista_cv(perfil, perfil_id):
    """
    Vista de lectura del perfil completo con la estructura
    visual del CV: encabezado, habilidades, experiencia,
    educación, certificaciones y cursos.
    """
    if not perfil or not perfil_id:
        st.warning("⚠️ Completa tus **Datos Personales** para ver la Vista CV.")
        return

    st.markdown("""
    <style>
    .cv-wrap {
        max-width: 860px;
        margin: 0 auto;
        font-family: 'Segoe UI', Calibri, sans-serif;
        color: #1a1a1a;
        padding: 8px 0;
    }
    .cv-header    { text-align: center; margin-bottom: 6px; }
    .cv-name      {
        font-size: 1.65rem; font-weight: 800;
        letter-spacing: 0.05em; text-transform: uppercase;
        color: #111; margin-bottom: 3px;
    }
    .cv-titulo    {
        font-size: 0.76rem; font-weight: 600; color: #444;
        letter-spacing: 0.14em; text-transform: uppercase;
        margin-bottom: 5px;
    }
    .cv-tags      { font-size: 0.71rem; color: #666; margin-bottom: 5px; }
    .cv-contact   { font-size: 0.71rem; color: #555; }
    .cv-contact a { color: #1a73e8; text-decoration: none; }
    .cv-hr        { border: none; border-top: 2px solid #111; margin: 10px 0 14px; }
    .cv-hr-thin   { border: none; border-top: 1px solid #ccc; margin: 10px 0 14px; }
    .cv-sec-title {
        font-size: 0.71rem; font-weight: 800;
        letter-spacing: 0.16em; text-transform: uppercase;
        color: #111; margin-bottom: 8px;
    }
    .cv-resumen   { font-size: 0.8rem; line-height: 1.7; color: #333; }
    .cv-skill-row {
        display: flex; gap: 6px; align-items: baseline;
        margin-bottom: 3px; font-size: 0.77rem;
    }
    .cv-skill-cat { font-weight: 700; color: #111; min-width: 200px; flex-shrink: 0; }
    .cv-skill-lst { color: #333; }
    .cv-exp-hdr   {
        display: flex; justify-content: space-between;
        align-items: baseline; margin-bottom: 1px;
    }
    .cv-exp-cargo {
        font-size: 0.8rem; font-weight: 700;
        text-transform: uppercase; color: #111;
    }
    .cv-exp-fecha { font-size: 0.71rem; color: #555; font-style: italic; }
    .cv-exp-emp   { font-size: 0.77rem; color: #444; font-style: italic; margin-bottom: 5px; }
    .cv-bullet    {
        font-size: 0.77rem; color: #333; line-height: 1.65;
        padding-left: 14px; text-indent: -8px; margin-bottom: 2px;
    }
    .cv-bullet::before { content: "• "; color: #111; }
    .cv-edu-row   {
        display: flex; justify-content: space-between;
        font-size: 0.77rem; margin-bottom: 3px;
    }
    .cv-edu-tit   { font-weight: 600; color: #111; }
    .cv-edu-inst  { color: #555; font-style: italic; }
    .cv-edu-fecha { color: #666; white-space: nowrap; margin-left: 8px; }
    .cv-subsec    {
        font-size: 0.69rem; font-weight: 700; color: #555;
        letter-spacing: 0.1em; text-transform: uppercase;
        margin: 8px 0 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Cargar datos ──────────────────────────────────────────
    skills       = database.obtener_skills(perfil_id)
    experiencias = database.obtener_experiencias(perfil_id)
    educacion    = database.obtener_educacion(perfil_id)
    cursos       = database.obtener_cursos(perfil_id)
    certs        = database.obtener_certificaciones(perfil_id)

    # ── Construir HTML ────────────────────────────────────────
    html = '<div class="cv-wrap">'

    # ENCABEZADO
    nombre = perfil.get('nombre', '').upper()
    titulo = perfil.get('titulo_profesional', '')
    tags   = ' • '.join([t.strip() for t in titulo.replace('|', '•').split('•') if t.strip()])

    contacto = []
    if perfil.get('correo'):
        contacto.append(perfil['correo'])
    if perfil.get('perfil_linkedin'):
        url = perfil['perfil_linkedin']
        contacto.append(f"<a href='{url}' target='_blank'>{url}</a>")
    if perfil.get('ciudad'):
        contacto.append(perfil['ciudad'])
    if perfil.get('celular'):
        contacto.append(perfil['celular'])

    html += f"""
    <div class="cv-header">
        <div class="cv-name">{nombre}</div>
        <div class="cv-titulo">{titulo}</div>
        <div class="cv-tags">{tags}</div>
        <div class="cv-contact">{' • '.join(contacto)}</div>
    </div>
    <hr class="cv-hr">
    """

    # RESUMEN — usamos el título como placeholder hasta tener cv_base
    html += f"""
    <div class="cv-sec-title">Resumen Profesional</div>
    <div class="cv-resumen">{titulo}</div>
    <hr class="cv-hr-thin">
    """

    # HABILIDADES
    if skills:
        html += '<div class="cv-sec-title">Habilidades</div>'
        cats: dict = {}
        for s in skills:
            cats.setdefault(s['categoria'], []).append(s['skill'])
        for cat, lista in cats.items():
            html += f"""
            <div class="cv-skill-row">
                <span class="cv-skill-cat">{cat}:</span>
                <span class="cv-skill-lst">{' • '.join(lista)}</span>
            </div>"""
        html += '<hr class="cv-hr-thin">'

    # EXPERIENCIA LABORAL
    if experiencias:
        html += '<div class="cv-sec-title">Experiencia Laboral</div>'
        for exp in experiencias:
            ff_str  = "Actualidad" if exp['es_trabajo_actual'] else _fmt_fecha(exp['fecha_fin'])
            fi_str  = _fmt_fecha(exp['fecha_inicio'])
            ciudad_str = f" | {exp['ciudad']}" if exp.get('ciudad') else ''
            html += f"""
            <div class="cv-exp-hdr">
                <span class="cv-exp-cargo">{exp['cargo']}</span>
                <span class="cv-exp-fecha">{fi_str} – {ff_str}</span>
            </div>
            <div class="cv-exp-emp">{exp['empresa']}{ciudad_str}</div>
            """
            for bloque in [exp.get('funciones'), exp.get('logros')]:
                if bloque:
                    for linea in bloque.split('\n'):
                        l = linea.lstrip('•- ').strip()
                        if l:
                            html += f'<div class="cv-bullet">{l}</div>'
            html += '<div style="margin-bottom:10px"></div>'
        html += '<hr class="cv-hr-thin">'

    # EDUCACIÓN Y FORMACIÓN
    if educacion or certs or cursos:
        html += '<div class="cv-sec-title">Educación y Formación</div>'

        if educacion:
            html += '<div class="cv-subsec">Educación</div>'
            for e in educacion:
                fi = _fmt_fecha(e['fecha_inicio'])
                ff = _fmt_fecha(e['fecha_fin']) if e['fecha_fin'] else e['status']
                inst = e['institucion']
                if e.get('ciudad'): inst += f" | {e['ciudad']}"
                html += f"""
                <div class="cv-edu-row">
                    <span>
                        <span class="cv-edu-tit">{e['titulo']}</span>
                        — <span class="cv-edu-inst">{inst}</span>
                    </span>
                    <span class="cv-edu-fecha">{fi} – {ff}</span>
                </div>"""

        if certs:
            html += '<div class="cv-subsec">Certificaciones</div>'
            for cert in certs:
                fo     = _fmt_fecha(cert['fecha_obtencion'])
                status = cert['status']
                html += f"""
                <div class="cv-edu-row">
                    <span>
                        <span class="cv-edu-tit">{cert['titulo']}</span>
                        — <span class="cv-edu-inst">{cert['institucion']}</span>
                    </span>
                    <span class="cv-edu-fecha">{fo} [{status}]</span>
                </div>"""

        if cursos:
            html += '<div class="cv-subsec">Cursos Relevantes</div>'
            html += f'<div style="font-size:0.77rem;color:#333;line-height:1.7">'
            html += ' • '.join([c['titulo'] for c in cursos])
            html += '</div>'

    html += '</div>'  # cv-wrap

    st.markdown(html, unsafe_allow_html=True)