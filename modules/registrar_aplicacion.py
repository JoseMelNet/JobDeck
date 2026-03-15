"""
modules/registrar_aplicacion.py - Pestaña: Registrar Nueva Aplicación

Lógica:
- Dropdown de vacantes disponibles (sin aplicación previa)
- Fecha de aplicación, estado, datos del recruiter y notas
- Validación anti-duplicados (1 aplicación por vacante)
- Limpieza del formulario tras guardar
"""

import streamlit as st
import database
from datetime import date
import time


# Estados disponibles con sus emojis para mostrar en UI
ESTADOS = ['Pendiente', 'Entrevista', 'Rechazado', 'Oferta']

ESTADO_EMOJIS = {
    'Pendiente':   '⏳ Pendiente',
    'Entrevista':  '🗓️ Entrevista',
    'Rechazado':   '❌ Rechazado',
    'Oferta':      '🎉 Oferta',
}


def mostrar_registrar_aplicacion():
    """
    Función principal que renderiza la pestaña "Registrar Aplicación".
    Se llama desde app.py.
    """
    st.subheader("Registrar Nueva Aplicación")

    # Inicializar form_key para poder limpiar el formulario
    if 'aplic_form_key' not in st.session_state:
        st.session_state.aplic_form_key = 0

    # ============================================================
    # OBTENER VACANTES DISPONIBLES (sin aplicación previa)
    # ============================================================
    vacantes_disponibles = database.obtener_vacantes_sin_aplicacion()

    if not vacantes_disponibles:
        st.info(
            "📭 No hay vacantes disponibles para aplicar. "
            "Todas tus vacantes ya tienen una aplicación registrada, "
            "o aún no has registrado ninguna vacante."
        )
        st.page_link("app.py", label="➕ Ir a Registrar Vacante", icon="📋")
        return

    # ============================================================
    # FORMULARIO
    # ============================================================
    with st.form(f"form_aplicacion_{st.session_state.aplic_form_key}", clear_on_submit=False):

        # --- VACANTE Y FECHA ---
        col_vacante, col_fecha = st.columns([3, 1])

        with col_vacante:
            # Construir opciones legibles para el dropdown
            opciones_vacantes = {
                v['id']: f"{v['empresa']}  —  {v['cargo']}  [{v['modalidad']}]"
                for v in vacantes_disponibles
            }
            vacante_id = st.selectbox(
                "💼 Vacante a la que apliqué",
                options=list(opciones_vacantes.keys()),
                format_func=lambda x: opciones_vacantes[x],
                key=f"aplic_vacante_{st.session_state.aplic_form_key}"
            )

        with col_fecha:
            fecha_aplicacion = st.date_input(
                "📅 Fecha de aplicación",
                value=date.today(),
                key=f"aplic_fecha_{st.session_state.aplic_form_key}"
            )

        # --- ESTADO ---
        estado = st.selectbox(
            "📊 Estado actual",
            options=ESTADOS,
            format_func=lambda x: ESTADO_EMOJIS[x],
            key=f"aplic_estado_{st.session_state.aplic_form_key}"
        )

        st.markdown("---")
        st.markdown("**👤 Datos del Recruiter** *(opcionales)*")

        # --- DATOS DEL RECRUITER ---
        col_nombre, col_email, col_tel = st.columns(3)

        with col_nombre:
            nombre_recruiter = st.text_input(
                "Nombre",
                placeholder="Ej: Ana García",
                key=f"aplic_recruiter_nombre_{st.session_state.aplic_form_key}"
            )

        with col_email:
            email_recruiter = st.text_input(
                "Email",
                placeholder="Ej: ana@empresa.com",
                key=f"aplic_recruiter_email_{st.session_state.aplic_form_key}"
            )

        with col_tel:
            telefono_recruiter = st.text_input(
                "Teléfono",
                placeholder="Ej: +52 55 1234 5678",
                key=f"aplic_recruiter_tel_{st.session_state.aplic_form_key}"
            )

        st.markdown("---")

        # --- NOTAS ---
        notas = st.text_area(
            "📝 Notas personales",
            placeholder="Ej: Apliqué por referido de Juan. Me pidieron portafolio. Segunda entrevista el martes...",
            height=130,
            key=f"aplic_notas_{st.session_state.aplic_form_key}"
        )

        # --- SUBMIT ---
        btn_guardar = st.form_submit_button(
            "💾 Guardar Aplicación",
            use_container_width=True,
            type="primary"
        )

    # ============================================================
    # PROCESAR GUARDADO
    # ============================================================
    if btn_guardar:
        _procesar_guardado(
            vacante_id=vacante_id,
            fecha_aplicacion=fecha_aplicacion,
            estado=estado,
            nombre_recruiter=nombre_recruiter,
            email_recruiter=email_recruiter,
            telefono_recruiter=telefono_recruiter,
            notas=notas,
        )


def _procesar_guardado(
    vacante_id: int,
    fecha_aplicacion,
    estado: str,
    nombre_recruiter: str,
    email_recruiter: str,
    telefono_recruiter: str,
    notas: str,
):
    """
    Valida y guarda la aplicación en la BD.
    """
    # Validar campo obligatorio mínimo
    if not vacante_id:
        st.error("⚠️ Debes seleccionar una vacante.")
        return

    resultado = database.insertar_aplicacion(
        vacante_id=vacante_id,
        fecha_aplicacion=fecha_aplicacion,
        estado=estado,
        nombre_recruiter=nombre_recruiter or None,
        email_recruiter=email_recruiter or None,
        telefono_recruiter=telefono_recruiter or None,
        notas=notas or None,
    )

    if resultado['success']:
        st.success(resultado['message'])
        st.balloons()
        # Limpiar formulario incrementando la key
        st.session_state.aplic_form_key += 1
        time.sleep(2)
        st.rerun()
    else:
        st.error(f"❌ {resultado['message']}")
