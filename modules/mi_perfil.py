"""
modules/mi_perfil.py
Pestaña: Mi Perfil — gestión completa del perfil profesional.

Estructura visual:
  Tabs: Datos Personales | Skills | Experiencia |
        Proyectos | Educación | Cursos | Certificaciones

Cada tab tiene:
  - Vista de registros existentes (tabla o tarjetas)
  - Formulario para agregar nuevos registros
  - Botón eliminar por registro
  - Botón guardar propio
"""

import streamlit as st
import database
from datetime import date, datetime
import time


# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

NIVELES_SENIORITY = ['Junior', 'Mid', 'Senior']

CATEGORIAS_SKILL = [
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

STATUS_EDUCACION    = ['En curso', 'Completado', 'Pausado', 'Abandonado']
STATUS_CURSOS       = ['En curso', 'Completado', 'Pausado']
STATUS_CERT         = ['Vigente', 'Vencido', 'En proceso']

MODALIDADES = ['Remoto', 'Presencial', 'Híbrido']

MONEDAS = ['COP', 'USD', 'EUR', 'MXN', 'ARS']


# ─────────────────────────────────────────────────────────────
# HELPER — formatear fechas
# ─────────────────────────────────────────────────────────────

def _fmt_fecha(fecha) -> str:
    """Convierte date/datetime a string legible. Retorna '—' si es None."""
    if not fecha:
        return '—'
    if isinstance(fecha, (datetime, date)):
        return fecha.strftime('%m/%Y')
    return str(fecha)


# ─────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────

def mostrar_mi_perfil():
    """
    Función principal. Se llama desde app.py en la pestaña 'Mi Perfil'.
    """
    st.subheader("Mi Perfil Profesional")

    # Cargar perfil activo
    perfil = database.obtener_perfil()

    if not perfil:
        st.info(
            "👋 Aún no tienes un perfil creado. "
            "Completa la pestaña **Datos Personales** para comenzar."
        )

    # ── Tabs ─────────────────────────────────────────────────
    tabs = st.tabs([
        "👤 Datos Personales",
        "🛠️ Skills",
        "💼 Experiencia",
        "🚀 Proyectos",
        "🎓 Educación",
        "📚 Cursos",
        "🏆 Certificaciones",
    ])

    with tabs[0]:
        _tab_datos_personales(perfil)

    # Las demás tabs requieren que exista un perfil
    perfil_id = perfil['id'] if perfil else None

    with tabs[1]:
        _tab_skills(perfil_id)

    with tabs[2]:
        _tab_experiencia(perfil_id)

    with tabs[3]:
        _tab_proyectos(perfil_id)

    with tabs[4]:
        _tab_educacion(perfil_id)

    with tabs[5]:
        _tab_cursos(perfil_id)

    with tabs[6]:
        _tab_certificaciones(perfil_id)


# ─────────────────────────────────────────────────────────────
# TAB 1 — Datos Personales
# ─────────────────────────────────────────────────────────────

def _tab_datos_personales(perfil: dict):
    st.markdown("#### Información Personal y Profesional")

    # Valores por defecto desde BD o vacíos
    p = perfil or {}

    with st.form("form_datos_personales"):

        # ── Fila 1: Nombre y Título ───────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input(
                "👤 Nombre completo *",
                value=p.get('nombre', ''),
                placeholder="Ej: Juan Pérez García"
            )
        with c2:
            titulo = st.text_input(
                "💼 Título profesional *",
                value=p.get('titulo_profesional', ''),
                placeholder="Ej: Data Analyst | BI Developer"
            )

        # ── Fila 2: Ciudad y Dirección ────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input(
                "🌆 Ciudad",
                value=p.get('ciudad', ''),
                placeholder="Ej: Bogotá, Colombia"
            )
        with c2:
            direccion = st.text_input(
                "📍 Dirección",
                value=p.get('direccion', ''),
                placeholder="Ej: Cra 7 # 45-20"
            )

        # ── Fila 3: Contacto ──────────────────────────────────
        c1, c2, c3 = st.columns(3)
        with c1:
            celular = st.text_input(
                "📱 Celular",
                value=p.get('celular', ''),
                placeholder="Ej: +57 310 123 4567"
            )
        with c2:
            correo = st.text_input(
                "📧 Correo",
                value=p.get('correo', ''),
                placeholder="Ej: juan@email.com"
            )
        with c3:
            nivel = st.selectbox(
                "📊 Nivel actual *",
                options=NIVELES_SENIORITY,
                index=NIVELES_SENIORITY.index(p['nivel_actual'])
                      if p.get('nivel_actual') in NIVELES_SENIORITY else 1
            )

        # ── Fila 4: Links ─────────────────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            linkedin = st.text_input(
                "🔗 LinkedIn",
                value=p.get('perfil_linkedin', ''),
                placeholder="https://linkedin.com/in/tu-perfil"
            )
        with c2:
            github = st.text_input(
                "🐙 GitHub",
                value=p.get('perfil_github', ''),
                placeholder="https://github.com/tu-usuario"
            )

        st.divider()
        st.markdown("**💰 Aspiración Salarial y Modalidad**")

        # ── Fila 5: Salario ───────────────────────────────────
        c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
        with c1:
            salario_min = st.number_input(
                "Salario mínimo",
                min_value=0.0,
                value=float(p['salario_min']) if p.get('salario_min') else 0.0,
                step=100000.0,
                format="%.0f"
            )
        with c2:
            salario_max = st.number_input(
                "Salario máximo",
                min_value=0.0,
                value=float(p['salario_max']) if p.get('salario_max') else 0.0,
                step=100000.0,
                format="%.0f"
            )
        with c3:
            moneda = st.selectbox(
                "Moneda",
                options=MONEDAS,
                index=MONEDAS.index(p['moneda'])
                      if p.get('moneda') in MONEDAS else 0
            )
        with c4:
            anos_exp = st.number_input(
                "Años de experiencia",
                min_value=0,
                max_value=50,
                value=int(p.get('anos_experiencia', 0))
            )

        # ── Fila 6: Modalidades ───────────────────────────────
        modalidades_actuales = p.get('modalidades_aceptadas', 'Remoto,Híbrido,Presencial')
        modalidades_lista    = [m.strip() for m in modalidades_actuales.split(',') if m.strip()]
        modalidades_sel = st.multiselect(
            "📍 Modalidades aceptadas *",
            options=MODALIDADES,
            default=[m for m in modalidades_lista if m in MODALIDADES],
        )

        # ── Submit ────────────────────────────────────────────
        submitted = st.form_submit_button(
            "💾 Guardar Datos Personales",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        # Validaciones
        errores = []
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not titulo.strip():
            errores.append("El título profesional es obligatorio.")
        if not modalidades_sel:
            errores.append("Selecciona al menos una modalidad.")
        if salario_max > 0 and salario_min > salario_max:
            errores.append("El salario mínimo no puede ser mayor al máximo.")

        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
        else:
            resultado = database.guardar_perfil({
                'nombre':               nombre,
                'titulo_profesional':   titulo,
                'ciudad':               ciudad,
                'direccion':            direccion,
                'celular':              celular,
                'correo':               correo,
                'perfil_linkedin':      linkedin,
                'perfil_github':        github,
                'nivel_actual':         nivel,
                'anos_experiencia':     anos_exp,
                'salario_min':          salario_min if salario_min > 0 else None,
                'salario_max':          salario_max if salario_max > 0 else None,
                'moneda':               moneda,
                'modalidades_aceptadas': ','.join(modalidades_sel),
            })
            if resultado['success']:
                st.success(resultado['message'])
                time.sleep(0.8)
                st.rerun()
            else:
                st.error(resultado['message'])


# ─────────────────────────────────────────────────────────────
# TAB 2 — Skills
# ─────────────────────────────────────────────────────────────

def _tab_skills(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Skills, Tecnologías e Idiomas")

    skills = database.obtener_skills(perfil_id)

    # ── Tabla de skills existentes ────────────────────────────
    if skills:
        # Agrupar por categoría
        categorias = {}
        for s in skills:
            cat = s['categoria']
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(s)

        for cat, items in categorias.items():
            st.markdown(f"**{cat}**")
            for s in items:
                col_skill, col_nivel, col_del = st.columns([3, 2, 1])
                with col_skill:
                    st.write(s['skill'])
                with col_nivel:
                    st.write(f"`{s['nivel']}`")
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
    else:
        st.info("📭 Aún no tienes skills registradas.")

    # ── Formulario agregar skill ──────────────────────────────
    st.markdown("#### ➕ Agregar Skill")

    with st.form("form_skill", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            categoria = st.selectbox("Categoría *", options=CATEGORIAS_SKILL)
        with c2:
            skill_nombre = st.text_input(
                "Skill *",
                placeholder="Ej: SQL, Python, Power BI, Inglés"
            )
        with c3:
            # Nivel dinámico según categoría
            es_idioma = categoria == 'Idiomas'
            nivel_ops = NIVELES_IDIOMA if es_idioma else NIVELES_SKILL_TECNICO
            nivel = st.selectbox("Nivel *", options=nivel_ops)

        submitted = st.form_submit_button(
            "➕ Agregar Skill",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        if not skill_nombre.strip():
            st.error("⚠️ El nombre de la skill es obligatorio.")
        else:
            res = database.insertar_skill(perfil_id, categoria, skill_nombre, nivel)
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 3 — Experiencia Laboral
# ─────────────────────────────────────────────────────────────

def _tab_experiencia(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Experiencia Laboral")

    experiencias = database.obtener_experiencias(perfil_id)

    # ── Tarjetas de experiencias existentes ───────────────────
    if experiencias:
        for exp in experiencias:
            fecha_fin_str = "Actualidad" if exp['es_trabajo_actual'] else _fmt_fecha(exp['fecha_fin'])
            with st.expander(
                f"💼 {exp['cargo']} — {exp['empresa']}  "
                f"({_fmt_fecha(exp['fecha_inicio'])} → {fecha_fin_str})"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Ciudad:** {exp['ciudad'] or '—'}")
                    if exp['descripcion_empresa']:
                        st.markdown(f"**Empresa:** {exp['descripcion_empresa']}")
                with c2:
                    st.markdown(f"**Período:** {_fmt_fecha(exp['fecha_inicio'])} → {fecha_fin_str}")

                if exp['funciones']:
                    st.markdown("**Funciones:**")
                    st.write(exp['funciones'])
                if exp['logros']:
                    st.markdown("**Logros:**")
                    st.write(exp['logros'])

                if st.button("🗑️ Eliminar", key=f"del_exp_{exp['id']}", type="secondary"):
                    res = database.eliminar_experiencia(exp['id'])
                    if res['success']:
                        st.toast("✅ Experiencia eliminada")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])
    else:
        st.info("📭 Aún no tienes experiencias registradas.")

    # ── Formulario agregar experiencia ────────────────────────
    st.markdown("#### ➕ Agregar Experiencia")

    with st.form("form_experiencia", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cargo = st.text_input("Cargo *", placeholder="Ej: Data Analyst")
        with c2:
            empresa = st.text_input("Empresa *", placeholder="Ej: Bancolombia")

        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Medellín")
        with c2:
            desc_empresa = st.text_input(
                "Descripción empresa",
                placeholder="Ej: Fintech, 500+ empleados"
            )

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today())
        with c2:
            fecha_fin = st.date_input("Fecha fin", value=None)
        with c3:
            es_actual = st.checkbox("Trabajo actual", value=False)

        funciones = st.text_area(
            "Funciones",
            placeholder="Describe las principales responsabilidades...",
            height=100
        )
        logros = st.text_area(
            "Logros",
            placeholder="Ej: Reduje el tiempo de generación de reportes en 40%...",
            height=100
        )

        submitted = st.form_submit_button(
            "➕ Agregar Experiencia",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        errores = []
        if not cargo.strip():
            errores.append("El cargo es obligatorio.")
        if not empresa.strip():
            errores.append("La empresa es obligatoria.")
        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
        else:
            res = database.insertar_experiencia(perfil_id, {
                'cargo':               cargo,
                'empresa':             empresa,
                'ciudad':              ciudad,
                'fecha_inicio':        fecha_inicio,
                'fecha_fin':           fecha_fin,
                'es_trabajo_actual':   es_actual,
                'descripcion_empresa': desc_empresa,
                'funciones':           funciones,
                'logros':              logros,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(res['message'])


# ─────────────────────────────────────────────────────────────
# TAB 4 — Proyectos
# ─────────────────────────────────────────────────────────────

def _tab_proyectos(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Proyectos")

    proyectos = database.obtener_proyectos(perfil_id)

    if proyectos:
        for p in proyectos:
            fecha_fin_str = "En curso" if p['es_proyecto_actual'] else _fmt_fecha(p['fecha_fin'])
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
                        st.markdown(f"**Repo:** [{p['url_repositorio']}]({p['url_repositorio']})")

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
    else:
        st.info("📭 Aún no tienes proyectos registrados.")

    st.markdown("#### ➕ Agregar Proyecto")

    with st.form("form_proyecto", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre del proyecto *", placeholder="Ej: Dashboard de Ventas")
        with c2:
            empresa = st.text_input("Empresa", placeholder="Dejar vacío si es personal")

        c1, c2 = st.columns(2)
        with c1:
            ciudad = st.text_input("Ciudad", placeholder="Ej: Bogotá")
        with c2:
            stack = st.text_input(
                "Stack tecnológico",
                placeholder="Ej: Python, SQL, Power BI, Azure"
            )

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            fecha_inicio = st.date_input("Fecha inicio *", value=date.today(), key="proy_fi")
        with c2:
            fecha_fin = st.date_input("Fecha fin", value=None, key="proy_ff")
        with c3:
            es_actual = st.checkbox("En curso", value=False)

        url_repo = st.text_input("URL Repositorio", placeholder="https://github.com/...")
        funciones = st.text_area("Descripción", placeholder="¿Qué hiciste en este proyecto?", height=90)
        logros    = st.text_area("Logros / Impacto", placeholder="Ej: Automaticé X, reduciendo Y en Z%", height=90)

        submitted = st.form_submit_button("➕ Agregar Proyecto", use_container_width=True, type="primary")

    if submitted:
        if not nombre.strip():
            st.error("⚠️ El nombre del proyecto es obligatorio.")
        else:
            res = database.insertar_proyecto(perfil_id, {
                'nombre': nombre, 'empresa': empresa, 'ciudad': ciudad,
                'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                'es_proyecto_actual': es_actual, 'stack': stack,
                'funciones': funciones, 'logros': logros, 'url_repositorio': url_repo,
            })
            if res['success']:
                st.success(res['message'])
                time.sleep(0.5)
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

    st.markdown("#### Formación Académica")

    educacion = database.obtener_educacion(perfil_id)

    if educacion:
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
    else:
        st.info("📭 Aún no tienes formación registrada.")

    st.markdown("#### ➕ Agregar Educación")

    with st.form("form_educacion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo      = st.text_input("Título *", placeholder="Ej: Ingeniería de Sistemas")
        with c2:
            institucion = st.text_input("Institución *", placeholder="Ej: Universidad Nacional")

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
            fecha_fin = st.date_input("Fecha fin", value=None, key="edu_ff")

        submitted = st.form_submit_button("➕ Agregar Educación", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not titulo.strip():
            errores.append("El título es obligatorio.")
        if not institucion.strip():
            errores.append("La institución es obligatoria.")
        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
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


# ─────────────────────────────────────────────────────────────
# TAB 6 — Cursos
# ─────────────────────────────────────────────────────────────

def _tab_cursos(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Cursos")

    cursos = database.obtener_cursos(perfil_id)

    if cursos:
        for c in cursos:
            with st.expander(
                f"📚 {c['titulo']} — {c['institucion']}  [{c['status']}]"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        f"**Período:** {_fmt_fecha(c['fecha_inicio'])} → {_fmt_fecha(c['fecha_fin'])}"
                    )
                with col2:
                    if c['url_certificado']:
                        st.markdown(f"**Certificado:** [Ver ↗]({c['url_certificado']})")

                if st.button("🗑️ Eliminar", key=f"del_cur_{c['id']}", type="secondary"):
                    res = database.eliminar_curso(c['id'])
                    if res['success']:
                        st.toast("✅ Curso eliminado")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])
    else:
        st.info("📭 Aún no tienes cursos registrados.")

    st.markdown("#### ➕ Agregar Curso")

    with st.form("form_curso", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo      = st.text_input("Título del curso *", placeholder="Ej: SQL para Análisis de Datos")
        with c2:
            institucion = st.text_input("Plataforma / Institución *", placeholder="Ej: Udemy, Coursera, Platzi")

        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_inicio = st.date_input("Fecha inicio", value=None, key="cur_fi")
        with c2:
            fecha_fin    = st.date_input("Fecha fin", value=None, key="cur_ff")
        with c3:
            status = st.selectbox("Status *", options=STATUS_CURSOS, index=1)

        url_cert = st.text_input("URL Certificado", placeholder="https://udemy.com/certificate/...")

        submitted = st.form_submit_button("➕ Agregar Curso", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not titulo.strip():
            errores.append("El título es obligatorio.")
        if not institucion.strip():
            errores.append("La institución es obligatoria.")
        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
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


# ─────────────────────────────────────────────────────────────
# TAB 7 — Certificaciones
# ─────────────────────────────────────────────────────────────

def _tab_certificaciones(perfil_id):
    if not perfil_id:
        st.warning("⚠️ Primero completa tus **Datos Personales**.")
        return

    st.markdown("#### Certificaciones Profesionales")

    certs = database.obtener_certificaciones(perfil_id)

    if certs:
        for cert in certs:
            vence_str = _fmt_fecha(cert['fecha_vencimiento']) if cert['fecha_vencimiento'] else 'No vence'
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
                        st.markdown(f"**Certificado:** [Ver ↗]({cert['url_certificado']})")

                if st.button("🗑️ Eliminar", key=f"del_cert_{cert['id']}", type="secondary"):
                    res = database.eliminar_certificacion(cert['id'])
                    if res['success']:
                        st.toast("✅ Certificación eliminada")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(res['message'])
    else:
        st.info("📭 Aún no tienes certificaciones registradas.")

    st.markdown("#### ➕ Agregar Certificación")

    with st.form("form_cert", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo      = st.text_input("Título *", placeholder="Ej: AWS Certified Data Analytics")
        with c2:
            institucion = st.text_input("Institución emisora *", placeholder="Ej: Amazon Web Services")

        c1, c2, c3 = st.columns(3)
        with c1:
            fecha_obt  = st.date_input("Fecha obtención *", value=date.today(), key="cert_fo")
        with c2:
            fecha_venc = st.date_input("Fecha vencimiento", value=None, key="cert_fv",
                                       help="Dejar vacío si no vence")
        with c3:
            status = st.selectbox("Status *", options=STATUS_CERT)

        url_cert = st.text_input("URL Certificado / Credly", placeholder="https://credly.com/...")

        submitted = st.form_submit_button("➕ Agregar Certificación", use_container_width=True, type="primary")

    if submitted:
        errores = []
        if not titulo.strip():
            errores.append("El título es obligatorio.")
        if not institucion.strip():
            errores.append("La institución es obligatoria.")
        if errores:
            for e in errores:
                st.error(f"⚠️ {e}")
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
